from django.urls import include, path
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneSeatConfigurationViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CrewMemberPositionViewSet,
    CrewMemberViewSet,
    FlightViewSet,
    OrderViewSet,
    RouteViewSet,
    TicketViewSet,
)

router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane-seat-configurations", AirplaneSeatConfigurationViewSet)
router.register("crew-member-positions", CrewMemberPositionViewSet)
router.register("crew-members", CrewMemberViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)
router.register("orders", OrderViewSet)

app_name = "airport"

urlpatterns = [
    path("", include(router.urls)),
]