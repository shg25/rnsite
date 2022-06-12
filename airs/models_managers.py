from django.db import models

from common.util.datetime_extensions import this_week_started, last_week_started


class AirTwoWeekListManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(started_at__gte=last_week_started()).order_by('-started_at')


class AirIdentificationManager(models.Manager):

    def get(self, broadcaster, started_at):
        return self.get_queryset().filter(broadcaster=broadcaster, started_at=started_at)


class NanitozoListManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')


class NanitozoSelfListManager(models.Manager):

    def get(self, user):
        return self.get_queryset().filter(user=user).order_by('-created_at')


class NanitozoCloseListManager(models.Manager):

    def get(self, user):
        return self.get_queryset().filter(user=user).filter(comment_open=False).order_by('-created_at')
