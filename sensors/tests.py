import json

from register.models import CustomUser
from sensors.models import Sensors
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.test import Client


class AddSensorAPIViewTestCase(APITestCase):
    """
    Tests for adding new sensor
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
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

    def test_add_sensor_with_valid_data_category_temp(self):
        response = self.client.post('/sensors/add/', {'name': 'temperatura_pokoj', 'category': 'temperature'})
        self.assertEqual(201, response.status_code)
        self.assertTrue(Sensors.objects.filter(name='temperatura_pokoj').exists())
        self.assertEqual(Sensors.objects.all().count(), 2)

    def test_add_sensor_with_valid_data_category_hum(self):
        response = self.client.post('/sensors/add/', {'name': 'wilg_pokoj', 'category': 'humidity'})
        self.assertEqual(201, response.status_code)
        self.assertTrue(Sensors.objects.filter(name='wilg_pokoj').exists())
        self.assertEqual(Sensors.objects.all().count(), 2)

    def test_add_sensor_with_name_already_exists(self):
        response = self.client.post('/sensors/add/', {'name': self.name, 'category': self.category})
        self.assertEqual(409, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_name(self):
        response = self.client.post('/sensors/add/', {'name': '', 'category': self.category})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_category(self):
        response = self.client.post('/sensors/add/', {'name': 'test', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_anything(self):
        response = self.client.post('/sensors/add/', {'name': '', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_with_invalid_category(self):
        response = self.client.post('/sensors/add/', {'name': 'testowanko', 'category': 'x'})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)
