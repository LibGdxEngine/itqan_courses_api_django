"""
URL Configuration for posts API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post.views import PostViewSet, TagViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('tags', TagViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
]
