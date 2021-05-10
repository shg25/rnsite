import datetime

from django.db import models
from django.utils import timezone
from pytz import timezone as pytztimezone  # TODO どこかにまとめる

# 番組
class Program(models.Model):
    name = models.CharField(max_length=200)  # 番組名
    def __str__(self):
        return self.name


# 放送
class Air(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    started = models.DateTimeField('開始日時')
    ended = models.DateTimeField('終了日時')
    def __str__(self):
        return self.program.name + " " + str(self.started.astimezone(pytztimezone('Asia/Tokyo')))
    def was_aired_this_week(self):
        now = timezone.now()
        return now - datetime.timedelta(days=7) <= self.started <= now
    was_aired_this_week.admin_order_field = 'started'  # 代わりにソートするカラムを指定する
    was_aired_this_week.boolean = True  # 見た目を○×アイコンにする
    was_aired_this_week.short_description = 'this week?'  # タイトルの表記設定


# 何卒（聴取）
class Nanitozo(models.Model):
    air = models.ForeignKey(Air, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)  # 感想
    def __str__(self):
        return self.comment
