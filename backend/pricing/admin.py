from django.contrib import admin

from config.admin_utils import ReadOnlyAdmin

from .models import PriceCheck

admin.site.register(PriceCheck, ReadOnlyAdmin)
