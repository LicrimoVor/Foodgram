from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class GetViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
    ):
    """Viewset для получения списка моделей."""

    pass

class GetPostDelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
    ):
    """Viewset для получения списка, удаления и создания моделей."""

    pass

class PostDelViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
    ):
    """Viewset для удаления и создания моделей."""

    pass