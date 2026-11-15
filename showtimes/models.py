from django.db import models
from movies.models import Movie

SEAT_TYPE = [
    ('VIP','Vip'),
    ('STANDARD','Standard'),
]

SHOWTIME_STATUS = [
    ('SCHEDULED','Scheduled'),
    ('COMPLETED','Completed'),
    ('CANCELLED','Cancelled')
]


# Create your models here.
class Cinema(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return self.name

class Auditorium(models.Model):
    name = models.CharField(max_length=255)
    cinema = models.ForeignKey(Cinema,on_delete=models.CASCADE,related_name='auditoriums')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together=[['name','cinema']]

    def __str__(self):
        return self.name

class Seat(models.Model):
    name = models.CharField(max_length=255)
    auditorium = models.ForeignKey(Auditorium,on_delete=models.CASCADE,related_name='seats')
    row = models.CharField(max_length=5)
    number = models.PositiveIntegerField()
    seat_type = models.CharField(choices=SEAT_TYPE, default='STANDARD')
    price = models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        unique_together=[['row','number','auditorium']]

    def __str__(self):
            return self.name

class Showtime(models.Model):
    name = models.CharField(max_length=255,unique=True)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='showtime')
    auditorium = models.ForeignKey(Auditorium,on_delete=models.CASCADE,related_name='showtime')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(choices=SHOWTIME_STATUS, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True )

    def __str__(self):
            return self.name

