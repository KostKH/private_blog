from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Post

User = get_user_model()


def is_staff_check(user):
    return user.is_staff


def is_current_user_check(user, username):
    requested_user = get_object_or_404(User, username=username)
    return bool(user == requested_user)


def get_also_list(current_post_id=None):
    if not current_post_id:
        return Post.objects.all()[:3]
    return Post.objects.exclude(id=current_post_id)[:3]
