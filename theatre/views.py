from django.shortcuts import render
from rest_framework import viewsets

from theatre.models import Actor, Genre, Play
from theatre.serializers import ActorSerializer, GenreSerializer, PlaySerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genre", "actors")
    serializer_class = PlaySerializer