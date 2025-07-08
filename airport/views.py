from datetime import datetime, timedelta

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType,
    Airport,
    CrewMember,
    CrewMemberPosition,
    Flight,
    Order,
    Route,
    Ticket,
)
from airport.permissions import (
    IsAdminUserOrReadOnly,
    IsOwner,
    IsOwnerOrIsAdminOrReadOnly,
)
from airport.serializers import (
    AirplaneImageSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSeatConfigurationListSerializer,
    AirplaneSeatConfigurationRetrieveSerializer,
    AirplaneTypeListSerializer,
    AirplaneTypeRetrieveSerializer,
    AirportImageSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    CrewMemberImageSerializer,
    CrewMemberListSerializer,
    CrewMemberPositionListSerializer,
    CrewMemberPositionRetrieveSerializer,
    CrewMemberRetrieveSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderListSerializer,
    OrderPaySerializer,
    OrderRetrieveSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
)


class SearchMixin:
    @staticmethod
    def _params_to_ints(params):
        return [int(param) for param in params.split(",")]

    @staticmethod
    def _string_to_date(departure_day):
        try:
            day = datetime.strptime(departure_day, "%Y-%m-%d").date()
            start_of_day = datetime.combine(day, datetime.min.time())
            end_of_day = start_of_day + timedelta(days=1)
            return start_of_day, end_of_day
        except ValueError:
            return None


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return AirplaneTypeRetrieveSerializer
        return AirplaneTypeListSerializer

    def get_queryset(self):
        qs = self.queryset.all()
        if self.action == "retrieve":
            qs = AirplaneType.objects.prefetch_related("airplanes").annotate(
                airplanes_total=Count("airplanes")
            )
        elif self.action == "list":
            qs = AirplaneType.objects.annotate(airplanes_total=Count("airplanes"))
        return qs


class AirplaneSeatConfigurationViewSet(viewsets.ModelViewSet):
    queryset = AirplaneSeatConfiguration.objects.prefetch_related(
        "airplane"
    ).select_related("airplane__airplane_type")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneSeatConfigurationRetrieveSerializer
        return AirplaneSeatConfigurationListSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type").prefetch_related(
        "seat_configurations"
    )
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
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
            qs = CrewMemberPosition.objects.prefetch_related("crew_members").annotate(
                crew_members_total=Count("crew_members")
            )
        elif self.action == "list":
            qs = CrewMemberPosition.objects.annotate(
                crew_members_total=Count("crew_members")
            )
        return qs


class CrewMemberViewSet(viewsets.ModelViewSet):
    queryset = CrewMember.objects.select_related("position")
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return CrewMemberRetrieveSerializer
        elif self.action == "upload_image":
            return CrewMemberImageSerializer
        return CrewMemberListSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        crew_member = self.get_object()
        serializer = self.get_serializer(crew_member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return AirportRetrieveSerializer
        elif self.action == "upload_image":
            return AirportImageSerializer
        return AirportListSerializer

    def get_queryset(self):
        qs = Airport.objects.annotate(source_routes_total=Count("sources")).annotate(
            destination_routes_total=Count("destinations")
        )
        if self.action == "retrieve":
            qs = qs.prefetch_related("sources", "destinations")
        return qs

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return RouteRetrieveSerializer
        return RouteListSerializer

    def get_queryset(self):
        qs = Route.objects.select_related("source", "destination")
        return qs


class FlightViewSet(viewsets.ModelViewSet, SearchMixin):
    queryset = Flight.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return FlightRetrieveSerializer
        return FlightListSerializer

    def get_queryset(self):
        qs = Flight.objects.select_related(
            "route__source", "route__destination", "airplane__airplane_type"
        )

        airplane_id = self.request.query_params.get("airplane-id", None)
        if airplane_id:
            qs = qs.filter(airplane_id=int(airplane_id))

        route_id = self.request.query_params.get("route-id", None)
        if route_id:
            qs = qs.filter(route_id=int(route_id))

        crew_ids = self.request.query_params.get("crew-ids", None)
        if crew_ids:
            qs = qs.filter(crew__in=self._params_to_ints(crew_ids))

        departure_day = self.request.query_params.get("departure-day", None)
        if departure_day:
            start_of_day, end_of_day = self._string_to_date(departure_day)
            qs = qs.filter(
                departure_time__gte=start_of_day, departure_time__lt=end_of_day
            )

        if self.action == "retrieve":
            qs = qs.prefetch_related("crew__position", "airplane__seat_configurations")
        return qs


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        "flight__route__source",
        "flight__route__destination",
        "order__user",
    )
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return TicketRetrieveSerializer
        return TicketListSerializer


class OrderViewSet(viewsets.ModelViewSet, SearchMixin):
    queryset = Order.objects.all()
    permission_classes = [IsOwnerOrIsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"retrieve", "update", "partial_update"}:
            return OrderRetrieveSerializer
        if self.action == "pay":
            return OrderPaySerializer
        return OrderListSerializer

    def get_queryset(self):
        qs = Order.objects.select_related("user").prefetch_related(
            "tickets__flight__route"
        )
        if not self.request.user.is_staff:
            qs = Order.objects.filter(user=self.request.user)

        order_day = self.request.query_params.get("order-day", None)
        if order_day:
            start_of_day, end_of_day = self._string_to_date(order_day)
            qs = qs.filter(created_at__gte=start_of_day, created_at__lt=end_of_day)
        return qs

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsOwner],
        url_path="pay",
    )
    def pay(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
