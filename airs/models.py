from django.db import models
from datetime import datetime
from pytz import timezone

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
        return self.program.name + " " + str(self.started.astimezone(timezone('Asia/Tokyo')))
    def was_aired_this_week(self):
        return self.started >= timezone.now() - datetime.timedelta(days=7)


# 何卒（聴取）
class Nanitozo(models.Model):
    air = models.ForeignKey(Air, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)  # 感想
    def __str__(self):
        return self.comment
