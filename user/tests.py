from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.username = 'testuser'
        self.password = 'securepass123'

        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_signup(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password': 'newpass123',
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)

    def test_logout(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 0)

    def test_logout_without_auth(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 401)
