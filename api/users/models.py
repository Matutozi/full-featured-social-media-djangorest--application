from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


class UserManager(BaseUserManager):
    
    def create_user(self, email, username, password=None):
        if not email:
            return ValueError("The Email Field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    """Model that contains all the info about a user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=40, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField()
    role = models.CharField(max_length=40)
    bio = models.TextField(null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDs = ["username"]

    object = UserManager()


    def __str__(self):
        return self.username
    

