from django.urls import path, include
from rest_framework import routers

from theatre.views import ActorViewSet, GenreViewSet, PlayViewSet, TheatreHallViewSet

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("theatre-halls", TheatreHallViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "theatre"
