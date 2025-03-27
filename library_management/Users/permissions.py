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
        # Admins have full access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Students: Check if obj is their linked Student
        if hasattr(request.user, 'student'):
            return obj.user == request.user

        # Librarians: Check if obj is their linked Librarian
        if hasattr(request.user, 'librarian'):
            return obj.user == request.user

        return False