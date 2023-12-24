"""
Tests for health_check api
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

HEALTH_CHECK_URL = reverse('health-check')


class TestHealthCheck(TestCase):
    """Test the health_check api"""

    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        """Test the health_check api"""
        res = self.client.get(HEALTH_CHECK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
