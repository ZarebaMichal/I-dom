from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    telephone = PhoneNumberField()
    sms_notifications = models.BooleanField(default=True)
    app_notifications = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def _str_(self):
        return self.username

