from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'copies_available')
    search_fields = ('title', 'author', 'isbn')
    
    
    def picture_preview(self, obj):
        return obj.picture and f'<img src="{obj.picture.url}"  style="width: 50px; height: 50px;" />' or 'No Image'
    
    picture_preview.short_description = 'Cover Preview'
    picture_preview.allow_tags = True