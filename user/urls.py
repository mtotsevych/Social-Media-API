from django.urls import path

from user.views import (
    UserLoginView,
    UserCreateView,
    UserLogoutView,
    UserListView,
    UserManageYourProfileView,
    UserRetrieveOtherProfileView,
)

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path(
        "users/me/",
        UserManageYourProfileView.as_view(),
        name="user-me-manage"
    ),
    path(
        "users/<int:pk>/",
        UserRetrieveOtherProfileView.as_view(),
        name="user-other-retrieve"
    ),
]
