from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()

router.register('cinemas',views.CinemaViewSet)
router.register('showtimes',views.ShowtimeViewSet)

cinema_router = routers.NestedDefaultRouter(router,'cinemas',lookup='cinema')
cinema_router.register('auditoriums',views.AuditoriumViewSet,basename='cinema-auditoriums')

auditorium_router = routers.NestedDefaultRouter(cinema_router,'auditoriums',lookup='auditorium')
auditorium_router.register('seats',views.SeatViewSet, basename='auditorium-seats')


urlpatterns = router.urls + cinema_router.urls + auditorium_router.urls