from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.LimitOffsetPagination):
    """Убирает лишние поля next, count, previous при пагинации."""
    def get_paginated_response(self, data):
        return Response(data)
