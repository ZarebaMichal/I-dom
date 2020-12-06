import json

from actions.models import Actions
from driver.models import Drivers
from register.models import CustomUser
from sensors.models import Sensors, SensorsData
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.test import Client
from rest_framework.test import APIClient


class AddActionAPIViewTestCase(APITestCase):
    """
    Tests for adding new action
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

        self.name_sensor = 'piwnica'
        self.category_sensor = 'temperature'
        self.frequency_sensor = 9999999999
        self.test_sensor = Sensors.objects.create(name=self.name_sensor, category=self.category_sensor)

        self.name_driver = 'Pilot'
        self.category_driver = 'remote_control'
        self.test_driver = Drivers.objects.create(name=self.name_driver, category=self.category_driver, data=False)

        self.name = 'bulb_night'
        self.sensor = self.test_sensor
        self.trigger = '15'
        self.operator = '<'
        self.driver = self.test_driver
        self.days = '1, 2'
        self.start_event = '12:00'
        self.end_event = '13:00'
        self.action = '1'
        self.flag = 4
        self.test_action = Actions.objects.create(name=self.name, sensor=self.sensor, trigger=self.trigger,
                                                  operator=self.operator, driver=self.driver, days=self.days,
                                                  start_event=self.start_event, end_event=self.end_event,
                                                  action=self.action, flag=self.flag)

    def test_add_action(self):
        response = self.client.post('/actions/add', {
                                                      "name": "bulb_day",
                                                      "sensor": "",
                                                      "trigger": "",
                                                      "operator": "",
                                                      "driver": "Pilot",
                                                      "is_active": True,
                                                      "days": '1',
                                                      "start_event": "12:00",
                                                      "end_event": "",
                                                      "action": '1',
                                                      "flag": 1
                                                    })
        self.assertEqual(201, response.status_code)
        self.assertTrue(Actions.objects.filter(name='bulb_day').exists())
        self.assertEqual(Actions.objects.all().count(), 2)

    def test_add_action_with_the_same_name(self):
        response = self.client.post('/actions/add', {
                                                        "name": "bulb_night",
                                                        "sensor": "",
                                                        "trigger": "",
                                                        "operator": "",
                                                        "driver": "Pilot",
                                                        "is_active": True,
                                                        "days": '1',
                                                        "start_event": "12:00",
                                                        "end_event": "",
                                                        "action": '1',
                                                        "flag": 1
                                                    })
        self.assertEqual(400, response.status_code)
        self.assertTrue(Sensors.objects.all().count(), 1)


class GetListOfActionsAPIViewTestCase(APITestCase):
    """
    Tests for getting list of actions
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

        self.name_sensor = 'piwnica'
        self.category_sensor = 'temperature'
        self.frequency_sensor = 9999999999
        self.test_sensor = Sensors.objects.create(name=self.name_sensor, category=self.category_sensor)

        self.name_driver = 'Pilot'
        self.category_driver = 'remote_control'
        self.test_driver = Drivers.objects.create(name=self.name_driver, category=self.category_driver, data=False)

        self.id = 9
        self.name = 'bulb_night'
        self.sensor = self.test_sensor
        self.trigger = '15'
        self.operator = '<'
        self.driver = self.test_driver
        self.days = '1, 2'
        self.start_event = '12:00'
        self.end_event = '13:00'
        self.action = '1'
        self.flag = 4
        self.test_action = Actions.objects.create(name=self.name, sensor=self.sensor, trigger=self.trigger,
                                                  operator=self.operator, driver=self.driver, days=self.days,
                                                  start_event=self.start_event, end_event=self.end_event,
                                                  action=self.action, flag=self.flag)

    def test_get_list_of_actions(self):
        response = self.client.get('/actions/list')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Sensors.objects.all().count(), 1)

    def test_get_single_action(self):
        response = self.client.get(f'/actions/detail/{self.test_action.id}')
        self.assertEqual(200, response.status_code)

    def test_single_not_existing_detail_of_action(self):
        response = self.client.get(f'/sensors/detail/{self.id}')
        self.assertEqual(404, response.status_code)


class DeleteActionAPIViewTestCase(APITestCase):
    """
    Tests for deleting new action
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

        self.name_sensor = 'piwnica'
        self.category_sensor = 'temperature'
        self.frequency_sensor = 9999999999
        self.test_sensor = Sensors.objects.create(name=self.name_sensor, category=self.category_sensor)

        self.name_driver = 'Pilot'
        self.category_driver = 'remote_control'
        self.test_driver = Drivers.objects.create(name=self.name_driver, category=self.category_driver, data=False)

        self.id = 9
        self.name = 'bulb_night'
        self.sensor = self.test_sensor
        self.trigger = '15'
        self.operator = '<'
        self.driver = self.test_driver
        self.days = '1, 2'
        self.start_event = '12:00'
        self.end_event = '13:00'
        self.action = '1'
        self.flag = 4
        self.test_action = Actions.objects.create(name=self.name, sensor=self.sensor, trigger=self.trigger,
                                                  operator=self.operator, driver=self.driver, days=self.days,
                                                  start_event=self.start_event, end_event=self.end_event,
                                                  action=self.action, flag=self.flag)

    def test_delete_action(self):
        response = self.client.delete(f'/actions/delete/{self.test_action.id}')
        self.assertEqual(200, response.status_code)
        self.assertEqual(Sensors.objects.all().count(), 1)

    def test_delete_not_existing_action(self):
        response = self.client.delete(f'/actions/delete/{self.id}')
        self.assertEqual(404, response.status_code)


class UpdateActionAPIViewTestCase(APITestCase):
    """
    Tests for updating new action
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

        self.name_sensor = 'piwnica'
        self.category_sensor = 'temperature'
        self.frequency_sensor = 9999999999
        self.test_sensor = Sensors.objects.create(name=self.name_sensor, category=self.category_sensor)

        self.name_driver = 'Pilot'
        self.category_driver = 'remote_control'
        self.test_driver = Drivers.objects.create(name=self.name_driver, category=self.category_driver, data=False)

        self.id = 9
        self.name = 'bulb_night'
        self.sensor = self.test_sensor
        self.trigger = '15'
        self.operator = '<'
        self.driver = self.test_driver
        self.days = '1, 2'
        self.start_event = '12:00'
        self.end_event = '13:00'
        self.action = '1'
        self.flag = 4
        self.test_action = Actions.objects.create(name=self.name, sensor=self.sensor, trigger=self.trigger,
                                                  operator=self.operator, driver=self.driver, days=self.days,
                                                  start_event=self.start_event, end_event=self.end_event,
                                                  action=self.action, flag=self.flag)

        self.validated_payload = {
            "end_event": "14:00",
        }

        self.non_validated_payload = {
            "sensor": "Pilot",
        }

    def test_update_action(self):
        response = self.client.put(f'/actions/update/{self.test_action.pk}', self.validated_payload)
        self.assertEqual(200, response.status_code)

    def test_fail_update_action(self):
        response = self.client.put(f'/action/update/{self.test_action.pk}', self.non_validated_payload)
        self.assertEqual(400, response.status_code)

    def test_fail_no_action_update(self):
        response = self.client.put(f'/actions/update/{self.id}', self.validated_payload)
        self.assertEqual(404, response.status_code)