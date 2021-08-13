from django.contrib import admin
from .models import Broadcaster, Program, Air, Nanitozo


class BroadcasterAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'abbreviation',
        'search_index',
        'site_url'
    ]


admin.site.register(Broadcaster, BroadcasterAdmin)


class ProgramAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'search_index',
        'site_url',
        'key_station'
    ]


admin.site.register(Program, ProgramAdmin)


class NanitozoInline(admin.TabularInline):  # class NanitozoInline(admin.StackedInline):
    model = Nanitozo
    extra = 1


class AirAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['program']}),
        ('放送日時', {'fields': ['broadcaster', 'started', 'ended']}),
        ('概要', {'fields': ['overview_before', 'overview_after']}),
    ]
    inlines = [NanitozoInline]
    list_display = ('id', 'program', 'started', 'ended', 'was_aired_this_week')
    list_filter = ['started']
    search_fields = ['program']  # programやprogram_idだと検索はエラー、やり方を調整する必要があるらしい https://k-mawa.hateblo.jp/entry/2018/03/10/005936


admin.site.register(Air, AirAdmin)


class NanitozoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('放送', {'fields': ['air']}),
        ('リスナー', {'fields': ['user', 'good']}),
        ('コメント', {'fields': ['comment_open', 'comment_recommend', 'comment', 'comment_negative']}),
        ('システム', {'fields': ['created', 'updated']}),
    ]


admin.site.register(Nanitozo, NanitozoAdmin)
