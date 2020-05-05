from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=9, unique=True)
    sms_notifications = models.BooleanField(default=True)
    app_notifications = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'telephone']

    objects = CustomUserManager()

    def _str_(self):
        return self.username

