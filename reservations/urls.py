from rest_framework_nested import routers
from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('reservation/<int:pk>/mpesa_callback/', views.mpesa_callback, name='mpesa-callback'),
]

router = routers.DefaultRouter()

router.register('reservations',views.ReservationViewSet,basename='reservations')


reservation_router = routers.NestedDefaultRouter(router,'reservations',lookup='reservation')
reservation_router.register('reservation-seats',views.ReservationSeatViewSet,basename='reservation-reservation_seats')

urlpatterns = router.urls + reservation_router.urls + urlpatterns