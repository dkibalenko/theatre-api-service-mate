from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Performance, TheatreHall, Play


def sample_play(**params):
    defaults = {
        "title": "Test title play",
        "description": "Test play description"
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Test theatre hall", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


class UnauthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        

    def test_performance_string_representation(self):
        performance = sample_performance(play=sample_play())
        self.assertEqual(
            str(performance),
            f"{performance.play} at {performance.theatre_hall} "
            f"at {performance.show_time}"
        )

    def test_retrieve_performances_unauthenticated(self):
        """Test that authentication is required for retrieving performances"""
        res = self.client.get(reverse("theatre:performance-list"))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
