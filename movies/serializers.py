from rest_framework import serializers
from .models import Genre,Movie

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster', 'description','duration','release_date','age_rating','is_active','genres']

    genres = serializers.PrimaryKeyRelatedField(queryset = Genre.objects.all(),many=True)
