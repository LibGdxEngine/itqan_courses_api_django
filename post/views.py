"""
Views related to posts APIs
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication

from core.permissions import IsAdminUserOrReadOnly

from core.models import Post, Tag
from post import serializers


class PostViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to apply CRUD on posts"""
    serializer_class = serializers.PostDetailSerializer
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(by=self.request.user)


class TagViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """API endpoint that allows tags to be viewed or edited"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
