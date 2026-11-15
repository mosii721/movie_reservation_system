from django.contrib import admin
from django.db.models import Count, Q
from . import models

# Register your models here.

class AuditoriumItemInline(admin.TabularInline):
    model = models.Auditorium

@admin.register(models.Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ['name','location','address','is_active','auditorium_count']
    ordering = ['name','location','address']
    list_editable = ['is_active']
    search_fields = ['name','location','address','is_active']
    list_filter = ['location','is_active']
    inlines = [AuditoriumItemInline]
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            auditorium_count = Count('auditoriums')
        )

    def auditorium_count(self,cinema):
        return cinema.auditorium_count




@admin.register(models.Auditorium)
class AuditoriumAdmin(admin.ModelAdmin):
    list_display = ['cinema__name','name','is_active','seat_count','reserved_seat_count']
    ordering = ['name','cinema__name']
    list_editable = ['is_active']
    list_select_related = ['cinema']
    search_fields = ['cinema__name','name','is_active']
    list_filter = ['cinema__name','is_active']
    autocomplete_fields = ['cinema']
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            seat_count = Count('seats'),
            reserved_seat_count = Count('seats__reservations_seats',
                                        filter=Q(seats__reservations_seats__status='PENDING') | Q(seats__reservations_seats__status='ACTIVE'))
        )

    def seat_count(self,auditorium):
        return auditorium.seat_count

    def reserved_seat_count(self,auditorium):
        return auditorium.reserved_seat_count



@admin.register(models.Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['auditorium__name','name','row','number']
    ordering = ['auditorium__name','name','row','number']
    list_select_related = ['auditorium']
    search_fields = ['auditorium__name','name','row','number']
    list_filter = ['auditorium__name','row']
    list_per_page = 10


@admin.register(models.Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ['movie__title','auditorium__name','name','start_time','end_time','ticket_price','status','created_at','reservation_count']
    ordering = ['movie__title','auditorium__name','start_time','end_time','ticket_price']
    list_editable = ['start_time','ticket_price','status']
    list_select_related = ['movie','auditorium']
    search_fields = ['movie__title','auditorium__name','name','status']
    list_filter = ['movie__title','auditorium__name','status']
    actions = ['complete_showtime']
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            reservation_count = Count('reservations',
            filter = Q(reservations__status = 'ACTIVE'))                                                                    
        )

    def reservation_count(self,showtime):
        return showtime.reservation_count

    @admin.action(description='cancel showtime status')
    def cancel_showtime(self,request,queryset):
        update_status = queryset.update(status = 'CANCELLED')
        self.message_user(request, f'{update_status} showtime is now cancelled')

    @admin.action(description='complete showtime status')
    def complete_showtime(self,request,queryset):
        update_status = queryset.update(status = 'COMPLETED')
        self.message_user(request, f'{update_status} showtime is now completed')