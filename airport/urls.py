from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneSeatConfigurationViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
)

router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane-seat-configurations", AirplaneSeatConfigurationViewSet)

app_name = "airport"

urlpatterns = [
    path("", include(router.urls)),
]