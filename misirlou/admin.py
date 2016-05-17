from django.contrib import admin
from misirlou.models import Manifest


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    pass
