from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User
from user.serializers import (
    UserCreateSerializer,
    AuthTokenSerializer,
    UserDetailSerializer
)


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)


class UserLoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    authentication_classes = ()
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer,)


class UserLogoutView(APIView):
    def post(self, request: Request) -> Response:
        token = request.auth
        if token:
            token.delete()
        return Response(
            {"detail": "Logged out"},
            status=status.HTTP_200_OK
        )


class UserManageYourProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer

    def get_object(self) -> User:
        return self.request.user


class UserRetrieveOtherProfileView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    queryset = get_user_model().objects.all()
