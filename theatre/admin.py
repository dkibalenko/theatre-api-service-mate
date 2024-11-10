from django.contrib import admin

from theatre.models import (
    Actor,
    Genre,
    Performance,
    Play,
    Prop,
    TheatreHall,
    Reservation,
    Ticket,
)

admin.register(Actor)
admin.register(Genre)
admin.register(Performance)
admin.register(Play)
admin.register(Prop)
admin.register(TheatreHall)
admin.register(Reservation)
admin.register(Ticket)
