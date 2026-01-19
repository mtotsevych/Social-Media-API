from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from user.models import User


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
        return get_user_model().objects.create_user(**validated_data)
