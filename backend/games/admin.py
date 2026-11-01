from django.contrib import admin

from config.admin_utils import ReadOnlyAdmin

from .models import Game, GameRelease, Platform

admin.site.register(Platform, ReadOnlyAdmin)
admin.site.register(Game, ReadOnlyAdmin)
admin.site.register(GameRelease, ReadOnlyAdmin)
