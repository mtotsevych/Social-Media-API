from django.urls import path

from user.views import UserLoginView, UserCreateView

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
]
