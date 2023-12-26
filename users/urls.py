from django.contrib import admin
from django.urls import path
from .views import google_callback, RegisterView, CheckNameView

urlpatterns = [
    # path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('check-name/', CheckNameView.as_view(), name='check_name'),
]
