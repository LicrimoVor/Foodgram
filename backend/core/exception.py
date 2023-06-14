from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    """400 ошибка."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"errors": "string"}
    default_code = 'parse_error'
