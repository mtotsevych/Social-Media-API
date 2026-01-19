import os
import uuid

from django.utils.text import slugify


def upload_to(base_dir: str, slug_source: str, filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return os.path.join(
        base_dir,
        f"{slugify(slug_source)}-{uuid.uuid4()}{extension}"
    )


def upload_user_photo(instance, filename: str) -> str:
    return upload_to("uploads/users/", instance.email, filename)


def upload_post_image(instance, filename: str) -> str:
    return upload_to("uploads/posts/", instance.title, filename)
