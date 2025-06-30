from django.contrib import admin

from airport.models import Airplane, AirplaneType, Route, Airport, CrewMemberPosition, CrewMember

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(CrewMemberPosition)
admin.site.register(CrewMember)
