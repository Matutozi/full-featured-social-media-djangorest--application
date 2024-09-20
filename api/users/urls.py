from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    RegisterView,
    LoginView,
    GetUserDetail,
    LogoutView,
    UserProfile,
    ProfilePicsCreation,
)
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
)

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("", GetUserDetail.as_view()),
    path("<uuid:pk>/", UserProfile.as_view()),
    path("logout/", TokenBlacklistView.as_view()),
    path("profile-pic/", ProfilePicsCreation.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
