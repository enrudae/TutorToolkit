from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


class CustomUserViewSet(UserViewSet):
    @swagger_auto_schema(responses={201: 'User created successfully'})
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)
