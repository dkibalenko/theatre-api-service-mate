import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


def play_image_file_path(instance, filename) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/plays/", filename)


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, blank=True)
    actors = models.ManyToManyField(Actor, blank=True)
    image = models.ImageField(null=True, upload_to=play_image_file_path)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self) -> str:
        return f"{self.play} at {self.theatre_hall} at {self.show_time}"


class Prop(models.Model):
    name = models.CharField(max_length=255)
    performance = models.ManyToManyField(
        Performance,
        blank=True,
        related_name="props"
    )

    def __str__(self) -> str:
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        unique_together = ["row", "seat", "performance"]
        ordering = ["row", "seat"]

    @staticmethod
    def validate_ticket(row, seat, theatre_hall, error_to_raise) -> None:
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {theatre_hall_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        """
        Validates that the ticket's row and seat are within the range
        defined by its performance's theatre hall.

        Raises a ValidationError if the ticket's row or seat are out of range.
        """

        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"
