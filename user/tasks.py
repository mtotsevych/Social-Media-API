from celery import shared_task

from user.models import Post


@shared_task
def delayed_post(**kwargs) -> None:
    Post.objects.create(**kwargs)
