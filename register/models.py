from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager


class CustomUser(AbstractUser):

    LANGUAGES = [
        ('pl', 'pl'),
        ('eng', 'eng'),
    ]

    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    telephone = PhoneNumberField(blank=True, null=True)
    sms_notifications = models.BooleanField(default=False)
    app_notifications = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=10, choices=LANGUAGES)

    REQUIRED_FIELDS = ['email', 'telephone', 'language']

    objects = CustomUserManager()

    def _str_(self):
        return self.username
