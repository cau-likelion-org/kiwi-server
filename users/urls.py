from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    # path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('check-name/', CheckNameView.as_view(), name='check_name'),
    path('rand-name/', RandomNameView.as_view(), name='random_name'),

    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
