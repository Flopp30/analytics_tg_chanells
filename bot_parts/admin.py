import json

from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from bot_parts.models import ExternalSettings


@admin.register(ExternalSettings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = (
        "edit", 'additional_percents_for_repost', 'starting_interval_second_task'
    )
    list_per_page = 1

    def edit(self, obj):
        return format_html('<div>Изменить</div>')

    edit.short_description = 'Изменить'

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ValidationError as e:
            self.message_user(request, str(*e), level=messages.ERROR)

    def response_delete(self, request, obj_display, obj_id):
        """ Changed super() method, fixed doubling the deletion message"""
        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps(
                {
                    "action": "delete",
                    "value": str(obj_id),
                }
            )
            return TemplateResponse(
                request,
                self.popup_response_template
                or [
                    "admin/%s/%s/popup_response.html"
                    % (self.opts.app_label, self.opts.model_name),
                    "admin/%s/popup_response.html" % self.opts.app_label,
                    "admin/popup_response.html",
                ],
                {
                    "popup_response_data": popup_response_data,
                },
            )

        # self.message_user(  # REMOVED
        #     request,
        #     "The %(name)s “%(obj)s” was deleted successfully."
        #     % {
        #         "name": self.opts.verbose_name,
        #         "obj": obj_display,
        #     },
        #     messages.SUCCESS,  # Shitty success tag :)
        # )

        if self.has_change_permission(request, None):
            post_url = reverse(
                "admin:%s_%s_changelist" % (self.opts.app_label, self.opts.model_name),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": self.opts}, post_url
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)
