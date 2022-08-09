from rest_framework import status
from rest_framework.response import Response


class MonkeyPatchPartial:
    """
    Work around bug #3847 in djangorestframework by monkey-patching the partial
    attribute of the root serializer during the call to validate_empty_values.
    """

    def __init__(self, root):
        self._root = root

    def __enter__(self):
        self._old = getattr(self._root, 'partial')
        setattr(self._root, 'partial', False)

    def __exit__(self, *args):
        setattr(self._root, 'partial', self._old)


class OverrideRootPartialMixin:
    def run_validation(self, *args, **kwargs):
        if not self.partial:
            with MonkeyPatchPartial(self.root):
                return super().run_validation(*args, **kwargs)
        return super().run_validation(*args, **kwargs)


def user_related_create_destroy_action(
    self,
    request,
    pk,
    *,
    manager_name,
    already_exists_error,
    not_exists_error,
    serializer_class
):
    obj = self.get_object()
    user = request.user
    manager = getattr(user, manager_name)
    if request.method == 'POST':
        if manager.filter(id=pk).exists():
            return Response(
                {'errors': already_exists_error},
                status=status.HTTP_400_BAD_REQUEST
            )
        manager.add(obj)
        serializer = serializer_class(obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not manager.filter(id=pk).exists():
        return Response(
            {'errors': not_exists_error},
            status=status.HTTP_400_BAD_REQUEST
        )
    manager.remove(obj)
    return Response(status=status.HTTP_204_NO_CONTENT)
