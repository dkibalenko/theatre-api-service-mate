from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.test import APIClient

from theatre.models import Play, Ticket, Performance, Reservation, TheatreHall


class AuthenticatedTicketApiTests(TestCase):
    """Test the API for tickets"""

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

    def test_validate_ticket(self):
        # Valid ticket
        try:
            Ticket.validate_ticket(
                row=5,
                seat=10,
                theatre_hall=self.theatre_hall,
                error_to_raise=ValidationError
            )
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for valid ticket.")
        # Invalid row
        with self.assertRaises(ValidationError) as cm:
            Ticket.validate_ticket(11, 10, self.theatre_hall, ValidationError)
            self.assertIn(
                "row number must be in available range",
                str(cm.exception)
            )
        # Invalid seat
        with self.assertRaises(ValidationError) as cm:
            Ticket.validate_ticket(5, 21, self.theatre_hall, ValidationError)
            self.assertIn(
                "seat number must be in available range",
                str(cm.exception)
            )

    def test_clean_method(self):
        # Valid ticket
        ticket = Ticket(
            row=5,
            seat=10,
            performance=self.performance,
            reservation=self.reservation)
        try:
            ticket.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for valid ticket.")

        # Invalid ticket
        ticket = Ticket(
            row=11,
            seat=10,
            performance=self.performance,
            reservation=self.reservation)
        with self.assertRaises(ValidationError) as cm:
            ticket.clean()
        self.assertIn(
            "row number must be in available range",
            str(cm.exception)
        )

    def test_save_method(self):
        # Valid ticket
        ticket = Ticket(
            row=5,
            seat=10,
            performance=self.performance,
            reservation=self.reservation)
        try:
            ticket.save()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly \
                    during save for valid ticket.")

        # Invalid ticket
        ticket = Ticket(
            row=11,
            seat=10,
            performance=self.performance,
            reservation=self.reservation)
        with self.assertRaises(ValidationError) as cm:
            ticket.save()
        self.assertIn(
            "row number must be in available range",
            str(cm.exception)
        )

    def test_ticket_string_representation(self):
        ticket = Ticket(
            row=5,
            seat=10,
            performance=self.performance,
            reservation=self.reservation
        )
        expected_string = f"{str(self.performance)} (row: 5, seat: 10)"
        self.assertEqual(str(ticket), expected_string)
