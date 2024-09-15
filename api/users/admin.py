from django.contrib import admin

# Register your models here.
from .models import User, ProfilePic, CoverPhoto

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')

class ProfilePicsAdmin(admin.ModelAdmin):
    list_display = ['user', "image"]

class CoverPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']

admin.site.register(User, UserAdmin)
admin.site.register(ProfilePic, ProfilePicsAdmin)
admin.site.register(CoverPhoto, CoverPhotoAdmin)