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
admin.site.register(Play)
admin.site.register(Prop)
admin.site.register(TheatreHall)
admin.site.register(Reservation)
admin.site.register(Ticket)


class PropInline(admin.TabularInline):
    model = Prop.performance.through
    extra = 0

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    inlines = [PropInline]
    list_display = ("play", "theatre_hall", "show_time", "prop_list", "id")
    
    def prop_list(self, obj):
        return ", ".join([prop.name for prop in obj.props.all()])
    
    prop_list.short_description = "Properties"
