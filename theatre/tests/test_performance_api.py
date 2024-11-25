import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError

from theatre.models import Performance, Prop, TheatreHall, Play
from theatre.serializers import (
    PerformanceDetailSerializer,
    PerformanceSerializer
)

PERFORMANCE_LIST_URL = reverse("theatre:performance-list")


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

    def test_update_performance_props(self):
        update_data = {
            "show_time": self.performance.show_time.isoformat(),
            "props": [{"name": "Updated Prop 1"}, {"name": "Updated Prop 2"}]}

        serializer = PerformanceDetailSerializer(
            instance=self.performance,
            data=update_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.performance.refresh_from_db()
        self.assertEqual(self.performance.props.count(), 2)
        self.assertEqual(
            {prop.name for prop in self.performance.props.all()},
            {"Updated Prop 1", "Updated Prop 2"}
        )

    def test_update_performance_transaction_integrity(self):
        # Update data with valid props
        update_data = {
            "show_time": self.performance.show_time.isoformat(),
            "props": [{"name": "Valid Prop"}]
        }

        serializer = PerformanceDetailSerializer(
            instance=self.performance,
            data=update_data,
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # Ensure props are updated
        self.performance.refresh_from_db()
        self.assertEqual(self.performance.props.count(), 1)

        # Update data with invalid props to trigger rollback
        update_data = {
            "show_time": "invalid-date",
            "props": [{"name": "Another Prop"}]}
        serializer = PerformanceDetailSerializer(
            instance=self.performance,
            data=update_data,
            partial=True
        )
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Ensure previous valid update is not rolled back
        self.performance.refresh_from_db()
        self.assertEqual(self.performance.props.count(), 1)
        self.assertEqual(self.performance.props.first().name, "Valid Prop")


class AuthenticatedPerformanceViewSetApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.play1 = sample_play(title="Play title 1")
        self.play2 = sample_play(title="Play title 2")
        self.performances = [
            sample_performance(
                show_time=f"2024-01-0{_} 12:00:00",
                play=play
            )
            for _, play in zip(
                range(1, 4), 
                [self.play1, self.play1, self.play2]
            )
        ]

    def test_get_queryset_no_filtering(self):
        res = self.client.get(PERFORMANCE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_get_queryset_filter_by_date(self):
        date = "2024-01-01"
        res = self.client.get(PERFORMANCE_LIST_URL, data={"date": date})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.performances[0].id)

    def test_get_queryset_filter_by_play_id(self):
        play_id = self.play1.id
        res = self.client.get(PERFORMANCE_LIST_URL, data={"play": play_id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]["id"], self.performances[0].id)
        self.assertEqual(res.data[1]["id"], self.performances[1].id)

    def test_get_queryset_filter_by_both_date_and_play_id(self):
        date = "2024-01-02"
        play_id = self.play1.id
        res = self.client.get(
            PERFORMANCE_LIST_URL,
            data={"date": date, "play": play_id}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.performances[1].id)

    def test_serialzer_class_retrieve_action(self):
        url = reverse(
            "theatre:performance-detail",
            args=[self.performances[0].id]
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = PerformanceDetailSerializer(self.performances[0])

        response_data = res.data
        serializer_data = serializer.data

        response_show_time = datetime.datetime.strptime(
            response_data["show_time"],
            "%Y-%m-%dT%H:%M:%SZ"
        )
        serializer_show_time = datetime.datetime.strptime(
            serializer_data["show_time"],
            "%Y-%m-%d %H:%M:%S"
        )

        self.assertEqual(response_show_time, serializer_show_time)
        del response_data["show_time"]
        del serializer_data["show_time"]
        self.assertEqual(response_data, serializer_data)

    def test_get_serializer_class_update_action(self):
        url = reverse(
            "theatre:performance-detail",
            kwargs={"pk": self.performances[0].id}
        )
        data = {
            "show_time": "2024-01-04 12:00:00",
            "props": [{"name": "Updated Prop 1"}, {"name": "Updated Prop 2"}]
        }
        res = self.client.put(url, data, format="json")
        performance = Performance.objects.get(id=self.performances[0].id)
        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_serializer_class_create_action(self):
        data = {
            "show_time": "2024-01-05 12:00:00",
            "play": 1,
            "theatre_hall": 1
        }
        res = self.client.post(PERFORMANCE_LIST_URL, data, format="json")
        performance = Performance.objects.get(show_time="2024-01-05 12:00:00")
        serializer = PerformanceSerializer(performance)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
