from django.db.models import Count
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
    AirplaneTypeListSerializer,
    AirplaneTypeRetrieveSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ("retrieve", "update", "partial_update"):
            return AirplaneTypeRetrieveSerializer
        return AirplaneTypeListSerializer

    def get_queryset(self):
        qs = self.queryset.all()
        if self.action == "retrieve":
            qs = (
                AirplaneType
                .objects
                .prefetch_related("airplanes")
                .annotate(airplanes_total=Count("airplanes"))
            )
        elif self.action == "list":
            qs = AirplaneType.objects.annotate(airplanes_total=Count("airplanes"))
        return qs


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
