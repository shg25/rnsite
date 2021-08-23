from django.contrib import admin
from .models import Broadcaster, Program, Air, Nanitozo


class ProgramInline(admin.TabularInline):  # class NanitozoInline(admin.StackedInline):
    model = Program
    extra = 1


class BroadcasterAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'abbreviation',
        'search_index',
        'site_url',
        'wikipedia_url',
        'area',
        'address',
        'keyword'
    ]
    inlines = [ProgramInline]
    list_display = ('id', 'name', 'search_index', 'area', 'keyword')
    list_display_links = ('name',)
    ordering = ('id',)


admin.site.register(Broadcaster, BroadcasterAdmin)


class ProgramAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'search_index',
        'hashtag',
        'twitter_id',
        'site_url',
        'wikipedia_url',
        'key_station'
    ]
    list_display = ('id', 'name', 'key_station')
    list_display_links = ('name',)
    list_filter = ['key_station']
    ordering = ('id',)


admin.site.register(Program, ProgramAdmin)


class NanitozoInline(admin.StackedInline):  # class NanitozoInline(admin.TabularInline):
    model = Nanitozo
    extra = 1


class AirAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'program']}),
        ('放送日時', {'fields': ['broadcaster', 'started', 'ended']}),
        ('概要', {'fields': ['overview_before', 'overview_after']}),
    ]
    inlines = [NanitozoInline]
    list_display = ('id', 'name', 'program', 'started', 'was_aired_this_week')
    list_display_links = ('name',)
    list_filter = ['started', 'program', 'broadcaster']
    ordering = ('-started',)
    search_fields = ['program']  # programやprogram_idだと検索はエラー、やり方を調整する必要があるらしい https://k-mawa.hateblo.jp/entry/2018/03/10/005936


admin.site.register(Air, AirAdmin)


# 何卒を管理画面から追加するのは現実的ではないので消した方が良いかも
class NanitozoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('放送', {'fields': ['air']}),
        ('リスナー', {'fields': ['user', 'good']}),
        ('コメント', {'fields': ['comment_open', 'comment_recommend', 'comment', 'comment_negative']}),
    ]
    readonly_fields = ('created', 'updated')
    list_display = ('id', 'user', 'air', 'created', 'updated')
    list_filter = ['user']
    ordering = ('-created',)


admin.site.register(Nanitozo, NanitozoAdmin)
