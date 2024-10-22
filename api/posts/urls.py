from django.urls import path
from .views import (
    PostCreateView,
    PostListView,
    PostView,
    PostReactionCreateView,
    PostCommentListCreateView,
    SearchView,
    TrendingHashtagsView,
    SuggestedUsersView,
)

urlpatterns = [
    path("create", PostCreateView.as_view(), name="create-post"),
    path("", PostListView.as_view(), name="list-posts"),
    path("<uuid:post_id>/", PostView.as_view(), name="post-detail"),
    path(
        "<uuid:post_id>/comment/",
        PostCommentListCreateView.as_view(),
        name="post-comment",
    ),
    path(
        "<uuid:post_id>/react/<str:reaction_type>/",
        PostReactionCreateView.as_view(),
        name="post_reaction",
    ),
    path("search", SearchView.as_view(), name="search"),
    path(
        "hashtags/trending/", TrendingHashtagsView.as_view(), name="trending_hashtags"
    ),
    path("users/suggested/", SuggestedUsersView.as_view(), name="suggested_users"),
]
