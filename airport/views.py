from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType,
)
from airport.permissions import IsAdminUserOrReadOnly
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSeatConfigurationListSerializer,
    AirplaneSeatConfigurationRetrieveSerializer,
    AirplaneTypeSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        return AirplaneTypeSerializer


class AirplaneSeatConfigurationViewSet(viewsets.ModelViewSet):
    queryset = (
        AirplaneSeatConfiguration
        .objects.prefetch_related("airplane")
        .select_related("airplane__airplane_type")
    )
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneSeatConfigurationRetrieveSerializer
        return AirplaneSeatConfigurationListSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = (
        Airplane
        .objects
        .select_related("airplane_type")
        .prefetch_related("seat_configurations")
    )
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return AirplaneRetrieveSerializer
        return AirplaneListSerializer
