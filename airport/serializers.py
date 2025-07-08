from rest_framework import serializers

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
    SeatClass,
    Ticket,
)

# ----------- Airplane, AirplaneType, AirplaneSeatConfiguration serializers -----------

class AirplaneSeatConfigurationSerializer(serializers.ModelSerializer):
    seat_class = serializers.ChoiceField(choices=SeatClass.choices)

    class Meta:
        model = AirplaneSeatConfiguration
        fields = ("id", "seat_class", "rows", "seats_in_row", "capacity")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all(), write_only=True
    )
    airplane_type_name = serializers.CharField(
        source="airplane_type.name", read_only=True
    )
    seat_configurations = AirplaneSeatConfigurationSerializer(
        many=True, write_only=True
    )
    image = serializers.SerializerMethodField()
    total_seats = serializers.SerializerMethodField()

    @staticmethod
    def get_total_seats(obj):
        return sum([conf.capacity for conf in obj.seat_configurations.all()])

    @staticmethod
    def get_image(obj):
        return str(obj.image.url) if obj.image else None

    @staticmethod
    def validate_seat_configurations(value):
        if len(value) < 1:
            raise serializers.ValidationError("Seat configuration must be provided.")
        seen = set()
        for configuration in value:
            seat_class = configuration.get("seat_class")
            if seat_class in seen:
                raise serializers.ValidationError(
                    f"Duplicate seat_class '{seat_class}' found."
                )
            seen.add(seat_class)
        return value

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "image",
            "airplane_type_id",
            "airplane_type_name",
            "total_seats",
            "seat_configurations",
        )


class AirplaneListSerializer(AirplaneSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "image",
            "airplane_type_id",
            "airplane_type_name",
            "total_seats",
            "seat_configurations",
        )

    def create(self, validated_data):
        seat_configurations = validated_data.pop("seat_configurations")
        airplane_type = validated_data.pop("airplane_type_id")
        instance = Airplane.objects.create(
            airplane_type=airplane_type,
            **validated_data
        )

        for conf in seat_configurations:
            AirplaneSeatConfiguration.objects.create(
                seat_class=conf["seat_class"],
                rows=conf["rows"],
                seats_in_row=conf["seats_in_row"],
                airplane=instance,
            )
        instance.save()
        return instance


class AirplaneImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = Airplane
        fields = (
            "id", "image"
        )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    seat_configurations = AirplaneSeatConfigurationSerializer(many=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all()
    )


    def update(self, instance, validated_data):
        seat_configurations_data = validated_data.pop("seat_configurations", [])

        instance.name = validated_data.get("name", instance.name)
        instance.airplane_type = validated_data.get(
            "airplane_type_id", instance.airplane_type
        )
        instance.save()

        existing_configs = {
            config.seat_class: config for config in instance.seat_configurations.all()
        }

        for seat_configuration in seat_configurations_data:
            seat_class = seat_configuration.get("seat_class")
            existing_config = existing_configs.get(seat_class)
            AirplaneSeatConfiguration.objects.update_or_create(
                airplane=instance,
                seat_class=seat_class,
                defaults={
                    "rows": seat_configuration.get(
                        "rows",
                        existing_config.rows if existing_config else 1
                    ),
                    "seats_in_row": seat_configuration.get(
                        "seats_in_row",
                        existing_config.seats_in_row if existing_config else 1
                    ),
                }
            )

        return instance


class AirplaneSeatConfigurationListSerializer(AirplaneSeatConfigurationSerializer):
    airplane_id = serializers.IntegerField(source="airplane.id")
    class Meta:
        model = AirplaneSeatConfiguration
        fields = ("id", "airplane_id", "seat_class", "rows", "seats_in_row", "capacity")


class AirplaneSeatConfigurationRetrieveSerializer(AirplaneSeatConfigurationSerializer):
    airplane = AirplaneListSerializer(read_only=True)
    class Meta:
        model = AirplaneSeatConfiguration
        fields = ("id", "airplane", "seat_class", "rows", "seats_in_row", "capacity")


class AirplaneTypeListSerializer(serializers.ModelSerializer):
    airplanes_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = AirplaneType
        fields = ("id", "name", "airplanes_total")


class AirplaneTypeRetrieveSerializer(AirplaneTypeListSerializer):
    airplane_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        source="airplanes",
    )

    class Meta:
        model = AirplaneType
        fields = ("id", "name", "airplanes_total", "airplane_ids")


