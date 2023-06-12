from rest_framework.filters import BaseFilterBackend
from recipe.models import IngredientModel


class IngredientFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('name'):
            string_name = request.query_params['name']
            queryset = (
                IngredientModel.objects.filter(name__iendswith=string_name)
                | IngredientModel.objects.filter(name__istartswith=string_name)
            )
        return queryset
