"""
Tests for the user api
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@passord',
            'name': 'test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertTrue('password' not in res.data)

    def test_user_exists(self):
        """Test creating a user that already exist"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@passord',
            'name': 'test name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'te',
            'name': 'test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user_exists)

    def test_authenticate_user_success(self):
        """Test authenticating user successfully"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@password',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in res.data)

    def test_authenticate_user_fail(self):
        """Test authenticating user fails when invalid credentials"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@rd',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('token' not in res.data)

    def test_create_token_password_empty(self):
        """Test authenticating user with empty password returns error"""
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('token' not in res.data)

    def test_retrieve_user_unauthorized(self):
        """Test retrieving user unauthorized"""
        res = self.client.get(ME_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test Private API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test@password',
            name='test@user'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):
        """Test retrieving user success"""
        res = self.client.get(ME_URL)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, {'email': self.user.email, 'name': self.user.name})

    def test_post_not_allowed(self):
        """Test post is not allowed for authenticated user"""
        res = self.client.post(ME_URL, {})
        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_for_authenticated_user(self):
        """Test updating user profile details for authenticated user"""
        payload = {'name': 'updated name', 'password': 'new password'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
        
