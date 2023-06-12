from django.urls import include, path, re_path

urlpatterns = [
    path('', include("api.v1.urls")),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
