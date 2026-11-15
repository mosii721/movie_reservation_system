from django.contrib import admin
from django.db.models import Count, Q
from . import models

# Register your models here.
@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['booking_refrence','user__username','showtime__name','status','total_amount','created_at','cancelled_at','reserved_seats_count']
    ordering = ['booking_refrence','total_amount','created_at','cancelled_at']
    list_editable = ['status']
    list_select_related = ['showtime','user']
    search_fields = ['booking_refrence','user__username','showtime__name','status']
    list_filter = ['user__username','showtime__name','status','created_at']
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            reserved_seats_count = Count('reservations_seats',
                                           filter = Q(reservations_seats__status = 'ACTIVE'))
        )

    def reserved_seats_count(self,reservation):
        return reservation.reserved_seats_count

@admin.register(models.ReservationSeat)
class ReservationSeatAdmin(admin.ModelAdmin):
    list_display = ['reservation__booking_refrence','showtime__name','seat__name','status','price','created_at']
    ordering = ['seat__name','price','created_at']
    list_editable = ['status']
    list_select_related = ['reservation','showtime','seat']
    search_fields = ['reservation__booking_refrence','showtime__name','seat__name','status']
    list_filter = ['reservation__booking_refrence','showtime__name','seat__name','status']
    list_per_page = 10