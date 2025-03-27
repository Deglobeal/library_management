from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import User, Student, Librarian


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'department')
    raw_id_fields = ('user',)

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'is_approved')
    list_filter = ('is_approved',)
    action = ['approve_librarians']
    
    
    def approve_librarians(self, request, queryset):
        queryset.update(is_approved=True)
    approve_librarians.short_description = 'Approve selected librarians'



class CustomAdminSite(AdminSite):
    site_header = 'Library Admin'

custom_admin = CustomAdminSite(name='customadmin')
custom_admin.register(User)