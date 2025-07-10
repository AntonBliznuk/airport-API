from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    AirplaneSeatConfiguration,
    SeatClass,
    CrewMemberPosition,
    CrewMember,
    Flight,
    Order,
    Ticket,
)


class ModelStrTests(TestCase):
    def setUp(self):
        self.airplane_type = AirplaneType.objects.create(name="Boeing 747")
        self.airplane = Airplane.objects.create(
            name="SkyMaster", airplane_type=self.airplane_type
        )
        self.airport1 = Airport.objects.create(name="JFK", closest_big_city="New York")
        self.airport2 = Airport.objects.create(
            name="LAX", closest_big_city="Los Angeles"
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=1000
        )
        self.config = AirplaneSeatConfiguration.objects.create(
            airplane=self.airplane,
            seat_class=SeatClass.ECONOMY,
            rows=10,
            seats_in_row=6,
        )
        self.position = CrewMemberPosition.objects.create(name="Pilot")
        self.crew_member = CrewMember.objects.create(
            first_name="John", last_name="Doe", position=self.position
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            base_price=Decimal("0.10"),
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2),
        )
        self.flight.crew.add(self.crew_member)
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="pass1234"
        )
        self.order = Order.objects.create(user=self.user, is_paid=False)
        self.ticket = Ticket.objects.create(
            row=1,
            seat=2,
            seat_class=SeatClass.ECONOMY,
            flight=self.flight,
            order=self.order,
        )

    def test_airplane_type_str(self):
        self.assertEqual(str(self.airplane_type), "Boeing 747")

    def test_airplane_str(self):
        self.assertEqual(str(self.airplane), "SkyMaster (type: Boeing 747)")

    def test_airport_str(self):
        self.assertEqual(str(self.airport1), "JFK(city: New York)")

    def test_route_str(self):
        expected = "JFK(New York) -> LAX(Los Angeles)"
        self.assertEqual(str(self.route), expected)

    def test_airplane_seat_config_str(self):
        expected = "name: SkyMaster type:Boeing 747 (economy)"
        self.assertEqual(str(self.config), expected)

    def test_crew_member_position_str(self):
        self.assertEqual(str(self.position), "Pilot")

    def test_crew_member_str(self):
        self.assertEqual(str(self.crew_member), "John Doe(Position:Pilot)")

    def test_flight_str(self):
        expected = (
            f"{self.route.source} "
            f"({self.flight.departure_time.strftime('%Y-%m-%d %H:%M')}) ->"
            f" {self.route.destination} "
            f"({self.flight.arrival_time.strftime('%Y-%m-%d %H:%M')})"
        )
        self.assertEqual(str(self.flight), expected)

    def test_order_str(self):
        expected = (
            f"{self.user.email} -> "
            f"{self.order.created_at.strftime('%Y-%m-%d %H:%M')} (is_paid:False)"
        )
        self.assertEqual(str(self.order), expected)

    def test_ticket_str(self):
        expected = f"(row:1, seat:2, seat_class:economy) -> {self.flight.route}"
        self.assertEqual(str(self.ticket), expected)
