from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Cinema,Auditorium,Showtime,Seat
from reservations.models import Reservation,ReservationSeat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.utils import timezone
from .serializers import CinemaSerializer,AuditoriumSerializer,SeatSerializer,ShowtimeSerializer,UpdateCinemaSerializer,UpdateAuditoriumSerializer,UpdateSeatSerializer, UpdateShowtimeSerializer
from .filters import SeatFilter,ShowtimeFilter
from .permissions import IsAdminOrReadOnly

# Create your views here.
class CinemaViewSet(ModelViewSet):
    queryset = Cinema.objects.all()
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['name','location','address']
    ordering_fields = ['created_at','updated_at']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateCinemaSerializer
        else:
            return CinemaSerializer

class AuditoriumViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Auditorium.objects.filter(cinema_id=self.kwargs['cinema_pk'])

    def get_serializer_context(self):
        return {'cinema_id': self.kwargs['cinema_pk']}

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateAuditoriumSerializer
        else:
            return AuditoriumSerializer

class SeatViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = SeatFilter
    search_fields = ['name','number']
    ordering_fields = ['price']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Seat.objects.filter(auditorium_id=self.kwargs['auditorium_pk'])

    def get_serializer_context(self):
        return {'auditorium_id' : self.kwargs['auditorium_pk']}

    def get_serializer_class(self):
            if self.request.method == 'PATCH':
                return UpdateSeatSerializer
            else:
                return SeatSerializer

class ShowtimeViewSet(ModelViewSet):
    queryset = Showtime.objects.all()
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ShowtimeFilter
    search_fields = ['name','movie__title','auditorium__name']
    ordering_fields = ['ticket_price','created_at','updated_at']
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return UpdateShowtimeSerializer
        else:
            return ShowtimeSerializer

    @action(detail=True,permission_classes=[IsAdminUser])
    def cancel(self,request,pk):
        showtime = Showtime.objects.get(id=pk)

        if showtime.status == 'COMPLETED' or showtime.start_time <= timezone.now():
            return Response({'error':'You can not cancel a show that is completed  or has started'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Showtime.objects.filter(id=pk).update(status='CANCELLED')

        Reservation.objects.filter(showtime_id=showtime.id).update(status='CANCELLED')
        ReservationSeat.objects.filter(showtime_id=showtime.id).update(status='CANCELLED')

        return Response(
            {'message': 'Showtime cancelled'},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        if Reservation.objects.filter(showtime_id = self.kwargs['pk']).exists():
            return Response({'error':'Showtime cannot be deleted since it has reservations'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

