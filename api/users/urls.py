from django.urls import path
from .views import RegisterView, LoginView, GetUserDetail, LogoutView, UserProfile
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
)

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("", GetUserDetail.as_view()),
    #path("logout", LogoutView.as_view()),
    path("<uuid:pk>/", UserProfile.as_view()),
    path("logout/", TokenBlacklistView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
