from django.contrib import admin

from config.admin_utils import ReadOnlyAdmin

from .models import Collection, CollectionItem

admin.site.register(Collection, ReadOnlyAdmin)
admin.site.register(CollectionItem, ReadOnlyAdmin)
