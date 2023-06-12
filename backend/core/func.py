from core.exception import BadRequest


def get_object_or_400(model, *args, **kwargs):
    queryset = model.objects.all()
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise BadRequest()
