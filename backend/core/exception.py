from rest_framework.exceptions import APIException
from rest_framework import status


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"errors": "string"}
    default_code = 'parse_error'