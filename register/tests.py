import json

from register.models import CustomUser
from django.urls import reverse

from rest_framework.test import APITestCase

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
