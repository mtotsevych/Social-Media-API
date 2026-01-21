import json

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import User, Post
from user.permissions import IsAuthor
from user.serializers import (
    UserCreateSerializer,
    AuthTokenSerializer,
    UserListSerializer,
    UserDetailSerializer,
    PostCreateUpdateSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentCreateSerializer,
    PostCreateScheduleSerializer,
)


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)


class UserLoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer,)


class UserLogoutView(APIView):
    permission_classes = (AllowAny,)

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


class UserYourProfileView(
    generics.RetrieveUpdateDestroyAPIView
):
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


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostCreateUpdateSerializer
    queryset = Post.objects.all()

    def get_permissions(self) -> list[BasePermission]:
        if self.action in (
            "update", "partial_update", "destroy",
        ):
            return [IsAuthor()]
        return [IsAuthenticated()]

    @staticmethod
    def params_to_ints(qs: str) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        elif self.action == "comment":
            return CommentCreateSerializer
        elif self.action == "schedule":
            return PostCreateScheduleSerializer

        return serializer_class

    def get_queryset(self) -> QuerySet[Post]:
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related("author")
                .prefetch_related("likes", "tags")
            )

        if self.action == "retrieve":
            queryset = (
                queryset
                .select_related("author")
                .prefetch_related("likes", "tags", "comments")
            )

        user_posts = self.request.query_params.get("my")
        subscriptions_posts = self.request.query_params.get(
            "subscriptions"
        )
        liked_posts = self.request.query_params.get("liked")
        tags = self.request.query_params.get("tags")

        if user_posts == "1":
            queryset = queryset.filter(author=self.request.user)
        if subscriptions_posts == "1":
            queryset = queryset.filter(
                author__in=self.request.user.subscriptions.all()
            )
        if liked_posts == "1":
            queryset = queryset.filter(
                likes__id=self.request.user.id
            )
        if tags:
            tag_ids = self.params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        return queryset.distinct()

    def perform_create(
        self,
        serializer: PostCreateUpdateSerializer
    ) -> None:
        serializer.save(author=self.request.user)

    @action(
        methods=["POST"],
        detail=True
    )
    def like(self, request: Request, pk: int) -> Response:
        post = self.get_object()

        if post.author == request.user:
            return Response(
                {"detail": "You cannot like your own post"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if post.likes.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You already liked this post"},
                status=status.HTTP_200_OK
            )

        post.likes.add(request.user)
        return Response(
            {"detail": "You successfully liked this post"},
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=["POST"],
        detail=True
    )
    def unlike(self, request: Request, pk: int) -> Response:
        post = self.get_object()

        if post.likes.filter(pk=request.user.pk).exists():
            post.likes.remove(request.user)
            return Response(
                {"detail": "You successfully unliked this post"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "You did not like this post"},
            status=status.HTTP_200_OK
        )

    @action(
        methods=["POST"],
        detail=True
    )
    def comment(self, request: Request, pk: int) -> Response:
        post = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            post=post,
            commentator=self.request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=["POST"],
        detail=False
    )
    def schedule(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_at = serializer.validated_data.pop("created_at")
        serializer.validated_data["author"] = self.request.user

        clocked_time = ClockedSchedule.objects.create(
            clocked_time=created_at
        )
        PeriodicTask.objects.create(
            name=f"Delayed post #{clocked_time.id}",
            task="user.tasks.delayed_post",
            clocked=clocked_time,
            description="This task publishes a post "
                        "at the exact time selected by the user",
            kwargs=json.dumps(serializer.validated_data),
            one_off=True
        )

        return Response(
            {"detail": "Post scheduled"},
            status=status.HTTP_201_CREATED
        )
