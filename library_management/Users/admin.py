# admin.py
from django.contrib import admin
from .models import User, Student, Librarian

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'user_type', 'is_staff', 'get_is_approved')
    list_filter = ('user_type', 'is_staff')
    readonly_fields = ('user_id', 'date_joined')
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'user_type')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_is_approved(self, obj):
        if hasattr(obj, 'librarian'):
            return obj.librarian.is_approved
        return "N/A"  # Return "N/A" for non-librarians

    get_is_approved.short_description = "Approved"
    get_is_approved.admin_order_field = "librarian__is_approved"
    
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'department')

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'is_approved')
    list_filter = ('is_approved',)
    list_editable = ('is_approved',)
    actions = ['approve_librarians']  
    
    
    def approve_librarians(self, request, queryset):
        queryset.update(is_approved=True)