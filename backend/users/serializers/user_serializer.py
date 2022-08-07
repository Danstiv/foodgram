from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.fields import ObjectExistsInUserRelatedManagerField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = ObjectExistsInUserRelatedManagerField('subscribed_to')

    class Meta:
        model = User
        fields = [
            'email', 'username', 'id',
            'first_name', 'last_name', 'is_subscribed'
        ]
