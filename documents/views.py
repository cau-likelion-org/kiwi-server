from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HistoryDoc
from .serializers import HistoryDocSerializer

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
