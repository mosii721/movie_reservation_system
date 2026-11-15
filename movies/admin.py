from django.contrib import admin
from django.utils.html import format_html
from . import models

# Register your models here.
@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    ordering = ['name']
    search_fields = ['name']
    list_per_page = 10

@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title','description','duration','release_date','age_rating','is_active']
    list_editable = ['is_active']
    ordering = ['title','duration','release_date']
    search_fields = ['title','duration','release_date','age_rating']
    list_per_page = 10
    readonly_fields = ['thumbnail']

    def thumbnail(self,instance):
        if instance.poster.name != '':
            return format_html('<img_src="{}" class="thumbnail" />',instance.poster.url)
        return ''

    class Media:
        css = {
            'all':['movies/styles.css']
        }