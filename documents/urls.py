from django.urls import path
from .views import *

urlpatterns = [
    path('', HistoryDocCreateAPI.as_view(), name = '문서 작성'),
    path('recent/<str:title>/', DocDetailAPI.as_view(), name = '특정 문서 중 가장 최근 편집된 글 가져오기'),
    path('recent/', RecentEditedDocumentsAPI.as_view(), name='최근 편집된 전체 문서 목록'),
    path('<str:title>/', DocumentEditHistoryAPI.as_view(), name='특정 문서의 전체 편집 목록'),
        
]