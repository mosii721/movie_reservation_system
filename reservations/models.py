from django.db import models
from django.conf import settings
from uuid import uuid4
from django.db.models import Q
from django.db.models import UniqueConstraint
from showtimes.models import Showtime, Seat

RESERVATION_STATUS = [
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled')
]

RESERVATION_SEAT_STATUS = [
    ('PENDING', 'Pending'),
    ('ACTIVE', 'Active'),
    ('CANCELLED', 'Cancelled')
]

# Create your models here.
class Reservation(models.Model):
    booking_refrence = models.UUIDField(default=uuid4,unique=True,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(choices=RESERVATION_STATUS,default='PENDING')
    total_amount = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.booking_refrence)

class ReservationSeat(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name='reservations_seats')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='reservations_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='reservations_seats')
    status = models.CharField(choices=RESERVATION_SEAT_STATUS,default='PENDING')
    price = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [ models.UniqueConstraint(
            fields=["showtime","seat"], 
            condition=Q(status="ACTIVE") | Q(status="PENDING"), 
            name="unique_seat_reservation"
            )]