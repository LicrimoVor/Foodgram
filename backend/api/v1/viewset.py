from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class GetViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Viewset для получения списка моделей."""

    pass

class GetPostDelViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset для получения списка, удаления и создания моделей."""

    pass
