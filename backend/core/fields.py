import binascii
import mimetypes
import urllib

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers


class ObjectExistsInUserRelatedManagerField(serializers.Field):
    def __init__(self, manager_name, **kwargs):
        self.manager_name = manager_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        if 'request' not in self.context:
            return False
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return False
        manager = getattr(current_user, self.manager_name)
        return manager.filter(id=value.id).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        msg = 'Неверный формат данных'
        if not data.startswith('data:') or ';base64,' not in data:
            raise serializers.ValidationError(msg)
        try:
            result = urllib.request.urlopen(data)
        except (TypeError, binascii.Error, ValueError):
            raise serializers.ValidationError(msg)
        content_type = result.headers.get('Content-Type')
        extension = mimetypes.guess_extension(content_type)
        return super().to_internal_value(SimpleUploadedFile(
            name='image' + extension,
            content=result.read(),
            content_type=content_type
        ))
