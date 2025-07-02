from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from airport.models import (
    AirplaneType,
)
from airport.serializers import (
    AirplaneTypeSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]
