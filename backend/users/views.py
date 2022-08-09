from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    CustomUserCreateSerializer,
    CustomUserResponseOnCreateSerializer,
    SetPasswordSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)
from core.pagination import CustomPagination
from core.utils import user_related_create_destroy_action

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = []
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        errors = []
        if User.objects.filter(
            username=serializer.validated_data['username']
        ).exists():
            errors.append('Имя пользователя занято.')
        if User.objects.filter(
            email=serializer.validated_data['email']
        ).exists():
            errors.append('Email занят.')
        if errors:
            return Response(
                {'errors': '\n'.join(errors)},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            password=serializer.validated_data['password'],
        )
        serializer = CustomUserResponseOnCreateSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
        url_path='set_password',
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not check_password(
            serializer.validated_data['current_password'],
            request.user.password
        ):
            return Response(
                {'errors': 'Текущий пароль указан неверно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        queryset = request.user.subscribed_to.all()
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, self.request, view=self)
        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
    )
    def subscribe(self, request, pk):
        return user_related_create_destroy_action(
            self, request, pk,
            manager_name='subscribed_to',
            already_exists_error='Вы уже подписаны на этого пользователя',
            not_exists_error='Вы не подписаны на этого пользователя',
            serializer_class=UserWithRecipesSerializer
        )
