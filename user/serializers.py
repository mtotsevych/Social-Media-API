from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from user.models import User, Tag, Post, Comment


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email address",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs: dict) -> dict:
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            user = authenticate(request=self.context.get("request"),
                                username=email, password=password)
            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = "Must include 'email' and 'password'."
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data: dict) -> User:
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="email"
    )
    subscribers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="email"
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "date_joined",
            "last_login",
            "is_staff",
            "photo",
            "bio",
            "subscriptions",
            "subscribers",
        )
        read_only_fields = (
            "is_staff",
            "date_joined",
            "last_login",
            "subscriptions",
            "subscribers",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"}
            }
        }

    def update(self, instance: User, validated_data: dict) -> User:
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "image",
            "tags",
        )


class PostListSerializer(serializers.ModelSerializer):
    author = UserListSerializer(
        many=False,
        read_only=True,
    )
    number_of_likes = serializers.IntegerField(
        source="likes.count", read_only=True
    )
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "image",
            "author",
            "number_of_likes",
            "tags",
        )


class CommentSerializer(serializers.ModelSerializer):
    commentator = UserListSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "created_at",
            "commentator",
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "created_at",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserListSerializer(
        many=False,
        read_only=True,
    )
    liked_by = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source="likes",
        slug_field="email"
    )
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    comments = CommentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "created_at",
            "image",
            "author",
            "liked_by",
            "tags",
            "comments"
        )
