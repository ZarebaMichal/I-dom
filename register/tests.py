from django.test import TestCase
from django.contrib.auth import get_user_model


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='Foka', email='xd@gmail.com', telephone='669938635', password='xdd')
        self.assertEqual(user.email, 'xd@gmail.com')
        self.assertEqual(user.username, 'Foka')
        self.assertEqual(user.telephone, '669938635')
        self.assertFalse(user.is_superuser)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', email='', telephone='', password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('superusers', 'super@user.com', 'foo', '545454545')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
               username='superusers', email='super@user.com', password='foo', telephone='545454545', is_superuser=False)
