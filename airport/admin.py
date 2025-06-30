from django.contrib import admin

from airport.models import Airplane, AirplaneType, Route, Airport

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Route)
