from rest_framework.permissions import BasePermission

MODERATION_ROLES = ('moderator', 'admin')


class IsCollectionOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsItemOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.collection.user_id == request.user.id


class CanHideCollection(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in MODERATION_ROLES


class CanUnhideCollection(CanHideCollection):
    def has_object_permission(self, request, view, obj):
        return obj.user_id != request.user.id
