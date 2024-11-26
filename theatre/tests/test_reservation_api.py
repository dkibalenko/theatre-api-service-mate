from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Performance, Play, Reservation, TheatreHall
from theatre.serializers import ReservationSerializer


class AuthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall",
            rows=10,
            seats_in_row=20
        )
        self.play = Play.objects.create(
            title="Example Play",
            description="An example play description.",
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=timezone.now()
        )
        self.reservation = Reservation.objects.create(user=self.user)

    def test_get_serializer_class_list(self):
        res = self.client.get(reverse("theatre:reservation-list"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        serializer = ReservationSerializer(self.reservation)

        expected_data = [
            {
                "id": serializer.data["id"],
                "created_at": serializer.data["created_at"],
                "tickets": []
            }
        ]
        
        self.assertEqual(res.data["results"], expected_data)
