from django.db.models import F, Count
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlayImageSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    PerformanceDetailSerializer,
    PerformanceListSerializer,
    ReservationListSerializer,
)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the movies with filters"""
        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if actors:
            actors_ids = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer
    
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter movies by title",
            ),
            OpenApiParameter(
                name="genres",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter movies by genre",
            ),
            OpenApiParameter(
                name="actors",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter movies by actors",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """ Get a list of all available movies """
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects.all()
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        )
    ).order_by("id")
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        
        return PerformanceSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset
    
    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        
        return ReservationSerializer
    
    def perform_create(self, serializer):
        """
        Sets the user field of the created Reservation to the current user
        """
        serializer.save(user=self.request.user)
