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


class BulbDriverIPAPIViewTestCase(APITestCase):
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

        self.name = 'Zarowka'
        self.category = 'bulb'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)
        self.name2 = 'pilot'
        self.category2 = 'pilot'
        self.driver2 = Drivers.objects.create(name=self.name2, category=self.category2)


        self.ip_correct = {
            'ip_address': '192.168.18.32'
        }
        self.ip_incorrect = {
            'ip_address': '192.168.1.7'
        }

    def test_add_not_exisiting_bulb_ip(self):
        response = self.client.post('/bulbs/ip/100', self.ip_incorrect)
        self.assertEqual(404, response.status_code)

    def test_add_existing_bulb_ip(self):
        response = self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        self.assertEqual(200, response.status_code)

    def test_add_turned_of_bulb_ip(self):
        response = self.client.post(f'/bulbs/ip/{self.driver2.id}', self.ip_incorrect)
        self.assertEqual(503, response.status_code)

    def test_add_invalid_ip(self):
        response = self.client.post(f'/bulbs/ip/{self.driver.id}', 'tiruru')
        self.assertEqual(400, response.status_code)


class BulbDriverTurnAPIViewTestCase(APITestCase):
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

        self.name = 'Zarowka'
        self.category = 'bulb'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)
        self.name2 = 'pilot'
        self.category2 = 'pilot'
        self.driver2 = Drivers.objects.create(name=self.name2, category=self.category2)

        self.ip_correct = {
            'ip_address': '192.168.18.32'
        }
        self.ip_incorrect = {
            'ip_address': '192.168.1.7'
        }

        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_incorrect)

        self.request_on = {
            'flag': 'on'
        }

        self.request_off = {
            'flag': 'off'
        }

        self.request_invalid_value = {
            'flag': 'xDD'
        }

        self.request_invalid_key = {
            'dadsa': 'on'
        }


    def test_turn_turn_on_not_exisiting_bulb(self):
        response = self.client.post(f'/bulbs/switch/300', self.request_on)
        self.assertEqual(404, response.status_code)

    def test_turn_on_category_not_bulb(self):
        response = self.client.post(f'/bulbs/switch/{self.driver2.id}', self.request_on)
        self.assertEqual(400, response.status_code)

    def test_turn_on_bulb_out_of_power(self):
        response = self.client.post(f'/bulbs/switch/{self.driver.id}', self.request_on)
        self.assertEqual(503, response.status_code)

    def test_turn_invalid_value(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/switch/{self.driver.id}', self.request_invalid_value)
        self.assertEqual(400, response.status_code)

    def test_turn_invalid_key(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/switch/{self.driver.id}', self.request_invalid_key)
        self.assertEqual(400, response.status_code)

    def test_ok_on(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/switch/{self.driver.id}', self.request_on)
        self.assertEqual(200, response.status_code)

    def test_ok_off(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/switch/{self.driver.id}', self.request_off)
        self.assertEqual(200, response.status_code)


class BulbDriverColorAPIViewTestCase(APITestCase):
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

        self.name = 'Zarowka'
        self.category = 'bulb'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)
        self.name2 = 'pilot'
        self.category2 = 'pilot'
        self.driver2 = Drivers.objects.create(name=self.name2, category=self.category2)

        self.ip_correct = {
            'ip_address': '192.168.18.32'
        }
        self.ip_incorrect = {
            'ip_address': '192.168.1.7'
        }

        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_incorrect)

        self.request_valid = {
            'red': 255,
            'green': 0,
            'blue': 0
        }

        self.request_invalid_colors = {
            'red': -300,
            'green': 0,
            'blue': 0
        }

        self.request_invalid_keys = {
            'sdada': 30,
            'sadad': 155,
            'sadadad': 0
        }


    def test_not_existing_bulb(self):
        response = self.client.post('/bulbs/color/100', self.request_valid)
        self.assertEqual(404, response.status_code)

    def test_wrong_cat(self):
        response = self.client.post(f'/bulbs/color/{self.driver2.id}', self.request_valid)
        self.assertEqual(400, response.status_code)

    def test_bulb_offline(self):
        response = self.client.post(f'/bulbs/color/{self.driver.id}', self.request_valid)
        self.assertEqual(503, response.status_code)

    def test_invalid_values(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/color/{self.driver.id}', self.request_invalid_colors)
        self.assertEqual(400, response.status_code)

    def test_invalid_keys(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/color/{self.driver.id}', self.request_invalid_keys)
        self.assertEqual(400, response.status_code)

    def test_ok(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/color/{self.driver.id}', self.request_valid)
        self.assertEqual(200, response.status_code)


class BulbDriverBrightnessAPIViewTestCase(APITestCase):
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

        self.name = 'Zarowka'
        self.category = 'bulb'
        self.driver = Drivers.objects.create(name=self.name, category=self.category)
        self.name2 = 'pilot'
        self.category2 = 'pilot'
        self.driver2 = Drivers.objects.create(name=self.name2, category=self.category2)

        self.ip_correct = {
            'ip_address': '192.168.18.32'
        }
        self.ip_incorrect = {
            'ip_address': '192.168.1.7'
        }

        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_incorrect)

        self.request_valid = {
            'brightness': 65
        }

        self.request_invalid_key = {
            'bsdaa': 15
        }

        self.request_invalid_value = {
            'brightness': 150
        }

    def test_not_existing_bulb(self):
        response = self.client.post(f'/bulbs/brightness/100', self.request_valid)
        self.assertEqual(404, response.status_code)

    def test_wrong_category_bulb(self):
        response = self.client.post(f'/bulbs/brightness/{self.driver2.id}', self.request_valid)
        self.assertEqual(400, response.status_code)

    def test_off_poweeer_bulb(self):
        response = self.client.post(f'/bulbs/brightness/{self.driver.id}', self.request_valid)
        self.assertEqual(503, response.status_code)

    def test_invalid_value(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/brightness/{self.driver.id}', self.request_invalid_value)
        self.assertEqual(400, response.status_code)

    def test_invalid_key(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/brightness/{self.driver.id}', self.request_invalid_key)
        self.assertEqual(400, response.status_code)

    def test_correct(self):
        self.client.post(f'/bulbs/ip/{self.driver.id}', self.ip_correct)
        response = self.client.post(f'/bulbs/brightness/{self.driver.id}', self.request_valid)
        self.assertEqual(200, response.status_code)