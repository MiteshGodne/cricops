from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import uuid

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
    PENDING = 'PENDING', 'Pending'
    ORGANIZER = 'ORGANIZER', 'Organizer'
    TEAMHEAD = 'TEAMHEAD', 'TeamHead'
    UMPIRE = 'UMPIRE', 'Umpire'
    REJECTED = 'REJECTED', 'Rejected'

class ApplyFor(models.TextChoices):
    ORGANIZER = 'ORGANIZER', 'Organizer'
    TEAMHEAD = 'TEAMHEAD', 'TeamHead'
    UMPIRE = 'UMPIRE', 'Umpire'

class User(AbstractUser):
    username = None
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    apply_for = models.CharField(max_length=20, choices=ApplyFor.choices)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    middle_name = models.CharField(max_length=15, blank=True, null=True)
    avatar_url = models.ImageField(upload_to='avatars/', blank=True, null=True)    
    
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PENDING)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        constraints = [
            models.CheckConstraint(condition=models.Q(role__in=['PENDING','ORGANIZER','TEAMHEAD','UMPIRE','REJECTED']), name='valid_user_role')
        ]
        
    def __str__(self):
        return f"{self.email} ({self.role})"