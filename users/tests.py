from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Role


def create_user(email, password, role=Role.VIEWER, is_active=True):
    user = User.objects.create_user(email=email, name='Test', password=password, role=role)
    user.is_active = is_active
    user.save()
    return user


def get_token(client, email, password):
    res = client.post(reverse('login'), {'email': email, 'password': password}, format='json')
    return res.data.get('access', '')


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        res = self.client.post(reverse('register'), {
            'email': 'new@test.com', 'name': 'New', 'password': 'Pass@1234'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', res.data)

    def test_register_duplicate_email(self):
        create_user('dup@test.com', 'Pass@1234')
        res = self.client.post(reverse('register'), {
            'email': 'dup@test.com', 'name': 'Dup', 'password': 'Pass@1234'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        res = self.client.post(reverse('register'), {'email': 'x@test.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_user('login@test.com', 'Pass@1234')

    def test_login_success(self):
        res = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'Pass@1234'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_wrong_password(self):
        res = self.client.post(reverse('login'), {
            'email': 'login@test.com', 'password': 'wrong'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        create_user('inactive@test.com', 'Pass@1234', is_active=False)
        res = self.client.post(reverse('login'), {
            'email': 'inactive@test.com', 'password': 'Pass@1234'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RolePermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin   = create_user('admin@test.com',   'Pass@1234', Role.ADMIN)
        self.analyst = create_user('analyst@test.com', 'Pass@1234', Role.ANALYST)
        self.viewer  = create_user('viewer@test.com',  'Pass@1234', Role.VIEWER)

    def auth(self, user_email, password='Pass@1234'):
        token = get_token(self.client, user_email, password)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_admin_can_list_users(self):
        self.auth('admin@test.com')
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_list_users(self):
        self.auth('viewer@test.com')
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_cannot_list_users(self):
        self.auth('analyst@test.com')
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        self.client.credentials()  # no token
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)