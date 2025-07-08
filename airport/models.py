from decimal import Decimal

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name = "Airplane Type"
        verbose_name_plural = "Airplane Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SeatClass(models.TextChoices):
    ECONOMY = "economy", "Economy"
    BUSINESS = "business", "Business"


class AirplaneSeatConfiguration(models.Model):
    airplane = models.ForeignKey(
        "Airplane", on_delete=models.CASCADE, related_name="seat_configurations"
    )
    seat_class = models.CharField(max_length=10, choices=SeatClass.choices)
    rows = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500)
        ]
    )
    seats_in_row = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["airplane", "seat_class"], name="unique_seat_class_per_airplane"
            )
        ]
        verbose_name = "Airplane Seat Configuration"
        verbose_name_plural = "Airplane Seat Configurations"
        ordering = ["seat_class", "rows", "seats_in_row"]

    def __str__(self):
        return (
            f"name: {self.airplane.name}"
            f" type:{self.airplane.airplane_type.name} ({self.seat_class})"
        )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    image = CloudinaryField("image", blank=True, null=True)
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    class Meta:
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (type: {self.airplane_type.name})"


class Airport(models.Model):
    name = models.CharField(max_length=63, unique=True)
    image = CloudinaryField("image", blank=True, null=True)
    closest_big_city = models.CharField(max_length=63)

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}(city: {self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="sources"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destinations"
    )
    distance = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        constraints = [
            UniqueConstraint(
                fields=["source", "destination"], name="unique_source_destination"
            )
        ]
        ordering = ["source", "destination", "distance"]

    def __str__(self):
        return (
            f"{self.source.name}({self.source.closest_big_city})"
            f" -> {self.destination.name}({self.destination.closest_big_city})"
        )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination must be different.")


class CrewMemberPosition(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name = "Crew Member Position"
        verbose_name_plural = "Crew Member Positions"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    photo = CloudinaryField("image", blank=True, null=True)
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    position = models.ForeignKey(
        CrewMemberPosition, on_delete=models.CASCADE, related_name="crew_members"
    )

    class Meta:
        verbose_name = "Crew Member"
        verbose_name_plural = "Crew Members"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}(Position:{self.position.name})"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    crew = models.ManyToManyField(CrewMember, related_name="flights")
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.10"),
        validators=[
            MinValueValidator(Decimal("0.01")),
        ]
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["airplane", "departure_time"],
                name="unique_airplane_departure_time"
            )
        ]
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ["departure_time"]

    def __str__(self):
        return (
            f"{self.route.source} "
            f"({self.departure_time.strftime('%Y-%m-%d %H:%M')}) ->"
            f" {self.route.destination} "
            f"({self.arrival_time.strftime('%Y-%m-%d %H:%M')})"
        )

    @property
    def seat_class_multipliers(self) -> dict:
        return {
            SeatClass.ECONOMY: settings.ECONOMY_SEAT_CLASS_MULTIPLIER,
            SeatClass.BUSINESS: settings.BUSINESS_SEAT_CLASS_MULTIPLIER,
        }

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    @property
    def str_route(self):
        return (
            f"{self.route.source.name}({self.route.source.closest_big_city}) ->"
            f" {self.route.destination.name}({self.route.destination.closest_big_city})"
        )


    def calculate_ticket_price(self, seat_class:str) -> float:
        multiplier = Decimal(str(self.seat_class_multipliers.get(seat_class, 1.0)))
        distance = Decimal(str(self.route.distance))
        price = self.base_price * distance * multiplier
        return round(float(price), 2)


class Order(models.Model):
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="orders"
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["created_at", "-is_paid"]

    def __str__(self):
        return (
            f"{self.user.email} -> "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')} (is_paid:{self.is_paid})"
        )

    @property
    def price(self):
        # you can add additional logic if needed.
        return

    def pay(self):
        self.is_paid = True


class Ticket(models.Model):
    row = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    seat = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    seat_class = models.CharField(
        max_length=10,
        choices=SeatClass.choices,
    )
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["order__created_at", "order"]
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "seat_class", "flight"],
                name="unique_row_seat_seat_class_flight"
            )
        ]

    def __str__(self):
        return (
            f"(row:{self.row}, "
            f"seat:{self.seat}, "
            f"seat_class:{self.seat_class})"
            f" -> {self.flight.route}"
        )
