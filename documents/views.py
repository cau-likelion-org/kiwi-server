from django.shortcuts import render
from django.db.models import Max
from django.db.models import Q
from random import choice
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HistoryDoc, CurrDoc, Generation
from .serializers import HistoryDocSerializer

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
                serializer.errors, 
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
        if not HistoryDoc.objects.filter(title=title).exists():
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        docs = HistoryDoc.objects.filter(title=title).order_by('-updated_at')
        serializer = HistoryDocSerializer(docs, many=True)
        return Response({
            "status": "200",
            "message": "success",
            "data": serializer.data
        })

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

class SearchHistoryDocAPI(APIView):
    def get(self, request,keyword):
        queryset = HistoryDoc.objects.filter(Q(title__icontains = keyword) | Q(content__icontains = keyword), curr_docs__isnull=False)\
        .order_by('-created_at')[:3]

        if queryset.exists():
            serializer = HistoryDocSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({
                "message" : "No documents found"},
                status=status.HTTP_404_NOT_FOUND
            )