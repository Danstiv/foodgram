from rest_framework.serializers import Field


class ObjectExistsInUserRelatedManagerField(Field):
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
