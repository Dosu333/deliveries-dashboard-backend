from rest_framework import permissions
from django.contrib.auth import get_user_model
import os, requests


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to super admin users. """
    message = "Only Super Admins are authorized to perform this action."

    def has_permission(self, request, view):
        url = f"{os.environ.get('AUTH_URL')}/{request.user.id}/"
        res = requests.get(url, verify=False)
        user = res.json()
        return bool(request.user and user['roles'] and 'SUPERADMIN' in user['roles'])


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users. """
    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        url = f"{os.environ.get('AUTH_URL')}/{request.user.id}/"
        res = requests.get(url, verify=False)
        user = res.json()
        return bool(request.user and user['roles'] and 'ADMIN' in user['roles'])


class IsRegularUser(permissions.BasePermission):
    """Allows access only to talent users. """
    message = "Only Regular users are authorized to perform this action."

    def has_permission(self, request, view):
        url = f"{os.environ.get('AUTH_URL')}/{request.user.id}/"
        res = requests.get(url, verify=False)
        user = res.json()
        return bool(request.user and user['roles'] and 'REGULAR' in user['roles']) 