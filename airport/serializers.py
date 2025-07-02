from rest_framework import serializers

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType,
    SeatClass,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSeatConfigurationSerializer(serializers.ModelSerializer):
    seat_class = serializers.ChoiceField(choices=SeatClass.choices)

    class Meta:
        model = AirplaneSeatConfiguration
        fields = ("seat_class", "rows", "seats_in_row", "capacity")


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

    @staticmethod
    def get_image(obj):
        return str(obj.image.url) if obj.image else None

    @staticmethod
    def validate_seat_configurations(value):
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
            "seat_configurations"
        )


class AirplaneListSerializer(AirplaneSerializer):
    seats = serializers.SerializerMethodField()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "image",
            "airplane_type_name",
            "seats",
            "airplane_type_id",
            "seat_configurations"
        )

    @staticmethod
    def get_seats(obj):
        result = {
            conf.seat_class: conf.capacity
            for conf in obj.seat_configurations.all()
        }
        result["total"] = sum(result.values())
        return result

    def create(self, validated_data):
        seat_configurations = validated_data.pop("seat_configurations")
        instance = Airplane.objects.create(**validated_data)

        for conf in seat_configurations:
            AirplaneSeatConfiguration.objects.create(
                seat_class=conf["seat_class"],
                rows=conf["rows"],
                seats_in_row=conf["seats_in_row"],
                airplane=instance,
            )
        instance.save()
        return instance


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
