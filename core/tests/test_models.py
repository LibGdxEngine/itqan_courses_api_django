"""
Tests for models
"""

from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from core import models
from core.models import User, Tag


class ModelTests(TestCase):
    """Test for models"""

    def test_create_user_with_email_successful(self):
        """test creating user with an email is successful."""
        email = "test@example.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_is_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@example.com', 'TEST3@example.com'],
            ['test4@EXAMPLE.com', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEquals(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without an email raises value error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_post(self):
        """Test creating post is successful"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test@password'
        )
        post = models.Post.objects.create(
            title='test title',
            content='test content',
            by=user,
            read_time_min=5,
        )

        self.assertEquals(str(post), post.title)

    def test_create_tag(self):
        """Test creating tag is successful"""
        user = User.objects.create_user(
            email='test@example.com',
            password='<PASSWORD>'
        )
        tag = Tag.objects.create(user=user, name='testtag')

        self.assertEqual(str(tag), tag.name)

    @patch('core.models.uuid.uuid4')
    def test_post_file_name_uuid(self, mock_uuid4):
        """Test creating a file name is successful"""
        uuid = 'test-uuid'
        mock_uuid4.return_value = uuid
        file_path = models.post_image_file_path(None, 'myimage.jpg')
        self.assertEqual(file_path, f'uploads/post/{uuid}.jpg')
