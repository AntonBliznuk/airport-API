from django.db import models


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
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
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
    distance = models.IntegerField()

    def __str__(self):
        return (
            f"{self.source.name}({self.source.closest_big_city})"
            f" -> {self.destination.name}({self.destination.closest_big_city})"
        )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["source", "destination", "distance"]