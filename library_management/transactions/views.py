from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Transaction
from books.models import Book
from .serializers import TransactionSerializer


class CheckoutBook(APIView):
    def post(self, request):
        book = get_object_or_404(Book, pk=request.data.get('book_id'))
        
        
        active_checkout = Transaction.objects.filter(
            user=request.user, 
            book=book, 
            return_date__isnull=True
        ).exists()
        
        if active_checkout:
            return Response(
                {'error': 'You already have an active checkout for this book'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)

class CheckoutBook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        book = get_object_or_404(Book, pk=request.data.get('book_id'))
        if book.copies_available <= 0:
            return Response({'error': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)
        if Transaction.objects.filter(user=request.user, book=book, return_date__isnull=True).exists():
            return Response({'error': 'You already checked out this book'}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = Transaction.objects.create(
            user=request.user,
            book=book,
            due_date=timezone.now() + timezone.timedelta(days=14)
        )
        book.copies_available -= 1
        book.save()
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

class ReturnBook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction = get_object_or_404(
            Transaction,
            book_id=request.data.get('book_id'),
            user=request.user,
            return_date__isnull=True
        )
        transaction.return_date = timezone.now()
        transaction.save()
        transaction.book.copies_available += 1
        transaction.book.save()
        return Response({'status': 'Book returned'}, status=status.HTTP_200_OK)
    
    
    
