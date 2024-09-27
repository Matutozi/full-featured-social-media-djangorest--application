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
    CoverPhotoCreation,
    FollowViewSet,
)
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    # path("user_detail", GetUserDetail.as_view(), name="get_user_details"),
    path("<uuid:pk>/", UserProfile.as_view(), name="user_profile"),
    path("logout/", LogoutView.as_view()),
    path("profile-pic/", ProfilePicsCreation.as_view()),
    path("coverphoto/", CoverPhotoCreation.as_view()),
    path("follow/<int:user_id>/", FollowViewSet.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
