from django.db import models

# 番組
class Program(models.Model):
    name = models.CharField(max_length=200) # 番組名

# 放送
class Air(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    started = models.DateTimeField('date published') # 開始日時
    ended = models.DateTimeField('date published') # 終了日時

# 何卒（聴取）
class Nanitozo(models.Model):
    air = models.ForeignKey(Air, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200) # 感想