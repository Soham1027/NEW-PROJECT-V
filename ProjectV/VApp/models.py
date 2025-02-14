from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.core.validators import RegexValidator


class OTPSave(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=100,blank=True,null=True)
    email=models.CharField(max_length=200,blank=True, null=True)
    OTP = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 

    class Meta:
        db_table = 'otpsave'
              

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(minutes=1)  # Set expiration time
        super().save(*args, **kwargs)


    def is_expired(self):
            return timezone.now() > self.expires_at

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
class User(AbstractBaseUser, PermissionsMixin):
    MALE = 1
    FEMALE = 2
    OTHERS = 3
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others'),
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    fullname = models.CharField(max_length=150, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)  # Set to optional
    email = models.EmailField(unique=True)  # Main identifier
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)  # Changed from CharField to IntegerField
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)  # Changed from CharField
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=150, null=True, blank=True)

    # Authentication & Device Fields
    otp = models.CharField(max_length=6, null=True, blank=True)
    device_type = models.CharField(max_length=255, null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    register_type = models.CharField(max_length=10, null=True, blank=True)
    remember_token = models.CharField(max_length=255, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Permissions & Activity
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Soft delete field
    is_deleted = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # No need for username, only email is required

    def __str__(self):
        return self.email  # You can display email instead of username

    class Meta:
        db_table = 'app_user'


class PaymentCard(models.Model):
    card_number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\d{16}$', 'Card number must be 16 digits.')],
        blank=False,
    )
    card_holder_name = models.CharField(max_length=100)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'app_payment_card'


