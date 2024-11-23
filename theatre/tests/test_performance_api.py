from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Performance, Prop, TheatreHall, Play
from theatre.serializers import PerformanceDetailSerializer


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
        "show_time": timezone.now(),
        "play": sample_play(),
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


class UnauthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        

    def test_performance_string_representation(self):
        performance = sample_performance()
        self.assertEqual(
            str(performance),
            f"{performance.play} at {performance.theatre_hall} "
            f"at {performance.show_time}"
        )

    def test_retrieve_performances_unauthenticated(self):
        """Test that authentication is required for retrieving performances"""
        res = self.client.get(reverse("theatre:performance-list"))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.prop1 = Prop.objects.create(name="Prop 1")
        self.prop2 = Prop.objects.create(name="Prop 2")
        self.performance = sample_performance()
        self.performance.props.set([self.prop1, self.prop2])

    def test_update_performance_basic_fields(self):
        self.assertEqual(
            self.performance.show_time.date(),
            timezone.now().date()
        )

        update_data = {"show_time": "2025-01-01T10:00:00Z", "props": []}

        serializer = PerformanceDetailSerializer(
            instance=self.performance,
            data=update_data,
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.performance.refresh_from_db()
        self.assertEqual(
            self.performance.show_time.isoformat(),
            "2025-01-01T10:00:00+00:00"
        )
        self.assertEqual(self.performance.props.count(), 0)
