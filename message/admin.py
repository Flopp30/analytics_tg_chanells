from django.contrib import admin

from message.models import Message
from metrics.models import Metric


class MetricAdminInline(admin.TabularInline):
    model = Metric
    extra = 1


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', "channel", 'average_forward_coef', 'average_reaction_coef', 'views',
        "reactions", "forwards", 'is_forwarded', "created_at", "updated_at"
    )
    list_filter = (
        'channel',
        'forwards',
        "created_at",
        "updated_at"
    )
    ordering = ('-id', 'channel', 'created_at')
    list_per_page = 20
    search_fields = ('text', 'channel')
    inlines = (MetricAdminInline,)
