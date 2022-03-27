from django.db import models


class NanitozoListManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')


class NanitozoSelfListManager(models.Manager):

    def get(self, user):
        return self.get_queryset().filter(user=user).order_by('-created_at')


class NanitozoCloseListManager(models.Manager):

    def get(self, user):
        return self.get_queryset().filter(user=user).filter(comment_open=False).order_by('-created_at')
