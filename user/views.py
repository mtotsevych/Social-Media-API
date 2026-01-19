from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User
from user.serializers import (
    UserCreateSerializer,
    AuthTokenSerializer,
    UserListSerializer,
    UserDetailSerializer,
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


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self) -> QuerySet[User]:
        queryset = self.queryset

        email = self.request.query_params.get("email")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if email:
            queryset = queryset.filter(email__iexact=email)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset


class UserYourProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer

    def get_object(self) -> User:
        return self.request.user


class UserOtherProfileView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    queryset = get_user_model().objects.all()


class UserSubscribeView(APIView):
    def post(self, request: Request, pk: int) -> Response:
        user = get_object_or_404(get_user_model(), pk=pk)

        if user == request.user:
            return Response(
                {"detail": "You cannot subscribe to yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.subscriptions.filter(pk=pk).exists():
            return Response(
                {"detail": "Already subscribed"},
                status=status.HTTP_200_OK
            )

        request.user.subscriptions.add(user)

        return Response(
            {"detail": f"You are now subscribed to {user.email}"},
            status=status.HTTP_201_CREATED
        )


class UserUnsubscribeView(APIView):
    def post(self, request: Request, pk: int) -> Response:
        user = get_object_or_404(get_user_model(), pk=pk)

        if request.user.subscriptions.filter(pk=pk).exists():
            request.user.subscriptions.remove(user)
            return Response(
                {"detail": f"You are unsubscribed from {user.email}"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": f"You are not subscribed to {user.email}"},
            status=status.HTTP_200_OK
        )
