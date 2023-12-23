"""
Tests for tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from post.serializers import TagSerializer

TAGS_URL = reverse('post:tag-list')


def detail_url(tag_id):
    return reverse('post:tag-detail', args=[tag_id])


def create_user(email='email@example.com', password='<PASSWORD>'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_getting_tags_success(self):
        """Test retrieving tags for unauthenticated user return list of tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='<PASSWORD>'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags_success(self):
        """Test retrieving tags for authenticated user return list of tags"""
        Tag.objects.create(user=self.user, name="test tag 1")
        Tag.objects.create(user=self.user, name="test tag 2")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')

        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_successful(self):
        """Test creating tag for authenticated user success"""

        self.client.force_authenticate(user=self.user)

        payload = {'name': 'test tag'}
        res = self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(name=payload['name']).exists()

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_update_tag(self):
        """Test updating tag for authenticated user"""
        tag = Tag.objects.create(user=self.user, name="test tag")

        payload = {'name': 'updated name'}
        res = self.client.patch(detail_url(tag.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="test delete tag")
        res = self.client.delete(detail_url(tag.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tag_exists = Tag.objects.filter(name='test delete tag').exists()
        self.assertFalse(tag_exists)
