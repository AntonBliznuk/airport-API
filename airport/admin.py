from django.contrib import admin

from airport.models import (
    Airplane,
    AirplaneType,
    Route,
    Airport,
    CrewMemberPosition,
    CrewMember,
    AirplaneSeatConfiguration,
    Flight,
    Order,
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
