from django.contrib import admin

from .models import Post, PostComment, PostReaction, Hashtag


# Register your models here.
class PostsAdmin(admin.ModelAdmin):
    list_display = ["user", "updated_at"]
    search_fields = ["user"]


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ["post", "updated_at"]


admin.site.register(Post, PostsAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostReaction)
admin.site.register(Hashtag)
