from rest_framework import  serializers
from .models import Cinema,Auditorium,Seat,Showtime
from movies.models import Movie
from datetime import timedelta
from django.utils import timezone

class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ['id','name','location','address','is_active']

class UpdateCinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ['id','name','is_active']

class AuditoriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditorium
        fields = ['id','name','cinema','is_active']

    cinema = serializers.StringRelatedField(read_only=True)

    def create(self, validated_data):
        cinema_id = self.context['cinema_id']
        return Auditorium.objects.create(cinema_id=cinema_id, **validated_data)

class UpdateAuditoriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditorium
        fields = ['id','name','is_active']

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id','name','auditorium','row','number','seat_type','price']

    auditorium = serializers.StringRelatedField(read_only=True)

    def create(self, validated_data):
        auditorium_id = self.context['auditorium_id']
        return Seat.objects.create(auditorium_id=auditorium_id, **validated_data)

class UpdateSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id','name','seat_type','price']

class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['id','name','auditorium','movie','ticket_price','start_time','end_time','status']

    auditorium = serializers.PrimaryKeyRelatedField(queryset = Auditorium.objects.all())
    movie = serializers.PrimaryKeyRelatedField(queryset = Movie.objects.all())
    status = serializers.CharField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        if data['auditorium'].is_active == False or data['movie'].is_active == False:
            raise serializers.ValidationError('You cant put this showtime in this auditorium since its not active or the movie is not active')
        return data

    def create(self, validated_data):
        start_time = self.validated_data['start_time']
        movie = self.validated_data['movie']
        movie_duration = movie.duration
        end_time = start_time + timedelta(minutes=movie_duration)
        return Showtime.objects.create(end_time=end_time, **validated_data)
    
class UpdateShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['id','ticket_price','start_time','end_time']

    end_time = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        start_time = self.validated_data['start_time']
        showtime = Showtime.objects.get(id=instance.id)
        movie_duration = showtime.movie.duration

        end_time = start_time + timedelta(minutes=movie_duration)

        if instance.status == 'COMPLETED' or instance.start_time <= timezone.now():
            raise serializers.ValidationError('You can not update this showtime since it is completed or has already begun')
        else:
            Showtime.objects.filter(id=instance.id).update(end_time=end_time, **validated_data)

        instance.refresh_from_db()
        return instance