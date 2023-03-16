# 何卒のアイコン名を管理
from enum import Enum


class NanitozoIconType(Enum):
    nanitozo = 'icon: user'
    good = 'icon: happy'
    comment_recommend = 'icon: star'
    comment = 'icon: comment'
    comment_negative = 'icon: paint-bucket'
    has_air_overview = 'icon: info'
