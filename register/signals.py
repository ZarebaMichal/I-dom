"""
Signals file for listening signal to create token, reset password
and sending email to user with url and token using smtp configured
in settings.py
"""


from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_url': "{}{}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    }

    send_mail(
        # subject:
        'Password Reset for {title}'.format(title='I-DOM'),
        # message:
        'Dear {username}, owner of the {email} account,'
        ' here is your password reset url: {reset_password_url}'.format(
                                                                        username=context['username'],
                                                                        email=context['email'],
                                                                        reset_password_url=context['reset_url']
                                                                        ),
        # from:
        'i.dom.industry@gmail.com',
        # to :
        [reset_password_token.user.email],
        fail_silently=False,
    )
