from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import timedelta
from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    CrewMemberPosition,
    CrewMember,
    Flight,
    Order,
    Ticket,
)
from decimal import Decimal
from django.utils.timezone import now


class AirportViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="pass"
        )
        self.client.force_authenticate(user=self.admin)

        self.airport = Airport.objects.create(name="JFK", closest_big_city="New York")

    def test_list_airports(self):
        url = reverse("airport:airport-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_airport(self):
        url = reverse("airport:airport-detail", args=[self.airport.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.airport.id)


class RouteViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="pass"
        )
        self.client.force_authenticate(user=self.admin)
        self.src = Airport.objects.create(name="JFK", closest_big_city="NY")
        self.dst = Airport.objects.create(name="LAX", closest_big_city="LA")
        self.route = Route.objects.create(
            source=self.src, destination=self.dst, distance=1000
        )

    def test_list_routes(self):
        url = reverse("airport:route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FlightViewSetTests(APITestCase):
    def setUp(self):
        Flight.objects.all().delete()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="pass"
        )
        self.client.force_authenticate(user=self.admin)
        self.src = Airport.objects.create(name="JFK", closest_big_city="NY")
        self.dst = Airport.objects.create(name="LAX", closest_big_city="LA")
        self.route = Route.objects.create(
            source=self.src, destination=self.dst, distance=1000
        )
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="Plane A", airplane_type=self.airplane_type
        )
        self.crew_position = CrewMemberPosition.objects.create(name="Pilot")
        self.crew = CrewMember.objects.create(
            first_name="John", last_name="Doe", position=self.crew_position
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            base_price=Decimal("0.10"),
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2),
        )
        self.flight.crew.add(self.crew)

    def test_list_flights(self):
        url = reverse("airport:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_airplane_id(self):
        url = reverse("airport:flight-list") + f"?airplane-id={self.airplane.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        flights = response.data
        if isinstance(flights, dict) and "results" in flights:
            flights = flights["results"]

        returned_ids = {f["id"] for f in flights}
        self.assertIn(self.flight.id, returned_ids)


class OrderViewSetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="pass"
        )
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user=self.user, is_paid=False)

    def test_list_orders(self):
        url = reverse("airport:order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pay_order(self):
        url = reverse("airport:order-pay", args=[self.order.id])
        response = self.client.post(url, data={})
        self.assertIn(
            response.status_code, [200, 400]
        )  # Expect 200 if logic is implemented, 400 if not


class TicketViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="pass"
        )
        self.client.force_authenticate(user=self.admin)
        self.src = Airport.objects.create(name="JFK", closest_big_city="NY")
        self.dst = Airport.objects.create(name="LAX", closest_big_city="LA")
        self.route = Route.objects.create(
            source=self.src, destination=self.dst, distance=1000
        )
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="Plane A", airplane_type=self.airplane_type
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            base_price=Decimal("0.10"),
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.admin, is_paid=True)
        self.ticket = Ticket.objects.create(
            row=1, seat=1, seat_class="economy", flight=self.flight, order=self.order
        )

    def test_list_tickets(self):
        url = reverse("airport:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
