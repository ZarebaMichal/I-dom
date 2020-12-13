from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager
    """
    def create_user(self, username, email, password, telephone, language,  **extra_fields):
        """
        Create and save a User with the given username, email, telephone number and password.
        """
        if not username:
            raise ValueError(_('The username must be set'))
        if not email:
            raise ValueError(_('The email must be set'))
        if not password:
            raise ValueError(_('The password must be set!'))
        if not language:
            raise ValueError(_('The language must be set!'))

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            telephone=telephone,
            language=language,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, telephone, language, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('sms_notifications', True)
        extra_fields.setdefault('app_notifications', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        return self.create_user(username, email, password, telephone, language, **extra_fields)