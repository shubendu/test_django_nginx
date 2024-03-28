from django.db import models
from users.mixins import UserTypeMixin
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages


class AdminContent(models.Model):
    """
    This model is used to store contents for the admin.
    """
    title = models.CharField(max_length=20)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Admin Content'


def post_login_action(sender, user, request, **kwargs):
    messages.success(request, f'Welcome {user.get_full_name()}')


user_logged_in.connect(post_login_action)
