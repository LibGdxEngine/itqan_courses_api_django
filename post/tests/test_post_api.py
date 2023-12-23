from unittest import TestCase

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from rest_framework import status
from django.urls import reverse
from core.models import Post, User, Tag
from post.serializers import PostSerializer, PostDetailSerializer

POSTS_URL = reverse("post:post-list")


def detail_url(post_id):
    """Return detail URL for post"""
    return reverse("post:post-detail", args=[post_id])


def create_post(user, **post_params):
    defaults = {
        'title': 'Test',
        'content': 'Test',
        'read_time_min': 2,
    }
    defaults.update(post_params)
    return Post.objects.create(by=user, **defaults)


class PublicPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_getting_posts_success(self):
        res = self.client.get(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivatePostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_superuser(
            email="admin_user@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.admin_user)

    def tearDown(self):
        self.admin_user.delete()

    def test_admin_getting_posts_success(self):
        """Test retrieving posts for authenticated admin-user"""
        first_user = get_user_model().objects.create_user(
            email='firstanother@example.com', password='testpass123'
        )
        create_post(user=first_user)

        res = self.client.get(POSTS_URL)
        posts = Post.objects.all().order_by('-id')
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_new_post_for_admin_user_success(self):
        """Test creating a new post for an admin user"""

        payload = {
            'title': 'Test',
            'content': 'Test',
            'read_time_min': 5,
            'status': 'published',
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}]
        }
        res = self.client.post(POSTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve and verify the created post
        post = Post.objects.get(id=res.data.get("id"))
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.read_time_min, payload['read_time_min'])
        self.assertEqual(post.status, payload['status'])
        self.assertEqual(post.by, self.admin_user)

    def test_create_new_post_for_non_admin_rejected(self):
        """Test creating a new post for non-admin user is rejected"""
        non_admin_user = User.objects.create_user(
            email='non_admin@example.com',
            password='PASSWORD'
        )
        # Create token for non_admin_user and authenticate with it
        token = Token.objects.create(user=non_admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client.force_authenticate(user=non_admin_user)

        payload = {
            'title': 'Test',
            'content': 'Test',
            'read_time_min': 5
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_post_detail(self):
        """Test getting a post by id"""
        post = create_post(self.admin_user, title='Test', content='Test')
        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_post(self):
        """Test updating a post."""
        post = create_post(self.admin_user,
                           title='Test Title',
                           content='Test Content',
                           )
        self.client.force_authenticate(user=self.admin_user)
        url = detail_url(post.id)
        res = self.client.patch(url,
                                {'title': 'New Test Title',
                                 'content': 'New Test Content'},
                                )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        self.assertEqual(post.title, 'New Test Title')
        self.assertEqual(post.content, 'New Test Content')
        self.assertEqual(post.by, self.admin_user)

    def test_full_update_post(self):
        """Test updating a full post"""
        post = create_post(self.admin_user,
                           title='Test Title',
                           content='Test Content',
                           status='published',
                           )
        url = detail_url(post.id)

        res = self.client.patch(url, {'title': 'New Test Title',
                                      'content': 'New Test Content',
                                      'status': 'draft',
                                      'read_time_min': 4})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        self.assertEqual(post.title, 'New Test Title')
        self.assertEqual(post.content, 'New Test Content')
        self.assertEqual(post.status, 'draft')
        self.assertEqual(post.read_time_min, 4)
        self.assertEqual(post.by, self.admin_user)

    def test_update_post_user_return_error(self):
        """Test updating a post user will return error message"""
        post = create_post(self.admin_user)
        url = detail_url(post.id)
        other_user = User.objects.create_user(
            email='other_email@gmail.com',
            password='PASSWORD'
        )

        self.client.patch(url, {'by': other_user.id})

        post.refresh_from_db()
        self.assertEqual(post.by, self.admin_user)

    def test_delete_post(self):
        """Test deleting a post return 204"""
        post = create_post(self.admin_user)
        url = detail_url(post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_create_post_with_new_tags(self):
        """Test creating a tag for a post"""
        payload = {
            'title': 'Test',
            'content': 'Test',
            'read_time_min': 2,
            'tags': [{'name': 'tag13'}, {'name': 'tag24'}]
        }

        res = self.client.post(POSTS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(by=self.admin_user)
        self.assertEqual(posts.count(), 1)
        post = posts.first()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.content, payload['content'])
        self.assertEqual(post.read_time_min, payload['read_time_min'])
        self.assertEqual(post.tags.count(), len(payload['tags']))

        for tag in payload['tags']:
            exists = Tag.objects.filter(
                name=tag['name'],
                user=self.admin_user,
            ).exists()
            self.assertTrue(exists)

    def test_create_post_with_existing_tag(self):
        """Test creating a tag for a post with an existing tag"""
        old_tag = Tag.objects.create(user=self.admin_user, name='Old tag')
        payload = {
            'title': 'Test',
            'content': 'Test',
            'read_time_min': 6,
            'tags': [{'name': 'Old tag'}, {'name': 'brand new tag'}]
        }
        self.client.post(POSTS_URL, payload, format='json')

        posts = Post.objects.filter(by=self.admin_user)
        self.assertEqual(posts.count(), 1)
        post = posts.first()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.content, payload['content'])
        self.assertEqual(post.tags.count(), len(payload['tags']))
        self.assertIn(old_tag, post.tags.all())
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                name=tag['name'],
                user=self.admin_user
            ).exists()
            self.assertTrue(exists)
