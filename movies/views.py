from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from .models import Genre, Movie
from .serializers import GenreSerializer, MovieSerializer
from .filters import MovieFilter
from .permissions import IsAdminOrReadOnly

# Create your views here.
class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]

class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = MovieFilter
    search_fields = ['title']
    ordering_fields = ['created_at','updated_at','release_date','duration']
    permission_classes = [IsAdminOrReadOnly]

