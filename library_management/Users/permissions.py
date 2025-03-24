from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsApprovedLibrarian(permissions.BasePermission):
    """Allows access only to approved librarians."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "librarian") and request.user.librarian.is_approved
    