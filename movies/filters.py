from django_filters.rest_framework import FilterSet
from .models import Movie

class MovieFilter(FilterSet):
    class Meta:
        model = Movie
        fields =  {
            'duration' : ['lt','gt'],
            'age_rating' : ['iexact'],
            'genres' : ['exact'],
            'is_active' : ['iexact'],
        }