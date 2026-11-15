from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()

router.register('genres',views.GenreViewSet)
router.register('movies',views.MovieViewSet)

urlpatterns = router.urls