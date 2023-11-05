from django.contrib import admin

from channel.models import Channel, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', "name", "target_chat_id"
    )
    list_filter = (
        'name',
    )
    ordering = ('-id', 'name')
    list_per_page = 20
    search_fields = ('name', )


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'average_react_coef', 'average_forward_coef', 'chat_id', 'name', "category", "created_at", "updated_at"
    )
    list_filter = (
        'name',
        'category',
        'created_at',
        'updated_at'
    )
    ordering = ('-id', 'category', 'name', 'created_at')
    list_per_page = 20
    search_fields = ('name', 'category__name')
