from django.contrib import admin

# Register your models here.
from .models import User

class UserAdmin(admin.ModelAdmin):
    fields = ["email", "username"]
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')



admin.site.register(User, UserAdmin)
