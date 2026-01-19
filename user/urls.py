from django.urls import path

from user.views import (
    UserLoginView,
    UserCreateView,
    UserLogoutView,
    UserManageYourProfileView,
    UserRetrieveOtherProfileView
)

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path(
        "profile/me/",
        UserManageYourProfileView.as_view(),
        name="manage-my-profile"
    ),
    path(
        "profile/<int:pk>/",
        UserRetrieveOtherProfileView.as_view(),
        name="retrieve-other-profile"
    ),
]
