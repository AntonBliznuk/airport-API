from django.db import models
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


class Airplane(models.Model):
    name = models.CharField(max_length=63)
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
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name}(seats:{self.capacity()}, type: {self.airplane_type.name})"

    class Meta:
        verbose_name = "Airplane"
        verbose_name_plural = "Airplanes"
        ordering = ["name", "rows", "seats_in_row"]


class Airport(models.Model):
    name = models.CharField(max_length=63, unique=True)
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
