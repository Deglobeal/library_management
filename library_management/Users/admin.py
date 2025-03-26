from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import User, Student, Librarian

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'user_type', 'is_approved')
    search_fields = ('user_id', 'email')
    list_filter = ('user_type', 'is_approved', 'is_staff', 'is_superuser')


    fieldsets = (
        (None, {'fields': ('user_id', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'user_type')}),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ('user_id',) + self.readonly_fields
        return self.readonly_fields

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'department')
    raw_id_fields = ('user',)

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'is_approved')
    list_filter = ('is_approved',)
    raw_id_fields = ('user',)



class CustomAdminSite(AdminSite):
    site_header = 'Library Admin'

custom_admin = CustomAdminSite(name='customadmin')
custom_admin.register(User)