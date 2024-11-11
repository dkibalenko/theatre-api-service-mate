from django.shortcuts import render
from rest_framework import viewsets

from theatre.models import Actor, Genre
from theatre.serializers import ActorSerializer, GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
