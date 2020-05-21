import json

from register.models import CustomUser
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django_rest_passwordreset.models import ResetPasswordToken
from django.test import TestCase
from django.contrib.auth import get_user_model


class CreateUserAPIViewTestCase(APITestCase):

    def test_user_create(self):
        """
        Test to verify if with validate data everything is ok
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        response = self.client.post('/register/', user_data)
        self.assertEqual(201, response.status_code)

    def test_wrong_password(self):
        """
        Test of creating user with wrong password
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test123',
            'telephone': ''
        }

        response = self.client.post('/register/', user_data)
        self.assertEqual(400, response.status_code)

    def test_wrong_email(self):
        """
        Test of creating user with wrong email
        """

        user_data = {
            'username': 'testuser',
            'email': 'test',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        response = self.client.post('/register/', user_data)
        self.assertEqual(400, response.status_code)


class UserLoginAPIViewTestCase(APITestCase):
    """
    Tests for user login API
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )

    def test_authentication_without_data(self):
        """
        Test to verify response if user doesn't provide login data
        """
        response = self.client.post('/api-token-auth/')
        self.assertEqual(400, response.status_code)
        self.assertTrue('username' in json.loads(response.content))
        self.assertTrue('password' in json.loads(response.content))

    def test_authentication_without_password(self):
        """
        Test to verify if user can authenticate without password.
        """
        response = self.client.post('/api-token-auth/', {'username': self.username})
        self.assertTrue('password' in json.loads(response.content))
        self.assertFalse('username' in json.loads(response.content))
        self.assertEqual(400, response.status_code)

    def test_authentication_without_username(self):
        """
        Test to verify if user can authenticate without username.
        """
        response = self.client.post('/api-token-auth/', {'password': self.password})
        self.assertEqual(400, response.status_code)
        self.assertTrue('username' in json.loads(response.content))
        self.assertFalse('password' in json.loads(response.content))

    def test_authentication_with_incorrect_username(self):
        """
        Test to verify if user can authenticate with incorrect username.
        """
        response = self.client.post('/api-token-auth/', {'username': 'cheeki', 'password': self.password})
        self.assertEqual(400, response.status_code)
        self.assertTrue('non_field_errors' in json.loads(response.content))

    def test_authentication_with_incorrect_password(self):
        """
        Test to verify if user can authenticate with incorrect password.
        """
        response = self.client.post('/api-token-auth/', {'username': self.username, 'password': 'damke'})
        self.assertEqual(400, response.status_code)
        self.assertTrue('non_field_errors' in json.loads(response.content))

    def test_authentication_with_valid_data(self):
        """
        Test to verify if user can authenticate with correct username, password
        and check if app returns token in json format
        """
        response = self.client.post('/api-token-auth/', {'username': self.username, 'password': self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("token" in json.loads(response.content))
        self.assertEqual(Token.objects.all().count(), 1)


class UserLogoutAPIViewTestCase(APITestCase):
    """
    Tests for user logout API
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_without_token(self):
        """
        Test to verify response if user doesn't give his token
        """
        response = self.client.post('/api-logout/ ',)
        self.assertEqual(404, response.status_code)

    def test_logout_with_invalid_token(self):
        """
        Test to verify response if user gives invalid token
        """
        response = self.client.post(f'/api-logout/398292dxndsisk29292nc512123')
        self.assertEqual(404, response.status_code)

    def test_logout_with_valid_token(self):
        """
        Test to verify if user can logout with valid token and if
        token has been removed from database
        """
        response = self.client.post(f'/api-logout/{self.token}')
        self.assertEqual(200, response.status_code)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())


class UserPasswordResetAPIViewTestCase(APITestCase):
    """
    Tests for password reset via e-mail.
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )

    def test_password_reset_without_email(self):
        """
        Test to verify if user can reset password without email.
        """
        response = self.client.post('/password-reset/', {'email': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue('email' in json.loads(response.content))

    def test_password_reset_with_incorrect_email(self):
        """
        Test to verify if user can reset password with invalid email.
        """
        response = self.client.post('/password-reset/', {'email': 'email@email.com'})
        self.assertEqual(400, response.status_code)
        self.assertTrue('email' in json.loads(response.content))

    def test_password_reset_with_valid_email(self):
        """
        Test to verify if user can reset password with valid email.
        """
        response = self.client.post('/password-reset/', {'email': self.email})
        self.assertEqual(200, response.status_code)
        self.assertTrue('status' in json.loads(response.content))
        self.assertEqual(ResetPasswordToken.objects.all().count(), 1)
