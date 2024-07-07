from django.contrib import admin

from api.models import Organisation


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("org_id", "name", "description")
    search_fields = ("name",)


admin.site.register(Organisation, OrganisationAdmin)
