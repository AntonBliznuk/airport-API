from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneSeatConfigurationViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewMemberPositionViewSet,
    CrewMemberViewSet,
)

router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane-seat-configurations", AirplaneSeatConfigurationViewSet)
router.register("crew-member-positions", CrewMemberPositionViewSet)
router.register("crew-members", CrewMemberViewSet)

app_name = "airport"

urlpatterns = [
    path("", include(router.urls)),
]