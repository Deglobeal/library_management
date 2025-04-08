from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView
from rest_framework import viewsets, permissions, status
from books.models import Book 
from transactions.models import Transaction
from .models import Student, Librarian
from rest_framework.permissions import AllowAny 
from .serializers import StudentSerializer, LibrarianSerializer 
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from rest_framework.views import APIView
from .permissions import IsApprovedLibrarian, IsAdminOrSelf
from .utils import BookCart  # Adjust the path to match the actual location of the utils module

# Viewset for Student
class StudentView(viewsets.ModelViewSet): 
    serializer_class = StudentSerializer 
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Student.objects.all()
        return Student.objects.filter(user=self.request.user)

# Viewset for Librarian
class LibrarianViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarianSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedLibrarian]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Librarian.objects.all()
        return Librarian.objects.filter(user=self.request.user, is_approved=True)

# Registration Views
class RegistrationChoiceView(APIView):
    def get(self, request):
        return render(request, 'auth/choice.html')

class StudentRegistrationView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'auth/student_register.html'

    def get(self, request):
        serializer = StudentSerializer()
        return Response({
            'serializer': serializer,
            'form_submitted': False
        })

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
            
        return Response({
            'serializer': serializer,
            'form_submitted': True
        }, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
class LibrarianRegistrationView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'auth/librarian_register.html'

    def get(self, request):
        serializer = LibrarianSerializer()
        return Response({
            'serializer': serializer,
            'form_submitted': False})

    def post(self, request):
        serializer = LibrarianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
        return Response({
            'serializer': serializer,
            'form_submitted': True
        }, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)

# Home Views
def home_view(request):
    available_books = Book.objects.filter(copies_available__gt=0)
    context = {
        'books': available_books,
        'title': 'Available Books'
    }
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        elif hasattr(request.user, 'student'):
            return redirect('student-home')
        elif hasattr(request.user, 'librarian'):
            return redirect('librarian-home')
    return render(request, 'general/home.html', context)


def student_home(request):
    return render(request, 'general/student_home.html')

def librarian_home(request):
    if request.user.is_authenticated:
        if request.user.is_librarian:
            return redirect('librarian-home.html')
        else:
            messages.error(request, "You are not authorized to view this page.")
            return redirect('home')  # Added redirect
    else:
        messages.error(request, "Please login to access this page.")
        return redirect('login')


# Custom Login View

class CustomLoginView(AuthLoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse('admin:index')
        elif hasattr(user, 'student'):
            return reverse('student-home')
        elif hasattr(user, 'librarian'):
            return reverse('librarian-home')
        return super().get_success_url()
    
    
    def form_valid(self, form):
        user = form.get_user()
        if hasattr(user, 'librarian') and not user.librarian.is_approved:
            form.add_error(None, "Your account is pending approval.")
            return self.form_invalid(form)
        return super().form_valid(form)
    
    
@login_required
def student_home(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    cart = BookCart(request)  # Initialize cart here
    student = request.user.student
    
    available_books = Book.objects.filter(status='APPROVED', copies_available__gt=0).order_by('title')      
    
    # Handle POST requests first
    if request.method == 'POST':
        if 'toggle_book' in request.POST:
            book_id = request.POST.get('book_id')
            selected = cart.toggle(book_id)
            return JsonResponse({'selected': selected})
            
        if 'confirm_borrow' in request.POST:
            return handle_borrow_request(request, cart)

    # Get data for context
    current_borrowed = Transaction.objects.filter(
        user=request.user, 
        return_date__isnull=True
    )
    overdue_books = current_borrowed.filter(due_date__lt=timezone.now())
    returned_books = Transaction.objects.filter(
        user=request.user, 
        return_date__isnull=False
    ).order_by('-return_date')
    
    approved_books = Book.objects.filter(status='APPROVED', copies_available__gt=0)
    selected_ids = cart.get_selected()
    
    context = {
        'student': student,
        'available_books': approved_books,
        'current_borrowed': current_borrowed,
        'returned_books': returned_books,
        'overdue_books': overdue_books,
        'max_books': 3,
        'selected_books': Book.objects.filter(id__in=selected_ids),
        'cart_count': len(selected_ids),
        'can_borrow': current_borrowed.count() + len(selected_ids) <= 3 and not overdue_books.exists()
    }
    return render(request, 'general/student_home.html', context)
def handle_borrow_request(request, cart):
    student_user = request.user
    selected_ids = cart.get_selected()
    
    try:
        with transaction.atomic():  
            for book_id in selected_ids:
                book = Book.objects.select_for_update().get(
                    id=book_id,
                    status='APPROVED',
                    copies_available__gt=0
                )
                
                if Transaction.objects.filter(
                    user=student_user,
                    book=book,
                    return_date__isnull=True
                ).exists():
                    raise ValidationError(f"You already have {book.title} borrowed")
                
                Transaction.objects.create(
                    user=student_user,
                    book=book,
                    due_date=timezone.now() + timezone.timedelta(days=3)
                )
                book.copies_available -= 1
                book.save()
                
            cart.clear()
            messages.success(request, 'Books borrowed successfully')
            
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('student-home')


@login_required
def student_all_books(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    student = request.user.student
    all_books = Book.objects.filter(status='APPROVED').order_by('title')
    
    context = {
        'student': student,
        'all_books': all_books,
        'cart_count': len(BookCart(request).get_selected())
    }
    
    return render(request, 'general/student_section.html', context)

@login_required
def current_borrowed_books(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    context = {
        'current_borrowed': Transaction.objects.filter(
            user=request.user, 
            return_date__isnull=True
        ).select_related('book'),
        'section_title': 'Currently Borrowed Books',
    }
    
    return render(request, 'general/student_section.html', context)

@login_required
def borrowing_history(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    context = {
        'returned_books': Transaction.objects.filter(
            user=request.user, 
            return_date__isnull=False
        ).order_by('-return_date'),
        'section_title': 'Borrowing History',
    }
    return render(request, 'general/student_section.html', context)

@login_required
def borrowing_status(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    current_borrowed = Transaction.objects.filter(
        user=request.user, 
        return_date__isnull=True
    )
    overdue_books = current_borrowed.filter(due_date__lt=timezone.now())
    
    context = {
        'current_borrowed_count': current_borrowed.count(),
        'overdue_books': overdue_books,
        'max_books': 3,
        'section_title': 'Borrowing Status'
    }
    return render(request, 'general/student_section.html', context)
    


    
    
    
    
@login_required
def librarian_home(request):
    # Check if user is an approved librarian
    if not hasattr(request.user, 'librarian') or not request.user.librarian.is_approved:
        return redirect('home')
    
    context = {}
    
    # Add staff-specific data to context
    if request.user.is_staff:
        context['pending_librarians'] = Librarian.objects.filter(is_approved=False)
        context['recent_transactions'] = Transaction.objects.all().order_by('-transaction_date')[:10]
    
    # Always render the template, even for non-staff librarians
    return render(request, 'general/librarian_home.html', context)