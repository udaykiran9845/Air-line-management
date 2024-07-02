from django.db import models
from autoslug import AutoSlugField
# Create your models here.

class airplane_type(models.Model):
    type = models.CharField(max_length=100)
    economy_seats = models.IntegerField()
    business_seats = models.IntegerField()
    first_seats = models.IntegerField()
    total_seats = models.IntegerField()
    basic_cost = models.FloatField()
    fareperkm = models.FloatField()

class airplanes(models.Model):
    type = models.CharField(max_length=100)
    plane_id = models.CharField(max_length=100)
    economy_price = models.IntegerField()
    business_price = models.IntegerField()
    first_price = models.IntegerField()


class weeklyschedule(models.Model):
    day = models.IntegerField()
    plane_id = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    arrival_day = models.IntegerField()
    distance = models.IntegerField()

