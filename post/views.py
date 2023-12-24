"""
Views related to posts APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from core.permissions import IsAdminUserOrReadOnly

from core.models import Post, Tag
from post import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Comma separated list of tags id to filter'
            ),
        ]
    )
)
class PostViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to apply CRUD on posts"""
    serializer_class = serializers.PostDetailSerializer
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]

    def _params_to_ints(self, qs):
        """Convert list of string to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_serializer_class(self):
        if action == 'list':
            return serializers.PostSerializer
        elif action == 'upload-image':
            return serializers.PostImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(by=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Uploads image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.get('tags', None)
        search_keywords = self.request.query_params.get('search', None)
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if search_keywords:
            queryset = queryset.filter(keywords__icontains=search_keywords)
        return queryset.order_by('-id').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT,
                enum=[0, 1],
                description='Filter by items assigned to post'
            )
        ]
    )
)
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

    def get_queryset(self):
        """Filter queryset based on the values of tags"""
        assigned_only = bool(self.request.query_params.get('assigned_only', 0))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(posts__isnull=False)
        return queryset.all().order_by('-id').distinct()
