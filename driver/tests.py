from driver.models import Drivers
from register.models import CustomUser
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.test import Client
from rest_framework.test import APIClient


class AddDriverAPIViewTestCase(APITestCase):
    """
    Tests for adding new driver
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

        self.name = 'Pilot'
        self.category = 'remote_control'
        self.driver = Drivers.objects.create(name=self.name, category=self.category, data=False)

        self.category1 = 'clicker'
        self.category2 = 'roller_blind'

    def test_add_driver_with_valid_data(self):
        response = self.client.post('/drivers/add', {'name': 'Klikacz', 'category': self.category1, 'data': False})
        self.assertEqual(201, response.status_code)
        self.assertTrue(Drivers.objects.filter(name='Klikacz').exists())
        self.assertEqual(Drivers.objects.all().count(), 2)

    def test_add_drivers_with_name_already_exists(self):
        response = self.client.post('/drivers/add', {'name': self.name, 'category': self.category, 'data': False})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Drivers.objects.all().count(), 1)

    def test_add_driver_without_name(self):
        response = self.client.post('/drivers/add', {'name': '', 'category': self.category})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Drivers.objects.all().count(), 1)

    def test_add_driver_without_category(self):
        response = self.client.post('/drivers/add', {'name': 'test', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Drivers.objects.all().count(), 1)

    def test_add_driver_without_anything(self):
        response = self.client.post('/drivers/add', {'name': '', 'category': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Drivers.objects.all().count(), 1)

    def test_add_driver_with_invalid_category(self):
        response = self.client.post('/drivers/add', {'name': 'testowanko', 'category': 'x'})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Drivers.objects.all().count(), 1)


class GetListOfDriversAPIViewTestCase(APITestCase):
    """
    Tests for getting list of drivers
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

        self.name = 'Pilot'
        self.category = 'remote_control'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)

        self.id = 5


    def test_get_list_of_drivers(self):
        response = self.client.get('/drivers/list')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Drivers.objects.all().count(), 1)

    def test_get_single_driver(self):
        response = self.client.get(f'/drivers/detail/{self.driver.id}')
        self.assertEqual(200, response.status_code)

    def test_single_not_existing_detail_of_driver(self):
        response = self.client.get(f'/drivers/detail/{self.id}')
        self.assertEqual(404, response.status_code)


class DeleteDriverAPIViewTestCase(APITestCase):
    """
    Tests for deleting new Driver
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

        self.name = 'Pilot'
        self.category = 'remote_control'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)

        self.id = 200

    def test_delete_driver(self):
        response = self.client.delete(f'/drivers/delete/{self.driver.id}')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Drivers.objects.all().count(), 1)

    def test_delete_not_existing_driver(self):
        response = self.client.delete(f'/drivers/delete/{self.id}')
        self.assertEqual(404, response.status_code)


class UpdateDriverAPIViewTestCase(APITestCase):
    """
    Tests for updating new driver
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

        self.name = 'Pilot'
        self.category = 'remote_control'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)

        self.id = 200

        self.validated_payload = {
            'name': 'Klikacz',
            'category': 'clicker'
        }

        self.non_validated_payload = {
            'name': '',
            'category': 'blabla'
        }

    def test_update_drivers(self):
        response = self.client.put(f'/drivers/update/{self.driver.pk}', self.validated_payload)
        self.assertEqual(200, response.status_code)

    def test_fail_update_drivers(self):
        response = self.client.put(f'/drivers/update/{self.driver.pk}', self.non_validated_payload)
        self.assertEqual(400, response.status_code)

    def test_fail_no_drivers_update(self):
        response = self.client.put(f'/drivers/update/{self.id}', self.validated_payload)
        self.assertEqual(404, response.status_code)


class AddIpAddressAPITestCase(APITestCase):

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

        self.name = 'Pilot'
        self.category = 'remote_control'
        self.driver = Drivers.objects.create(name=self.name, category=self.category, data=False)

        self.invalid_ip = {
            'name': self.name,
            'ip_address': '11112222'
        }

        self.wrong_driver = {
            'name': 'nie_ma_takiego_sterownika',
            'ip_address': '192.168.1.7'
        }

        self.correct_data = {
            'name': self.name,
            'ip_address': '192.168.1.7'
        }

    def test_add_invalid_ip(self):
        response = self.client.post('/drivers/ip', self.invalid_ip)
        self.assertEqual(400, response.status_code)

    def test_add_not_existing_driver(self):
        response = self.client.post('/drivers/ip', self.wrong_driver)
        self.assertEqual(404, response.status_code)

    def test_add_valid_ip_and_driver(self):
        response = self.client.post('/drivers/ip', self.correct_data)
        self.assertEqual(200, response.status_code)
