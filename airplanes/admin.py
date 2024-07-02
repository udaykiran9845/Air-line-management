from django.contrib import admin
from .models import airplanes,airplane_type,weeklyschedule

# Register your models here.

admin.site.register(airplane_type)
admin.site.register(airplanes)
admin.site.register(weeklyschedule)
