from django.db import models
from .validators import validate_file_size

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
            return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.ImageField(upload_to='movies/images',blank=True, null=True,validators=[validate_file_size])
    duration = models.PositiveIntegerField()
    release_date = models.DateField()
    age_rating = models.CharField(max_length=10)
    genres = models.ManyToManyField(Genre, related_name='movies')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return self.title
