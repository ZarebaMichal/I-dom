import json
from register.models import CustomUser
from cameras.models import Cameras
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.test import Client


class AddCameraAPIViewTestCase(APITestCase):
    """
    Tests for adding new camera
    """

    def setUp(self):
        self.username = 'foka'
        self.email = 'fokafoka@gmail.com'
        self.password = 'fokimajapletwy'
        self.telephone = '+48606606606'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language)

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'korytarz'

        self.camera = Cameras.objects.create(name=self.name)

    def test_add_camera_with_name_already_exists(self):
        response = self.client.post('/cameras/add', {'name': self.name})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Cameras.objects.all().count(), 1)

    def test_add_camera_without_name(self):
        response = self.client.post('/cameras/add', {'name': ''})
        self.assertEqual(400, response.status_code)
        self.assertTrue(Cameras.objects.all().count(), 1)


class GetListOfCamerasAPIViewTestCase(APITestCase):
    """
    Test for getting list of cameras, and their details
    """
    def setUp(self):
        self.username = 'foka'
        self.email = 'fokafoka@gmail.com'
        self.password = 'fokimajapletwy'
        self.telephone = '+48606606606'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language)

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'korytarz'
        self.name2 = 'korytarz2'
        self.id = 10

        self.camera = Cameras.objects.create(name=self.name)
        self.camera2 = Cameras.objects.create(name=self.name2)

    def test_get_list_of_cameras(self):
        response = self.client.get('/cameras/list')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Cameras.objects.all().count(), 2)

    def test_get_single_camera_detail(self):
        response = self.client.get(f'/cameras/detail/{self.camera.id}')
        self.assertEqual(200, response.status_code)

    def test_get_single_not_existing_detail_of_camera(self):
        response = self.client.get(f'/cameras/detail/{self.id}')
        self.assertEqual(404, response.status_code)


class DeleteCameraAPIViewTestCase(APITestCase):
    """
    Tests for deleting camera
    """
    def setUp(self):
        self.username = 'foka'
        self.email = 'fokafoka@gmail.com'
        self.password = 'fokimajapletwy'
        self.telephone = '+48606606606'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language)

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'korytarz'
        self.name2 = 'korytarz2'
        self.id = 40

        self.camera = Cameras.objects.create(name=self.name)
        self.camera2 = Cameras.objects.create(name=self.name2)

    def test_delete_valid_camera(self):
        response = self.client.delete(f'/cameras/delete/{self.camera.id}')
        self.assertEqual(200, response.status_code)

    def test_delete_not_existing_camera(self):
        response = self.client.delete(f'/cameras/delete/{self.id}')
        self.assertEqual(404, response.status_code)


class UpdateCameraAPIViewTestCase(APITestCase):
    """
    Tests for updating cameras data
    """

    def setUp(self):
        self.username = 'foka'
        self.email = 'fokafoka@gmail.com'
        self.password = 'fokimajapletwy'
        self.telephone = '+48606606606'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language)

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'korytarz'
        self.name2 = 'korytarz2'
        self.id = 40

        self.camera = Cameras.objects.create(name=self.name)
        self.camera2 = Cameras.objects.create(name=self.name2)

        self.validated_payload = json.dumps({
            'name': 'salon',
            'ip_address': '192.168.18.7'
        })

        self.non_validated_payload = json.dumps({
            'name': '',
            'ip_address': '192.168.18.6'
        })

        self.non_validated_payload2 = json.dumps({
            'name' : 'korytarz2',
            'ip_address': '192.168.18.6'
        })

    def test_update_camera(self):
        response = self.client.put(f'/cameras/update/{self.camera.id}', self.validated_payload,
                                   content_type='application/json')
        self.assertEqual(200, response.status_code)

    def test_no_name_update(self):
        response = self.client.put(f'/cameras/update/{self.camera.id}', self.non_validated_payload,
                                   content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_existing_name_update(self):
        response = self.client.put(f'/cameras/update/{self.camera.id}', self.non_validated_payload2,
                                   content_type='application/json')
        self.assertEqual(400, response.status_code)


class AddIPAddressAPITestCase(APITestCase):

    def setUp(self):
        self.username = 'foka'
        self.email = 'fokafoka@gmail.com'
        self.password = 'fokimajapletwy'
        self.telephone = '+48606606606'
        self.language = 'pl'

        self.user = CustomUser.objects.create_user(
            self.username, self.email, self.password, self.telephone, self.language)

        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.name = 'korytarz'
        self.name2 = 'korytarz2'
        self.id = 40

        self.camera = Cameras.objects.create(name=self.name)

        self.invalid_ip = {
            'name': 'korytarz',
            'ip_address': '111112222'
        }

        self.invalid_camera = {
            'name': 'tiruru',
            'ip_address': '192.168.1.7'
        }

        self.correct_data = {
            'name': 'korytarz',
            'ip_address': '192.168.1.6'
        }

    def test_add_invalid_ip(self):
        response = self.client.post('/cameras/ip', self.invalid_ip)
        self.assertEqual(400, response.status_code)

    def test_add_not_existing_camera(self):
        response = self.client.post('/cameras/ip', self.invalid_camera)
        self.assertEqual(404, response.status_code)

    def test_add_correct_data(self):
        response = self.client.post('/cameras/ip', self.correct_data)
        self.assertEqual(200, response.status_code)

