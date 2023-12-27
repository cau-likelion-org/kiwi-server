from django.urls import path
from .views import *

urlpatterns = [
    path('', DocsPost.as_view()),
    path('<str:title>/', DocDetail.as_view()),
]