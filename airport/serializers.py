from rest_framework import serializers

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType,
    Airport,
    CrewMember,
    CrewMemberPosition,
    Route,
    SeatClass,
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
