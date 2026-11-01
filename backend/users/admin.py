from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import User

# Stran z izdanimi žetoni bi glavnemu skrbniku pokazala veljavne refresh žetone drugih uporabnikov.
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']
    fields = ['username', 'email', 'role', 'is_active', 'date_joined', 'last_login']

    def get_readonly_fields(self, request, obj=None):
        readonly = ['username', 'email', 'date_joined', 'last_login']
        if obj is not None and (obj == request.user or obj.is_superuser):
            readonly += ['role', 'is_active']
        return readonly

    def _is_administrator(self, request):
        return request.user.is_active and request.user.role == User.Role.ADMIN

    def has_module_permission(self, request):
        return self._is_administrator(request)

    def has_view_permission(self, request, obj=None):
        return self._is_administrator(request)

    def has_change_permission(self, request, obj=None):
        return self._is_administrator(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
