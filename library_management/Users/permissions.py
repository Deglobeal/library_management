from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsApprovedLibrarian(permissions.BasePermission):
    """Allows access only to approved librarians."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, "librarian") and 
            request.user.librarian.is_approved
        )

class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission: 
    - Admins can access all student records.
    - Students can only view and edit their own record.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if user is an admin
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Allow students to access their own record
        return obj.id == request.user.id
