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

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Performance)
admin.site.register(Play)
admin.site.register(Prop)
admin.site.register(TheatreHall)
admin.site.register(Reservation)
admin.site.register(Ticket)
