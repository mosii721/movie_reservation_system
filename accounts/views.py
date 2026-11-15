from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin
from .models import Profile
from .serializers import ProfileSerializer

# Create your views here.
class ProfileViewSet(CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Profile.objects.all()
        else:
            return Profile.objects.get(user_id = self.request.user.id)

    def get_serializer_context(self):
        return {"user_id":self.request.user.id}

