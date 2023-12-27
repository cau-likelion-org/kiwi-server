from django.urls import path
from .views import *

urlpatterns = [
    path('recent/', RecentEditedDocumentsAPI.as_view(), name='최근 편집된 전체 문서 목록'),
    path('<str:title>/', DocumentEditHistoryAPI.as_view(), name='특정 문서의 전체 편집 목록'),    
]