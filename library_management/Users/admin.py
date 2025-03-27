# admin.py
from django.contrib import admin
from .models import User, Student, Librarian

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'user_type', 'is_approved', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'is_staff')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll', 'department')

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_librarians']  
    
    
    def approve_librarians(self, request, queryset):
        queryset.update(is_approved=True)