# ----------- CrewMemberPosition, CrewMember serializers -----------

class CrewMemberPositionListSerializer(serializers.ModelSerializer):
    crew_members_total = serializers.IntegerField(read_only=True)
    class Meta:
        model = CrewMemberPosition
        fields = ("id", "name", "crew_members_total")


class CrewMemberPositionRetrieveSerializer(CrewMemberPositionListSerializer):
    crew_member_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, many=True, source="crew_members"
    )
    class Meta:
        model = CrewMemberPosition
        fields = ("id", "name", "crew_members_total", "crew_member_ids")


class CrewMemberListSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    position_name = serializers.SlugField(
        source="position.name", read_only=True
    )
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=CrewMemberPosition.objects.all(), source="position"
    )

    class Meta:
        model = CrewMember
        fields = (
            "id",
            "photo",
            "first_name",
            "last_name",
            "position_name",
            "position_id",
        )

    @staticmethod
    def get_photo(obj):
        return str(obj.photo.url) if obj.photo else None


class CrewMemberRetrieveSerializer(CrewMemberListSerializer):
    ...


class CrewMemberImageSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()

    class Meta:
        model = CrewMember
        fields = ("id", "photo")


# ----------- Airport, Route serializers -----------

class AirportListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    source_routes_total = serializers.IntegerField(read_only=True)
    destination_routes_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "image",
            "closest_big_city",
            "source_routes_total",
            "destination_routes_total",
        )

    @staticmethod
    def get_image(obj):
        return str(obj.image.url) if obj.image else None


class AirportRetrieveSerializer(AirportListSerializer):
    source_route_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="sources"
    )
    destination_route_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="destinations"
    )

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "image",
            "closest_big_city",
            "source_routes_total",
            "source_route_ids",
            "destination_routes_total",
            "destination_route_ids",
        )


class AirportImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = Airport
        fields = ("id", "image")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugField(
        read_only=True, source="source.closest_big_city"
    )
    destination = serializers.SlugField(
        read_only=True, source="destination.closest_big_city"
    )
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), write_only=True
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(), write_only=True
    )
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
            "source_id",
            "destination_id",
        )


    def validate(self, attrs):
        super().validate(attrs)

        source_id = attrs.get("source_id")
        destination_id = attrs.get("destination_id")

        if source_id == destination_id:
            raise serializers.ValidationError({
                "source_id": "Must be different from destination_id.",
                "destination_id": "Must be different from source_id.",
            })
        if Route.objects.filter(
                source_id=source_id, destination_id=destination_id
        ).exists():
            raise serializers.ValidationError({
                "route": "This route already exists."
            })
        return attrs

    def create(self, validated_data):
        source_id = validated_data.pop("source_id")
        destination_id = validated_data.pop("destination_id")
        return Route.objects.create(
            source=source_id, destination=destination_id, **validated_data
        )


class RouteRetrieveSerializer(RouteListSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)

    def update(self, instance, validated_data):
        instance.source = validated_data.pop(
            "source_id", instance.source
        )
        instance.destination = validated_data.pop(
            "destination_id", instance.destination
        )
        instance.save()

        return instance


# ----------- Flight, Order, Ticket serializers -----------

class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.CharField(read_only=True, source="str_route")
    route_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Route.objects.all()
    )
    airplane_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Airplane.objects.all()
    )
    crew_ids = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=CrewMember.objects.all(), many=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route_id",
            "airplane_id",
            "crew_ids",
            "base_price",
            "departure_time",
            "arrival_time",
            "route",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        flight_id = self.instance.id if self.instance else None

        if flight := Flight.objects.filter(
                airplane=attrs["airplane_id"],
                departure_time=attrs["departure_time"]
        ).exclude(id=flight_id).first():
            raise serializers.ValidationError({
                "airplane_id": f"This airplane is already scheduled "
                               f"for another flight(id:{flight.id}) at this time.",
            })

        if flight := Flight.objects.filter(
            crew__in=attrs["crew_ids"],
            departure_time=attrs["departure_time"]
        ).exclude(id=flight_id).first():
            raise serializers.ValidationError({
                "crew_ids": f"One or more crew members are already "
                            f"assigned to another flight(id:{flight.id}) at this time.",
            })

        return attrs


    def create(self, validated_data):
        crew = validated_data.pop("crew_ids")
        airplane = validated_data.pop("airplane_id")
        route = validated_data.pop("route_id")

        flight = Flight.objects.create(
            airplane=airplane,
            route=route,
            **validated_data,
        )
        flight.crew.set(crew)
        return flight


