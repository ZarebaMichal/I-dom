import json

from register.models import CustomUser
from sensors.models import Sensors, SensorsData
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.test import Client
from rest_framework.test import APIClient


class AddSensorAPIViewTestCase(APITestCase):
    """
    Tests for adding new sensor
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'
        self.frequency = 9999999999

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

    def test_add_sensor_with_valid_data_category_temp(self):
        response = self.client.post('/sensors/add', {'name': 'temperatura_pokoj', 'category': 'temperature', 'frequency': '3500'})
        self.assertEqual(201, response.status_code)
        self.assertTrue(Sensors.objects.filter(name='temperatura_pokoj').exists())
        self.assertEqual(Sensors.objects.all().count(), 2)

    def test_add_sensor_with_valid_data_category_hum(self):
        response = self.client.post('/sensors/add', {'name': 'wilg_pokoj', 'category': 'humidity', 'frequency': '3000'})
        self.assertEqual(201, response.status_code)
        self.assertTrue(Sensors.objects.filter(name='wilg_pokoj').exists())
        self.assertEqual(Sensors.objects.all().count(), 2)

    def test_add_sensor_with_name_already_exists(self):
        response = self.client.post('/sensors/add', {'name': self.name, 'category': self.category})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_name(self):
        response = self.client.post('/sensors/add', {'name': '', 'category': self.category})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_category(self):
        response = self.client.post('/sensors/add', {'name': 'test', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_without_anything(self):
        response = self.client.post('/sensors/add', {'name': '', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_with_invalid_category(self):
        response = self.client.post('/sensors/add', {'name': 'testowanko', 'category': 'x', 'frequency': '333333'})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)

    def test_add_sensor_with_invalid_frequency(self):
        response = self.client.post('/sensors/add', {'name': 'testujemy', 'category': 'temperature',
                                                                                      'frequency': self.frequency})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)


class GetListOfSensorsAPIViewTestCase(APITestCase):
    """
    Tests for getting list of sensors
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.id = 5
        self.sensor_data = '29.00'

        self.data = SensorsData.objects.create(sensor=Sensors.objects.get(name=self.name, category=self.category),
                                               sensor_data=self.sensor_data)

    def test_get_list_of_sensors(self):
        response = self.client.get('/sensors/list')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Sensors.objects.all().count(), 1)

    def test_get_single_sensor(self):
        response = self.client.get(f'/sensors/detail/{self.sensor.id}')
        self.assertEqual(200, response.status_code)

    def test_single_not_existing_detail_of_sensor(self):
        response = self.client.get(f'/sensors/detail/{self.id}')
        self.assertEqual(404, response.status_code)


class DeleteSensorAPIViewTestCase(APITestCase):
    """
    Tests for deleting new sensor
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.id = 5

    def test_delete_sensor(self):
        response = self.client.delete(f'/sensors/delete/{self.sensor.id}')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Sensors.objects.all().count(), 1)

    def test_delete_not_existing_sensor(self):
        response = self.client.delete(f'/sensors/delete/{self.id}')
        self.assertEqual(404, response.status_code)


class UpdateSensorAPIViewTestCase(APITestCase):
    """
    Tests for updating new sensor
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)
        pk = int(self.sensor.pk)

        self.id = 4

        self.validated_payload = {
            'name': 'salon',
            'category': 'temperature'
        }

        self.non_validated_payload = {
            'name': '',
            'category': 'blabla'
        }

    def test_update_sensor(self):
        response = self.client.put(f'/sensors/update/{self.sensor.pk}', self.validated_payload)
        self.assertEqual(200, response.status_code)

    def test_fail_update_sensor(self):
        response = self.client.put(f'/sensors/update/{self.sensor.pk}', self.non_validated_payload)
        self.assertEqual(400, response.status_code)

    def test_fail_no_sensor_update(self):
        response = self.client.put(f'/sensors/update/{self.id}', self.validated_payload)
        self.assertEqual(404, response.status_code)


class ListSensorsDataAPIViewTestCase(APITestCase):
    """
    Tests for updating new sensor
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor_data = '324324'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.data = SensorsData.objects.create(sensor=Sensors.objects.get(name=self.name, category=self.category),
                                               sensor_data=self.sensor_data)

    def test_list_all_data_from_sensor_data(self):
        response = self.client.get('/sensors_data/list')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, SensorsData.objects.all().count())


class AddSensorDataAPIViewTestCase(APITestCase):
    """
    Tests to verify if adding new data to database works properly
    """

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

    def test_add_new_data(self):
        data = {
            'sensor': self.sensor.name,
            'sensor_data': '3789'
        }
        response = self.client.post('/sensors_data/add', data)
        self.assertEqual(201, response.status_code)

    def test_add_new_data_without_name(self):
        data = {
            'sensor': '',
            'sensor_data': '3789'
        }
        response = self.client.post('/sensors_data/add', data)
        self.assertEqual(404, response.status_code)

    def test_add_new_data_with_non_validated_data(self):
        data = {
            'sensor': self.sensor.name,
            'sensor_data': 123456789012345678901234567890
        }
        response = self.client.post('/sensors_data/add', data)
        self.assertEqual(400, response.status_code)


class GetLastDataAPIViewTestCase(APITestCase):

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor_data = '324324'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.data = SensorsData.objects.create(sensor=Sensors.objects.get(name=self.name, category=self.category),
                                               sensor_data=self.sensor_data)

        self.id = 3

    def test_get_sensor_data_not_exists(self):
        response = self.client.get(f'/sensors_data/latest_value/{self.id}')
        self.assertEqual(404, response.status_code)

    def test_get_sensor_data(self):
        response = self.client.get(f'/sensors_data/latest_value/{self.sensor.id}')
        self.assertEqual(200, response.status_code)


class ChangeFrequencyAPITestCase(APITestCase):

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor_data = '324324'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.data = SensorsData.objects.create(sensor=Sensors.objects.get(name=self.name, category=self.category),
                                               sensor_data=self.sensor_data)

        self.id = 3

    def test_change_frequency_sensor_doesnt_exist(self):
        response = self.client.post(f'/sensors_data/frequency/{self.id}')
        self.assertEqual(404, response.status_code)

class AddIpAddressAPITestCase(APITestCase):

    def setUp(self):
        self.username = "CheekiBreeki"
        self.email = "chernobyl@gmail.com"
        self.password = "ivdamke"
        self.telephone = '+48999111000'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language
        )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'piwnica'
        self.category = 'temperature'

        self.sensor_data = '324324'

        self.sensor = Sensors.objects.create(name=self.name, category=self.category)

        self.data = SensorsData.objects.create(sensor=Sensors.objects.get(name=self.name, category=self.category),
                                               sensor_data=self.sensor_data)


        self.invalid_ip = {
            'name': self.name,
            'ip_address': '11112222'
        }

        self.wrong_sensor = {
            'name': 'nie_ma_takiego_sensora',
            'ip_address': '192.168.1.7'
        }

        self.correct_data = {
            'name': self.name,
            'ip_address': '192.168.1.7'
        }

    def test_add_invalid_ip(self):
        response = self.client.post('/sensors/ip', self.invalid_ip)
        self.assertEqual(400, response.status_code)

    def test_add_not_existing_sensor(self):
        response = self.client.post('/sensors/ip', self.wrong_sensor)
        self.assertEqual(404, response.status_code)

    def test_add_valid_ip_and_sensor(self):
        response = self.client.post('/sensors/ip', self.correct_data)
        self.assertEqual(200, response.status_code)