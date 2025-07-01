from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from cloudinary.models import CloudinaryField


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Airplane Type"
        verbose_name_plural = "Airplane Types"
        ordering = ["name"]


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

    def __str__(self):
        return f"name: {self.airplane.name} type:{self.airplane.airplane_type.name} ({self.seat_class})"

    class Meta:
        unique_together = ("airplane", "seat_class")
        verbose_name = "Airplane Seat Configuration"
        verbose_name_plural = "Airplane Seat Configurations"
        ordering = ["seat_class", "rows", "seats_in_row"]


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    image = CloudinaryField("image", blank=True, null=True)
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    def __str__(self):
        return f"{self.name} type: {self.airplane_type.name}"

    class Meta:
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"
        ordering = ["name"]


class Airport(models.Model):
    name = models.CharField(max_length=63, unique=True)
    image = CloudinaryField("image", blank=True, null=True)
    closest_big_city = models.CharField(max_length=63)

    def __str__(self):
        return f"{self.name}(city: {self.closest_big_city})"

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        ordering = ["name"]


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

    def __str__(self):
        return (
            f"{self.source.name}({self.source.closest_big_city})"
            f" -> {self.destination.name}({self.destination.closest_big_city})"
        )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["source", "destination", "distance"]


class CrewMemberPosition(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Crew Member Position"
        verbose_name_plural = "Crew Member Positions"
        ordering = ["name"]


class CrewMember(models.Model):
    photo = CloudinaryField("image", blank=True, null=True)
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    position = models.ForeignKey(
        CrewMemberPosition, on_delete=models.CASCADE, related_name="crew_members"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}(Position:{self.position.name})"

    class Meta:
        verbose_name = "Crew Member"
        verbose_name_plural = "Crew Members"
        ordering = ["first_name", "last_name"]


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
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

    @property
    def seat_class_multipliers(self) -> dict:
        return {
            SeatClass.ECONOMY: settings.ECONOMY_SEAT_CLASS_MULTIPLIER,
            SeatClass.BUSINESS: settings.BUSINESS_SEAT_CLASS_MULTIPLIER,
        }

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    def calculate_ticket_price(self, seat_class:str) -> float:
        multiplier = Decimal(str(self.seat_class_multipliers.get(seat_class, 1.0)))
        distance = Decimal(str(self.route.distance))
        price = self.base_price * distance * multiplier
        return round(float(price), 2)

    def __str__(self):
        return f"{self.route.source}({self.departure_time}) -> {self.route.destination}({str(self.arrival_time)})"

    class Meta:
        unique_together = ("airplane", "departure_time")
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ["departure_time"]


class Order(models.Model):
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")

    @property
    def price(self):
        # you can add additional logic if needed.
        return

    def pay(self):
        self.is_paid = True

    def __str__(self):
        return f"{self.user.username} -> {self.created_at} (is_paid:{self.is_paid})"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["created_at", "-is_paid"]

