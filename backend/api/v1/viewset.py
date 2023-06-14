from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class GetViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """Viewset для Get-запросов."""

    pass
