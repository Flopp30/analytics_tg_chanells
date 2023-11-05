from django.contrib import admin

from metrics.models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message', 'views', "reactions", "forwards", "created_at"
    )
    list_filter = (
        'message__channel',
        "created_at",
    )
    ordering = ('-id', 'created_at',)
    list_per_page = 20
    list_select_related = ('message', 'message__channel')
    search_fields = ('message', )
