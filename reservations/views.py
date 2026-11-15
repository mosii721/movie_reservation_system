from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin
from .models import ReservationSeat,Reservation
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAuthenticated
from .serializers import ReservationSeatSerializer,ReservationSerializer, UpdateReservationSerializer, UpdateReservationSeatSerializer, CancelReservationSeatSerilalizer, MpesaReservationSerializer
from .filters import ReservationFilter
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
import requests
from decouple import config
from django.utils import timezone
import base64



# Create your views here.
class ReservationViewSet(CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,GenericViewSet):
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = ['showtime__name','booking_refrence']
    ordering_fields = ['total_amount','created_at','cancelled_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.all()
        else:
            return Reservation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateReservationSerializer
        else:
            return ReservationSerializer

    def get_serializer_context(self):
            if 'pk' in self.kwargs:
                reservation = Reservation.objects.get(id=self.kwargs['pk'])
                if self.request.method == 'PUT':
                    showtime_status = reservation.showtime.status
                    showtime_start_time = reservation.showtime.start_time
                    return {'user_id': self.request.user.id,'showtime_status':showtime_status, 'showtime_start_time':showtime_start_time}
                
            return {'user_id': self.request.user.id,'user_staff':self.request.user.is_staff}

    @action(detail=True,permission_classes=[IsAuthenticated],methods=['POST'])
    def mpesa_payment(self,request,pk):
        serializer = MpesaReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        consumer_key = config('CONSUMER_KEY')
        consumer_secret = config('CONSUMER_SECRET')
        credentials = f'{consumer_key}:{consumer_secret}'
        shortcode = config('BUSINESS_SHORT_CODE')
        passkey = config('PASSKEY')
        timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
        password = f'{shortcode}{passkey}{timestamp}'
        encoded_password = base64.b64encode(password.encode()).decode()
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        reservation = Reservation.objects.get(id=pk)
        amount = int(reservation.total_amount)
        partyA = serializer.validated_data['phone_number']
        refrence= f'{reservation.id}:{reservation.booking_refrence}'
    
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        auth_response = requests.get('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
                                    headers=auth_headers)
    
        auth_body = auth_response.json()
        access_token = auth_body['access_token']
    
        payload = {
            "BusinessShortCode":config('BUSINESS_SHORT_CODE'),
            "Password":encoded_password,
            "Timestamp":timestamp,
            "TransactionType":config('TRANSACTION_TYPE'),
            "Amount":amount,
            "PartyA":partyA,
            "PartyB":config('BUSINESS_SHORT_CODE'),
            "PhoneNumber":partyA,
            "CallBackURL": f"{config('BASE_URL')}/reservations/reservation/{reservation.id}/mpesa_callback/",
            "AccountReference":refrence,
            "TransactionDesc": "Movie booking"
        }
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
            }
        response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',json=payload, headers=headers)
        body = response.json()
        return Response({"message":"Mpesa payment endpoint"})
        

class ReservationSeatViewSet(CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,GenericViewSet):
    serializer_class = ReservationSeatSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['showtime_id','status','seat']
    search_fields = ['showtime__name','reservation__booking_refrence','seat__name','seat__number']
    ordering_fields = ['price','created_at']
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return ReservationSeat.objects.filter(reservation_id=self.kwargs['reservation_pk'])

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateReservationSeatSerializer
        elif self.request.method == 'PATCH':
            return CancelReservationSeatSerilalizer
        else:
            return ReservationSeatSerializer
    
    def get_serializer_context(self):
        reservation = Reservation.objects.get(id=self.kwargs['reservation_pk'])
        auditorium_id = reservation.showtime.auditorium.id
        return {'reservation_id': self.kwargs['reservation_pk'], 'auditorium_id':auditorium_id}
    

@api_view(['POST'])
def mpesa_callback(request,pk):
    print("MPESA CALLBACK RECEIVED:", request.data)
    result_code = request.data['Body']['stkCallback']['ResultCode']
    if result_code == 0:
            Reservation.objects.filter(id=pk).update(status='COMPLETED')
    print(result_code)

    return Response({"message": "Callback received"})
  





