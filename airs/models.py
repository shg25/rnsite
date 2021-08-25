import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import constraints
from django.utils import timezone
from pytz import timezone as pytztimezone  # TODO どこかにまとめる


def get_last_name(self):
    return self.last_name

User.add_to_class("__str__", get_last_name)


# 放送局
class Broadcaster(models.Model):
    name = models.CharField(
        verbose_name='名前',
        unique=True,
        max_length=80,
    )
    abbreviation = models.CharField(
        verbose_name='略称',
        unique=True,
        max_length=20,
        help_text='一覧に表示するための表記'
    )
    search_index = models.CharField(
        verbose_name='検索インデックス',
        null=True, blank=True,
        max_length=400,
    )
    site_url = models.CharField(
        verbose_name='サイトURL',
        null=True, blank=True,
        max_length=400,
    )
    wikipedia_url = models.CharField(
        verbose_name='Wikipedia',
        null=True, blank=True,
        max_length=400,
    )
    area = models.CharField(
        verbose_name='放送対象地域',
        max_length=20,
    )
    address = models.CharField(
        verbose_name='所在地',
        max_length=400,
    )
    keyword = models.CharField(
        verbose_name='キーワード',
        null=True, blank=True,
        max_length=400,
    )

    def __str__(self):
        return self.name


# 番組
class Program(models.Model):
    name = models.CharField(
        verbose_name='名前',
        unique=True,
        max_length=200,
    )
    search_index = models.CharField(
        verbose_name='検索インデックス',
        null=True, blank=True,
        max_length=400,
    )
    hashtag = models.CharField(
        verbose_name='ハッシュタグ',
        null=True, blank=True,
        max_length=80,
    )
    twitter_id = models.CharField(
        verbose_name='Twitter ID',
        null=True, blank=True,
        max_length=400,
    )
    site_url = models.CharField(
        verbose_name='サイトURL',
        null=True, blank=True,
        max_length=400,
    )
    wikipedia_url = models.CharField(
        verbose_name='Wikipedia',
        null=True, blank=True,
        max_length=400,
    )
    key_station = models.ForeignKey(
        Broadcaster, on_delete=models.CASCADE,
        verbose_name='キー局',
        null=True, blank=True,
    )
    per_week = models.FloatField(
        verbose_name='週何回放送か',
        default=1,
    )

    def __str__(self):
        return self.name


# 放送
class Air(models.Model):
    name = models.CharField(
        verbose_name='名前',
        max_length=200,
    )
    share_text = models.CharField(
        verbose_name='シェアラジオ全文',
        max_length=400,
    )
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE,
        verbose_name='番組',
        null=True, blank=True,
    )
    broadcaster = models.ForeignKey(
        Broadcaster, on_delete=models.CASCADE,
        verbose_name='放送局',
        null=True, blank=True,
    )
    started = models.DateTimeField(
        verbose_name='開始日時',
    )
    ended = models.DateTimeField(
        verbose_name='終了日時',
    )
    overview_before = models.TextField(
        verbose_name='事前告知',
        null=True, blank=True,
    )
    overview_after = models.TextField(
        verbose_name='放送内容',
        null=True, blank=True,
    )

    def __str__(self):
        return self.name[:8] + "_" + str(self.broadcaster)[:4] + "_" + str(self.started.astimezone(pytztimezone('Asia/Tokyo')))[:16]

    def was_aired_this_week(self):
        now = timezone.now()
        return now - datetime.timedelta(days=7) <= self.started <= now
    was_aired_this_week.admin_order_field = 'started'  # 代わりにソートするカラムを指定する
    was_aired_this_week.boolean = True  # 見た目を○×アイコンにする
    was_aired_this_week.short_description = 'this week?'  # タイトルの表記設定

    class Meta:
        constraints = [
            # 同じ 放送局 と 開始日時 の組み合わせが登録済の場合は却下
            models.UniqueConstraint(
                fields=['broadcaster', 'started'],
                name='air_unique',
            ),
        ]


# 何卒（聴取）
class Nanitozo(models.Model):
    air = models.ForeignKey(
        Air, on_delete=models.CASCADE,
        verbose_name='放送',
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='リスナー',
    )
    good = models.BooleanField(
        verbose_name='満足',
        default=False,
    )
    comment_open = models.BooleanField(
        verbose_name='コメント公開',
        default=True,
    )
    comment_recommend = models.TextField(
        verbose_name='推薦文',
        null=True, blank=True,
    )
    comment = models.TextField(
        verbose_name='感想文',
        null=True, blank=True,
    )
    comment_negative = models.TextField(
        verbose_name='感想文ネガ',
        null=True, blank=True,
    )
    created = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True,
    )

    def __str__(self):
        return self.user.last_name + '_' + str(self.air)

    class Meta:
        constraints = [
            # 同じ 放送 と ユーザー の組み合わせが登録済の場合は却下
            models.UniqueConstraint(
                fields=['air', 'user'],
                name='nanitozo_unique',
            ),
        ]
