from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UserProfile
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("", UserView.as_view()),
    path("logout", LogoutView.as_view()),
    path("<int:pk>/", UserProfile.as_view(), name="user-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
