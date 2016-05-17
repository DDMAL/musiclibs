from django.contrib import admin
from misirlou.models import Manifest


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('remote_url', 'created')
    readonly_fields = ('id', 'remote_url', 'manifest_hash')

    def has_add_permission(self, request):
        return False