from django import template

register = template.Library()


VERSION_NAME = 'v2.5.0'
VERSION_NAME_FOR_STATIC_FILE = '?20230311'

SITE_NAME = 'R.N.' + ' ' + VERSION_NAME
TITLE_SUFFIX = ' - ' + SITE_NAME

TITLE_LOGIN = 'ログイン'
TITLE_LOGOUT = 'ログアウト'
TITLE_PASSWORD_CHANGE = 'パスワード変更'

TITLE_AIR_LIST = '放送'
TITLE_AIR_CREATE = '放送登録&何卒'
TITLE_AIR_CREATE_SHORT = '+放送登録'
TITLE_AIR_UPDATE = '放送概要編集'

TITLE_NANITOZO_LIST = '何卒'
TITLE_NANITOZO_UPDATE = '感想編集'
TITLE_NANITOZO_DELETE = '何卒取消'
TITLE_NANITOZO_APPLY_GOOD = '満足？'
TITLE_NANITOZO_CANCEL_GOOD = '満足！'

TITLE_USER_LIST = 'リスナー'
TITLE_BROADCASTER_LIST = '放送局'
TITLE_PROGRAM_LIST = '番組'

# AIR_LIST
THIS_WEEK = '今週'
LAST_WEEK = '先週'
NONE_THIS_WEEK = '今週なし'
NONE_LAST_WEEK = '先週なし'

# 外部URL
URL_GITHUB_RELEASES = 'https://github.com/shg25/rnsite/releases'


@register.simple_tag
def rn_const(attr):
    return eval(attr)
