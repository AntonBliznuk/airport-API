from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneTypeViewSet,
)

router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)

app_name = "airport"

urlpatterns = [
    path("", include(router.urls)),
]