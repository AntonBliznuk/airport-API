from django.contrib import admin

from airport.models import Airplane, AirplaneType


admin.site.register(AirplaneType)
admin.site.register(Airplane)