class FlightRetrieveSerializer(FlightListSerializer):
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewMemberListSerializer(read_only=True, many=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "base_price",
            "departure_time",
            "arrival_time",
            "route_id",
            "route",
            "airplane_id",
            "airplane",
            "crew_ids",
            "crew",
        )

    def update(self, instance, validated_data):
        crew = validated_data.pop("crew_ids")
        airplane = validated_data.pop("airplane_id")
        route = validated_data.pop("route_id")

        instance.base_price = validated_data.get(
            "base_price", instance.base_price
        )
        instance.departure_time = validated_data.get(
            "departure_time", instance.departure_time
        )
        instance.arrival_time = validated_data.get(
            "arrival_time", instance.arrival_time
        )

        instance.route = route
        instance.airplane = airplane
        instance.save()

        instance.crew.set(crew)

        return instance


class TicketSerializer(serializers.ModelSerializer):
    seat_class = serializers.ChoiceField(choices=SeatClass.choices)
    flight_id = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all()
    )
    route_string = serializers.CharField(read_only=True, source="flight.str_route")
    price = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "seat_class",
            "flight_id",
            "route_string",
            "price"
        )

    @staticmethod
    def get_price(obj):
        return obj.flight.calculate_ticket_price(
            seat_class=obj.seat_class,
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        ticket_id = self.instance.id if self.instance else None

        flight = attrs.get("flight_id", None)
        if not flight:
            raise serializers.ValidationError({
                "flight_id": "This field is required.",
            })

        airplane = flight.airplane
        seat_configuration = airplane.seat_configurations.filter(
            seat_class=attrs["seat_class"]
        ).first()
        if not seat_configuration:
            raise serializers.ValidationError({
                "seat_class": f"Airplane of this flight(id:{flight.id})"
                              f" does not have seat class '{attrs['seat_class']}'."
            })
        if seat_configuration.rows < attrs["row"]:
            raise serializers.ValidationError({
                "row": f"Airplane of this flight(id:{flight.id}) "
                       f"does not have row '{attrs['row']}' "
                       f"(rows: {seat_configuration.rows})."
            })
        if seat_configuration.seats_in_row < attrs["seat"]:
            raise serializers.ValidationError({
                "seat": f"Airplane of this flight(id:{flight.id}) "
                        f"does not have seat '{attrs['seat']}' "
                        f"(seats_in_row: {seat_configuration.seats_in_row})."
            })

        if Ticket.objects.filter(
            flight=flight,
            row=attrs["row"],
            seat=attrs["seat"],
            seat_class=attrs["seat_class"],
        ).exclude(id=ticket_id).exists():
            raise serializers.ValidationError({
                "ticket": "This seat is already taken."
            })

        return attrs


class TicketListSerializer(TicketSerializer):
    owner_email = serializers.CharField(read_only=True, source="order.user.email")
    flight_id = serializers.IntegerField(read_only=True, source="flight.id")

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "seat_class",
            "owner_email",
            "route_string",
            "price",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, write_only=True)
    email = serializers.CharField(read_only=True, source="user.email")
    order_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "is_paid",
            "created_at",
            "email",
            "order_price",
            "tickets",
        )

    @staticmethod
    def get_order_price(obj):
        return sum([
            ticket.flight.calculate_ticket_price(ticket.seat_class)
            for ticket in obj.tickets.all()
        ])


class OrderListSerializer(OrderSerializer):

    def create(self, validated_data):
        tickets = validated_data.pop("tickets")
        user = self.context["request"].user
        instance = Order.objects.create(
            user=user,
            **validated_data
        )

        for ticket in tickets:
            Ticket.objects.create(
                row=ticket["row"],
                seat=ticket["seat"],
                seat_class=ticket["seat_class"],
                flight=ticket["flight_id"],
                order=instance,
            )
        instance.save()
        return instance

    @staticmethod
    def validate_tickets(value):
        if len(value) < 1:
            raise serializers.ValidationError(
                "This field can not be empty."
            )


class TicketRetrieveSerializer(TicketSerializer):
    order = OrderListSerializer(read_only=True)
    flight = FlightListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "seat_class",
            "price",
            "order",
            "flight",
        )


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "is_paid",
            "created_at",
            "email",
            "order_price",
            "tickets",
        )


class OrderPaySerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "is_paid",
        )
