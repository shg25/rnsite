from django.contrib import admin
from .models import Program, Air, Nanitozo


class ProgramAdmin(admin.ModelAdmin):
    fields = ['name']


admin.site.register(Program, ProgramAdmin)


class NanitozoInline(admin.TabularInline):  # class NanitozoInline(admin.StackedInline):
    model = Nanitozo
    extra = 1


class AirAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['program']}),
        ('放送日時', {'fields': ['started', 'ended']}),
    ]
    inlines = [NanitozoInline]
    list_display = ('id', 'program', 'started', 'ended', 'was_aired_this_week')
    list_filter = ['started']
    search_fields = ['program']  # programやprogram_idだと検索はエラー、やり方を調整する必要があるらしい https://k-mawa.hateblo.jp/entry/2018/03/10/005936


admin.site.register(Air, AirAdmin)


class NanitozoAdmin(admin.ModelAdmin):
    fields = ['air', 'comment']


admin.site.register(Nanitozo, NanitozoAdmin)
