from django_filters.rest_framework import FilterSet
from .models import Seat,Showtime

class SeatFilter(FilterSet):
    class Meta:
        model = Seat
        fields = {
            'price' : ['lt','gt'],
            'row' : ['iexact'],
            'seat_type' : ['iexact']
        }

class ShowtimeFilter(FilterSet):
    class Meta:
        model = Showtime
        fields = {
            'movie_id': ['exact'],
            'auditorium_id': ['exact'],
            'ticket_price': ['lt','gt'],
            'status': ['iexact']
        }