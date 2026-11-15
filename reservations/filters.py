from django_filters.rest_framework import FilterSet
from .models import Reservation

class ReservationFilter(FilterSet):
    class Meta:
        model = Reservation
        fields = {
            'showtime_id' : ['exact'],
            'status' : ['iexact'],
            'total_amount' : ['lt','gt'],
        }