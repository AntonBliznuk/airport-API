from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/airport/", include("airport.urls", namespace="airport")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/doc/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'api/doc/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
