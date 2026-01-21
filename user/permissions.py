from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from user.models import Post


class IsAuthor(BasePermission):
    def has_object_permission(
        self,
        request: Request,
        view,
        obj: Post
    ) -> bool:
        return bool(request.user == obj.author)
