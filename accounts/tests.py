# accounts/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'newuser11',
            'email': 'newuser11@example.com',
            'password': 'password123',
            'password_confirmation': 'password123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser11')
        self.assertEqual(response.data['email'], 'newuser11@example.com')

    def test_register_user_password_mismatch(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirmation': 'differentpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'Passwords do not match')
