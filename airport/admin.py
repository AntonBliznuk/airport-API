from django.contrib import admin

from airport.models import (
    Airplane,
    AirplaneSeatConfiguration,
    AirplaneType,
    Airport,
    CrewMember,
    CrewMemberPosition,
    Flight,
    Order,
    Route,
    Ticket,
)

admin.site.register(AirplaneType)
admin.site.register(AirplaneSeatConfiguration)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(CrewMemberPosition)
admin.site.register(CrewMember)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)
