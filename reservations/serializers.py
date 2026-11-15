from rest_framework import serializers
from .models import Reservation, ReservationSeat
from django.db.models import Sum,Count, Q
from django.utils import timezone
from uuid import uuid4                                                                           
from showtimes.models import Seat,Showtime, Auditorium
from django.db import transaction
from decimal import Decimal
import logging


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id','booking_refrence','user','showtime','status','total_amount']

    user = serializers.StringRelatedField(read_only=True)
    booking_refrence = serializers.UUIDField(default=uuid4,read_only=True)
    status = serializers.CharField(read_only=True,default='PENDING')
    showtime = serializers.PrimaryKeyRelatedField(queryset = Showtime.objects.all())
    total_amount = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)

    def create(self, validated_data):
        user_id = self.context['user_id']
        showtime = self.validated_data['showtime']

        auditorium_seats = Auditorium.objects.annotate(seat_count = Count('seats')).get(id=showtime.auditorium_id)

        total_seats = auditorium_seats.seat_count

        reserved_seats = ReservationSeat.objects.filter( Q(status='ACTIVE') | Q(status='PENDING'), showtime=showtime).count()

        if total_seats <= reserved_seats:
            raise serializers.ValidationError('This Showtime is fully booked')
        elif showtime.start_time <= timezone.now() or showtime.end_time <= timezone.now():
            raise serializers.ValidationError('This showtime has already started or ended')
        elif showtime.status == 'CANCELLED':
            raise serializers.ValidationError('This showtime is Cancelled')
        return Reservation.objects.create(user_id=user_id, **validated_data)


class UpdateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id','cancelled_at','status']

    status = serializers.CharField(read_only=True,default='CANCELLED')

    def update(self, instance, validated_data):
        cancelled_at = timezone.now()
        status = 'CANCELLED'

        if self.context['showtime_status'] == 'COMPLETED' or self.context['showtime_start_time'] <= timezone.now():
            raise serializers.ValidationError("You can't cancel this reservation since showtime has either started or is completed")
        else:
            Reservation.objects.filter(id=instance.id).update(cancelled_at=cancelled_at,status=status, ** validated_data)

        ReservationSeat.objects.filter(reservation_id = instance.id).update(status='CANCELLED')

        instance.refresh_from_db()
        return instance

        

class ReservationSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationSeat
        fields = ['id','reservation','seat','showtime','status','price','seats']

    reservation = serializers.StringRelatedField(read_only=True)
    showtime = serializers.StringRelatedField(read_only=True)
    seat = serializers.PrimaryKeyRelatedField(read_only = True)
    seats = serializers.PrimaryKeyRelatedField(queryset = Seat.objects.all(),many=True, write_only=True)
    price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    status = serializers.CharField(read_only=True,default='PENDING')

    @transaction.atomic()
    def create(self, validated_data):
        reservation_id = self.context['reservation_id']
        reservation = Reservation.objects.get(id=reservation_id)

        reservation_seats = [
            ReservationSeat(reservation_id=reservation_id, showtime_id=reservation.showtime_id, seat=seat, price = seat.price)
            for seat in validated_data['seats']
        ]

        for seat in validated_data['seats']:
            if seat.auditorium_id != self.context['auditorium_id']:
                raise serializers.ValidationError('That seat is not in the showtimes auditorium')

        try:
            ReservationSeat.objects.bulk_create(reservation_seats)
        except u as e:
            Logger.error(f"Error occurred while creating reservation seats: {e}")
            raise serializers.ValidationError("Error occurred while creating reservation seats")

        price = sum((reservation_seat.price for reservation_seat in reservation_seats),Decimal(0.0))

        showtime_price = reservation.showtime.ticket_price

        total_amount = price + showtime_price

        Reservation.objects.filter(id=reservation_id).update(total_amount=total_amount)

        return reservation_seats[0]

class MpesaReservationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_digits=12, min_length=10, write_only=True)
        

class UpdateReservationSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationSeat
        fields = ['id','seat','price']

    seat = serializers.PrimaryKeyRelatedField(queryset = Seat.objects.all())
    price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)

    def update(self, instance, validated_data):
        seat = self.validated_data['seat']
        price = seat.price

        reservation = Reservation.objects.get(id=self.context['reservation_id'])

        if reservation.status == 'ACTIVE' or reservation.status == 'CANCELLED':
            raise serializers.ValidationError('You can not update the seat since your reservation is already active or was cancelled')
        elif seat.auditorium_id != self.context['auditorium_id']:
            raise serializers.ValidationError('That seat is not in the showtimes auditorium')
        else:
            ReservationSeat.objects.filter(id=instance.id).update(price=price, seat=seat)

        reservation_seats = ReservationSeat.objects.filter(reservation_id=self.context['reservation_id']).exclude(status='CANCELLED')
        seats_price = Decimal(0.00)
        
        for reservation_seat in reservation_seats:
            seats_price += reservation_seat.price

        reservation = Reservation.objects.get(id=self.context['reservation_id'])

        showtime_price = reservation.showtime.ticket_price

        total_amount = seats_price + showtime_price

        Reservation.objects.filter(id=self.context['reservation_id']).update(total_amount=total_amount)

        instance.refresh_from_db()
        return instance
        
class CancelReservationSeatSerilalizer(serializers.ModelSerializer):
    class Meta:
        model = ReservationSeat
        fields = ['id','seat','status']

    seat = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(read_only=True, default='CANCELLED')

    def update(self, instance, validated_data):
        ReservationSeat.objects.filter(id=instance.id).update(status='CANCELLED')

        reservation_seats = ReservationSeat.objects.filter(reservation_id=self.context['reservation_id']).exclude(status='CANCELLED')

        seats_price =  Decimal(0.00)
        for reservation_seat in reservation_seats:
            seats_price += reservation_seat.price

        all_reservation_seats = ReservationSeat.objects.filter(reservation_id=self.context['reservation_id'])
        if all(seat.status == 'CANCELLED' for seat in all_reservation_seats):
            Reservation.objects.filter(id=self.context['reservation_id']).update(status='CANCELLED')

        reservation=Reservation.objects.get(id=self.context['reservation_id'])

        showtime_price = reservation.showtime.ticket_price

        total_amount = seats_price + showtime_price

        Reservation.objects.filter(id=self.context['reservation_id']).update(total_amount=total_amount)

        instance.refresh_from_db()
        return instance
