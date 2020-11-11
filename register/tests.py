import json

from rest_framework.exceptions import ErrorDetail

from register.models import CustomUser
from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django_rest_passwordreset.models import ResetPasswordToken
from register.serializer import CustomUserSerializer, UpdateCustomUserSerializer
from django.test import Client
import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model


class CreateUserAPIViewTestCase(APITestCase):

    def test_user_create(self):
        """
        Test to verify if with validate data user can be created
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': '+48123456789'
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(201, response.status_code)

    def test_user_create_without_password(self):
        """
        Test to verify if without password user can be created
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': '',
            'password2': '',
            'telephone': ''
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(400, response.status_code)

    def test_user_create_wrong_password(self):
        """
        Test to verify if with wrong password user can be created
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test123',
            'telephone': ''
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(400, response.status_code)

    def test_user_create_without_username(self):
        """
        Test to verify if without username user can be created
        """

        user_data = {
            'username': '',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(400, response.status_code)

    def test_user_create_wrong_email(self):
        """
        Test to verify if with wrong email user can be created
        """

        user_data = {
            'username': 'testuser',
            'email': 'test',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(400, response.status_code)

    def test_user_create_wrong_telephone(self):
        """
        Test to verify if with wrong telephone user can be created
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': '123'
        }

        response = self.client.post('/users/add', user_data)
        self.assertEqual(400, response.status_code)

    def test_user_create_the_same_username(self):
        """
        Test to verify if can be created users with the same names
        """

        user_data = {
            'username': 'testuser',
            'email': 'test1@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        self.client.post('/users/add', user_data)

        user_data_2 = {
            'username': 'testuser',
            'email': 'test@test.pl',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        response = self.client.post('/users/add', user_data_2)
        self.assertEqual(400, response.status_code)


class UsersListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_superuser(
            self.username, self.email, self.password, self.telephone
        )

        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.username2 = 'notme'

    def test_get_users_list(self):
        """
        Test of list of all users in database
        """
        response = self.client.get('/users/list')
        self.assertEqual(200, response.status_code)

    def test_get_one_user(self):
        """
        Test to check if user can be called by username
        """
        response = self.client.get(f'/users/detail/{self.user.username}')
        self.assertEqual(200, response.status_code)

    def test_get_user_which_doesnt_exist(self):
        """
        Test to get user detail who isn't existing
        """
        response = self.client.get(f'/users/detail/{self.username2}')
        self.assertEqual(404, response.status_code)


class UserUpdateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.username2 = "test2"
        self.email2 = "test@gmail.com"
        self.password2 = "test"
        self.telephone2 = '+48666666666'

        self.user2 = CustomUser.objects.create_superuser(
            self.username2, self.email2, self.password2, self.telephone2
        )

        self.token2, self.created2 = Token.objects.get_or_create(user=self.user2)
        self.client2 = Client(HTTP_AUTHORIZATION='Token ' + self.token2.key)

        self.user2_id = 10

        self.valid_payload = {
            'email': 'test1@test.pl',
            'telephone': '+48123456780',
            'sms_notifications': False,
            'app_notifications': False
        }

        self.non_valid_payload = {
            'email': '',
            'telephone': '+4848123456789',
            'sms_notifications': True,
            'app_notifications': True
        }

        self.test_payload = {
            'sms_notifications' : False,
            'app_notifications' : False

        }

    def test_update(self):
        """
        Test to verify if with validated data user can be updated
        :return:
        """
        response = self.client.put(f'/users/update/{self.user.pk}', self.valid_payload)
        self.assertEqual(200, response.status_code)

    def test_failed_update(self):
        response = self.client.put(f'/users/update/{self.user.pk}', self.non_valid_payload)
        self.assertEqual(400, response.status_code)

    def test_no_user(self):
        """
        Test to verify if we can update user which doesn't exist
        """
        response = self.client2.put(f'/users/update/{self.user2_id}', self.valid_payload)
        self.assertEqual(404, response.status_code)

    def test_only_notifications(self):
        """
        Test to verify if we can update user with only notifications.
        """
        response = self.client.put(f'/users/update/{self.user.pk}', self.test_payload)
        self.assertEqual(200, response.status_code)


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

        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_logout_without_token(self):
        """
        Test to verify response if user doesn't give his token
        """
        response = self.client.post('/api-logout/ ', )
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


class DeleteUserAPIViewTestCase(APITestCase):
    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'

        self.user = CustomUser.objects.create_superuser(
            self.username, self.email, self.password, self.telephone
        )

        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.username2 = "test2"
        self.email2 = "test@gmail.com"
        self.password2 = "test"
        self.telephone2 = '+48666666666'

        self.user2 = CustomUser.objects.create_user(
            self.username2, self.email2, self.password2, self.telephone2
        )

        self.token2, self.created2 = Token.objects.get_or_create(user=self.user2)
        self.client2 = Client(HTTP_AUTHORIZATION='Token ' + self.token2.key)

    def test_delete_user_by_no_admin(self):
        """
        Test to verify if non-admin user can delete someone's account
        """
        response = self.client2.delete(f'/users/delete/{self.user.id}')
        self.assertEqual(403, response.status_code)
        self.assertTrue('detail' in json.loads(response.content))
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_delete_user_by_admin(self):
        """
        Test to verify if admin user can delete someone's account
        """
        response = self.client.delete(f'/users/delete/{self.user2.id}')
        self.assertEqual(200, response.status_code)
        self.assertEqual(CustomUser.objects.all().count(), 2)

    def test_delete_user_which_doesnt_exist(self):
        """
        Test to verify response if user doesn't exists
        """
        response = self.client.delete('/users/delete/35')
        self.assertEqual(404, response.status_code)


class TestSerializer(unittest.TestCase):
    """
    Tests written for serializer
    """
    def setUp(self):

        self.username = "TruboTest"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48606707808'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )

        self.serializer_data = {
            'username': 'Troll',
            'email': 'chernobyl@gmail.com',
            'password1': 'test',
            'password2': 'test',
            'telephone': ''
        }

        self.serializer_data_2 = {
            'username': 'Troll',
            'email': 'chernobyl2@gmail.com',
            'password1': 'test',
            'password2': 'test',
            'telephone': '+48606707808'
        }

    def test_serializer(self):

        serializer = CustomUserSerializer(data=self.serializer_data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(serializer.errors, {'email': [ErrorDetail(
            string='Email address already exists', code='invalid')]})

        serializer = CustomUserSerializer(data=self.serializer_data_2)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(serializer.errors, {'telephone': [ErrorDetail(
            string='Telephone number already exists', code='invalid')]})


class TestUpdateSerializer(unittest.TestCase):

    def setUp(self):

        self.username = "TruboTest2"
        self.email = "chernobyl3@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48606707808'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone
        )

        self.serializer_data = {
            'email': 'chernobyl4@gmail.com',
            'telephone': '+48606707808'
        }

        self.serializer_data_2 = {
            'email': 'chernobyl3@gmail.com'
        }

        self.serializer_data_3 = {
            'sms_notifications': 'true',
            'app_notifications': 'false'
        }

    def test_serializer(self):
        serializer = UpdateCustomUserSerializer(data=self.serializer_data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(serializer.errors, {'telephone': [ErrorDetail(
            string='Telephone number already exists', code='invalid')]})

        serializer = UpdateCustomUserSerializer(data=self.serializer_data_2)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(serializer.errors, {'email': [ErrorDetail(
            string='Email address already exists', code='invalid')]})

        serializer = UpdateCustomUserSerializer(data=self.serializer_data_3)
        self.assertEqual(serializer.is_valid(), True)





