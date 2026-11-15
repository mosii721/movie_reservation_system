from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()

router.register('profiles',views.ProfileViewSet,basename='profiles')

urlpatterns = router.urls