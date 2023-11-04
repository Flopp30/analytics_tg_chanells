from django.contrib import admin

from channel.models import Channel


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', "category", "created_at", "updated_at"
    )
    list_filter = (
        'name',
        'category',
        'created_at',
        'updated_at'
    )
    ordering = ('-id', 'category', 'name', 'created_at')
    list_per_page = 20
    search_fields = ('name', 'category')
