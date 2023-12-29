from django.urls import path
from .views import *

urlpatterns = [
    path('', HistoryDocCreateAPI.as_view(), name = '문서 작성'),
    path('recent/<str:title>/', DocDetailAPI.as_view(), name = '특정 문서 중 가장 최근 편집된 글 가져오기'),
    path('random/', RandomDocAPI.as_view(), name = '임의 문서 가져오기'),    
    path('<str:generation>/', GenerationFilteredDocAPI.as_view(), name = '기수로 분류된 문서 전체 조회'),
    path('search/<str:keyword>/', SearchHistoryDocAPI.as_view(), name="문서 검색"),
    path('backlink/<str:title>/', BackLinkAPI.as_view(), name='역링크 조회'),
    path('image/',ImageUploadView.as_view(), name='이미지 업로드' ),

    path('recent/', RecentEditedDocumentsAPI.as_view(), name='최근 편집된 전체 문서 목록'),
    path('<str:title>/', DocumentEditHistoryAPI.as_view(), name='특정 문서의 전체 편집 목록'),
    path('<str:title>/detail/', DocumentEditComparisonAPI.as_view(), name='특정 문서의 편집 변경 사항'), 
]