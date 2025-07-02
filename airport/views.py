from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from airport.models import (
    Airplane,
    AirplaneType,
)
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneTypeSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = (
        Airplane
        .objects
        .select_related("airplane_type")
        .prefetch_related("seat_configurations")
    )

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return AirplaneRetrieveSerializer
        return AirplaneListSerializer
