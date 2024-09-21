from django.urls import path
from .views import PostCreateView, PostListView, PostView

urlpatterns = [
    path("create/", PostCreateView.as_view(), name="create-post"),
    path("", PostListView.as_view(), name="list-posts"),
     path('<uuid:post_id>/', PostView.as_view(), name='post-detail')
]
