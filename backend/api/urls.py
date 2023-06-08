from django.urls import path, include, re_path

urlpatterns = [
    path('v1/', include("api.v1.urls")),
    path('v1/auth/', include('djoser.urls')), 
    re_path('auth/', include('djoser.urls.authtoken')),
]
