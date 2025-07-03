from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType, CrewMemberPosition,
)
from airport.permissions import IsAdminUserOrReadOnly
from airport.serializers import (
    AirplaneImageSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSeatConfigurationListSerializer,
    AirplaneSeatConfigurationRetrieveSerializer,
    AirplaneTypeListSerializer,
    AirplaneTypeRetrieveSerializer,
    CrewMemberPositionListSerializer,
    CrewMemberPositionRetrieveSerializer,
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
        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneListSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewMemberPositionViewSet(viewsets.ModelViewSet):
    queryset = CrewMemberPosition.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return CrewMemberPositionRetrieveSerializer
        return CrewMemberPositionListSerializer

    def get_queryset(self):
        qs = self.queryset
        if self.action == "retrieve":
            qs = (
                CrewMemberPosition
                .objects
                .prefetch_related("crew_members")
                .annotate(crew_members_total=Count("crew_members"))
            )
        elif self.action == "list":
            qs = (
                CrewMemberPosition
                .objects
                .annotate(crew_members_total=Count("crew_members"))
            )
        return qs
