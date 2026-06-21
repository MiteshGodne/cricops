from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import uuid

'''Override the default functions to customize the Manager which handles the creation of users by communicating with the db'''
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required !!")
        if not password:
            raise ValueError("Password is required !!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not email:
            raise ValueError("Email is required !!")
        if not password:
            raise ValueError("Superuser must have a password !!")
        return self.create_user(email, password, **extra_fields)
    
class UserRole(models.TextChoices):
    ORGANIZER = 'ORGANIZER', 'Organizer'
    TEAMHEAD = 'TEAMHEAD', 'TeamHead'
    UMPIRE = 'UMPIRE', 'Umpire'
    VIEWER = 'VIEWER', 'Viewer'

class User(AbstractUser):
    username = None
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.VIEWER)
    avatar_url = models.ImageField(upload_to='avatars/', blank=True, null=True)    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return f"{self.email} ({self.role})"