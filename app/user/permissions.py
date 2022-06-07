from rest_framework import permissions
from django.contrib.auth import get_user_model
from .utils import get_user_data
import os, requests


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to super admin users. """
    message = "Only Super Admins are authorized to perform this action."

    def has_permission(self, request, view):
        user = get_user_data(request.user.id)
        return bool(user and user['roles'] and 'SUPERADMIN' in user['roles'])


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users. """
    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        user = get_user_data(request.user.id)
        return bool(user and user['roles'] and 'ADMIN' in user['roles'])


class IsRegularUser(permissions.BasePermission):
    """Allows access only to talent users. """
    message = "Only Regular users are authorized to perform this action."

    def has_permission(self, request, view):
        user = get_user_data(request.user.id)
        return bool(user and user['roles'] and 'REGULAR' in user['roles']) 