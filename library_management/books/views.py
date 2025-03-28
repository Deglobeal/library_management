from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from Users.permissions import IsAdminOrApprovedLibrarianOrReadOnly


class BookViewSet(viewsets.ModelViewSet): 
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrApprovedLibrarianOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        
        if params.get('available') == 'true':
            queryset = queryset.filter(copies_available__gt=0)
        elif params.get('available') == 'false':
            queryset = queryset.filter(copies_available=0)
            
        if title := params.get('title'):
            queryset = queryset.filter(title__icontains=title)
        if author := params.get('author'):
            queryset = queryset.filter(author__icontains=author)
        if isbn := params.get('isbn'):
            queryset = queryset.filter(isbn=isbn)
            
        return queryset