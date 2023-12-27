from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HistoryDoc
from .serializers import HistoryDocSerializer

# 문서 생성
class HistoryDocCreateAPI(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            serializer = HistoryDocSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                history_doc = serializer.save(author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)



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

# 특정 문서 중 가장 최신의 문서 가져오기
class DocDetailAPI(APIView):
     def get(self, request, title, format =None):
        try:
            latest_doc = HistoryDoc.objects.filter(title=title).latest('created_at')
            serializer = HistoryDocSerializer(latest_doc)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except HistoryDoc.DoesNotExist:
            return Response({
                'message': 'Document does not exist'
                }, 
                status=status.HTTP_404_NOT_FOUND)