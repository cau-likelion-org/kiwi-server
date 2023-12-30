from django.shortcuts import render
from django.db.models import Max
from django.db.models import Q
from random import choice
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HistoryDoc, CurrDoc, Generation, BackLink
from .serializers import HistoryDocSerializer, ImageUploadSerializer
from .service import *

# 문서 생성
class HistoryDocCreateAPI(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            serializer = HistoryDocSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                history_doc = serializer.save(author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({
                "message": "Failed to create Doc"},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'message': '로그인이 필요합니다.'}, 
                status=status.HTTP_401_UNAUTHORIZED)


# 최근 편집된 전체 문서 목록
class RecentEditedDocumentsAPI(APIView):
    def get(self, request):
        try:
            recent_docs = HistoryDoc.objects.order_by('-updated_at')[:5]
            serializer = HistoryDocSerializer(recent_docs, many=True)
            return Response({
                "status": "200",
                "message": "success",
                "data": serializer.data
            })
        except Exception as e:
            return Response({"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

# 특정 문서의 전체 편집 목록
class DocumentEditHistoryAPI(APIView):
    def get(self, request, title):
        docs = HistoryDoc.objects.filter(title=title).order_by('-updated_at')

        if not docs.exists():
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            data = []
            for i in range(len(docs) - 1):
                serializer_current = HistoryDocSerializer(docs[i])
                serializer_previous = HistoryDocSerializer(docs[i + 1])

                comparison = diff_strings(serializer_previous.data['content'], serializer_current.data['content'])
                
                doc_data = serializer_current.data
                doc_data['change'] = comparison
                data.append(doc_data)

            if docs:
                data.append(HistoryDocSerializer(docs.last()).data)

            return Response({
                "status": "200",
                "message": "success",
                "data": data
            })
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 특정 문서 중 가장 최신의 문서 가져오기(CurrDoc 활용)
class DocDetailAPI(APIView):
     def get(self, request, title, format=None):
        try:
            curr_doc = CurrDoc.objects.get(history_doc__title=title)
            serializer = HistoryDocSerializer(curr_doc.history_doc)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CurrDoc.DoesNotExist:
            return Response({
                'message': 'Document with the given title does not exist'}, 
                status=status.HTTP_404_NOT_FOUND)
         

# 임의 문서 가져오기
class RandomDocAPI(APIView):
    def get(self, request, format=None):
        curr_docs = CurrDoc.objects.all()
        if curr_docs.exists():
            # 랜덤한 CurrDoc 선택
            random_doc = choice(list(curr_docs))
            serializer = HistoryDocSerializer(random_doc.history_doc)
            return Response(serializer.data) 
        else:
            return Response({
                "message": "No documents found"}, 
                status=status.HTTP_404_NOT_FOUND)

# generation으로 분류된 문서 전체 조회
class GenerationFilteredDocAPI(APIView):
    def get(self, request, generation=None):
        if generation is not None:
            queryset = HistoryDoc.objects.filter(generations__generation=generation)\
                                         .annotate(max_id=Max('id'))\
                                         .filter(id=Max('id'))\
                                         .filter(curr_docs__isnull=False)
        else:
            queryset = HistoryDoc.objects.all()
        serializer = HistoryDocSerializer(queryset, many=True)

        if queryset.exists():  
            serializer = HistoryDocSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({
                "message": "No documents found"}, 
                status=status.HTTP_404_NOT_FOUND)

#문서 검색
class SearchHistoryDocAPI(APIView):
    def get(self, request,keyword):
        queryset = HistoryDoc.objects.filter(Q(title__iexact = keyword) | Q(content__icontains = keyword), curr_docs__isnull=False)\
        .order_by('-created_at')[:3]

        if queryset.exists():
            serializer = HistoryDocSerializer(queryset, many=True, context={'keyword': keyword})
            return Response(serializer.data)
        else:
            return Response({
                "message" : "No documents found"},
                status=status.HTTP_404_NOT_FOUND
            )

# 특정 문서의 편집 변경 사항
class DocumentEditComparisonAPI(APIView):
    def get(self, request, title):
        docs = HistoryDoc.objects.filter(title=title).order_by('-updated_at')

        if not docs.exists():
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            for i in range(len(docs) - 1):
                old_doc = docs[i + 1].content
                new_doc = docs[i].content
                comparison = diff_strings(old_doc, new_doc)
                serializer = HistoryDocSerializer(docs[i])
                data = serializer.data
                data['change'] = comparison

            return Response({
                "status": "200",
                "message": "success",
                "data": data
            })

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#역링크
class BackLinkAPI(APIView):
    def get(self, request, title):
        print("Title received: ", title)
        currdocs = CurrDoc.objects.exclude(title=title)
        backlinks_created = []

        for currdoc in currdocs:
            historydoc = currdoc.history_doc
            #if 'http://127.0.0.1:8000/docs/recent/{}'.format(title) in historydoc.content:
            if 'http://localhost:3000/viewer?title={}'.format(title) in historydoc.content:
                referenced_currdoc = CurrDoc.objects.filter(title=title).first()
                if referenced_currdoc:
                    BackLink.objects.create(src=currdoc, dst=referenced_currdoc)
                    backlinks_created.append(currdoc.title)
                else:
                    print("CurrDoc with title {} does not exist.".format(title))
            else:
                print("backlink not found in historydoc content.")
        
        return Response({"message": "Backlink creation process completed.", "backlinks_created_for": backlinks_created})


#이미지 반환
class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            url = serializer.save()
            return Response(url, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
