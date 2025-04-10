from django.shortcuts import render, redirect, get_object_or_404
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
from .utils import BookCart  
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy


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
    
    current_borrowed = Transaction.objects.filter(
        user=request.user,
        return_date__isnull=True
    )
    overdue = current_borrowed.filter(due_date__lt=timezone.now()).exists()
    
    context = {
        'all_books': Book.objects.filter(status='APPROVED'),
        'can_borrow': current_borrowed.count() < 3 and not overdue,
        'section': 'books',
        'section_title': 'All Books'
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
        'section': 'borrowed'
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
    if not hasattr(request.user, 'librarian') or not request.user.librarian.is_approved:
        return redirect('home')
    
    context = {}
    
    if request.user.is_staff:
        context['pending_librarians'] = Librarian.objects.filter(is_approved=False)
        context['recent_transactions'] = Transaction.objects.all().order_by('-transaction_date')[:10]
    
    return render(request, 'general/librarian_home.html', context)

@login_required
def librarian_section(request, section):
    context = {'section' : section}
    template = f'general/librarian_sections/{section}.html'
    
    if section == 'students':
        context['students'] = Student.objects.all()
    elif section == 'overdue-books':
        context['transactions'] = Transaction.objects.filter(
            return_date__isnull=True, 
            due_date__lt=timezone.now()
        )
    elif section == 'returned-books':
        context['transactions'] = Transaction.objects.filter(
            return_date__isnull=False
        ).order_by('-return_date')
    elif section == 'approved-librarians':
        context['librarians'] = Librarian.objects.filter(is_approved=True)
    
    return render(request, template, context)

class BookCreateView(CreateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'genre', 'copies_available', 'status']
    template_name = 'general/librarian_sections/book_form.html'
    success_url = reverse_lazy('librarian-home')
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user.librarian
        return super().form_valid(form)
    
class BookUpdateView(UpdateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'genre', 'copies_available', 'status']
    template_name = 'general/librarian_sections/book_form.html'
    success_url = reverse_lazy('librarian-home')
    
class BookListView(ListView):
    model = Book
    template_name = 'general/librarian_sections/books.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'general/librarian_sections/book_detail.html'

    
class BookDeleteView(DeleteView):
    model = Book
    template_name = 'general/librarian_sections/book_confirm_delete.html'
    success_url = reverse_lazy('librarian-books')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.librarian.is_approved if hasattr(request.user, 'librarian') else False):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

@login_required
def pending_approvals(request):
    pending = Transaction.objects.filter(status='PENDING')
    return render(request, 'general/librarian_sections/approve_borrowed.html', 
                {'pending_approvals': pending})

@login_required
def approve_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.status = 'APPROVED'
    transaction.save()
    messages.success(request, 'Transaction approved successfully')
    return redirect('pending-approvals')

@login_required
def reject_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.status = 'REJECTED'
    transaction.save()
    messages.success(request, 'Transaction rejected')
    return redirect('pending-approvals') 

@login_required
def toggle_student_status(request):
    if request.method == 'POST':
        for key in request.POST:
            if key.startswith('student_'):
                user_id = key.split('_')[1]
                student = get_object_or_404(Student, user__user_id=user_id)
                action = request.POST.get(key)
                student.user.is_active = (action == 'activate')
                student.user.save()
        messages.success(request, 'Student statuses updated successfully')
    return redirect('librarian-students') 

@login_required
def student_profile(request):
    student = request.user.student
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('student-profile')
    
    return render(request, 'general/student_section.html', {
        'section': 'profile',
        'section_title': 'Update Profile'
    })
    
@login_required
def request_return(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        if not transaction_id:
            messages.error(request, "Please select a book to return")
            return redirect('student-borrowed')
            
        try:
            transaction = Transaction.objects.get(
                pk=transaction_id,
                user=request.user,
                return_date__isnull=True
            )
            transaction.status = 'RETURN_REQUESTED'
            transaction.save()
            messages.success(request, f'Return requested for "{transaction.book.title}"')
        except Transaction.DoesNotExist:
            messages.error(request, "Invalid book selection")
    
    return redirect('student-borrowed')

@login_required
def pending_return_requests(request):
    context = {
        'return_requests': Transaction.objects.filter(
            status='RETURN_REQUESTED'
        ).select_related('book', 'user'),
        'section': 'return-requests',
        'section_title': 'Pending Return Requests'
    }
    return render(request, 'general/librarian_sections/return_requests.html', context)

@login_required
def approve_return(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.status = 'RETURNED'
        transaction.return_date = timezone.now()
        transaction.book.copies_available += 1
        transaction.book.save()
        transaction.save()
        messages.success(request, f'Return approved for {transaction.book.title}')
    return redirect('pending-return-requests')

@login_required
def reject_return(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.status = 'APPROVED'
        transaction.save()
        messages.warning(request, f'Return rejected for {transaction.book.title}')
    return redirect('pending-return-requests')


@login_required
def borrow_book(request, book_id):
    if not hasattr(request.user, 'student'):
        return redirect('home')
    
    book = get_object_or_404(Book, id=book_id)
    student = request.user.student
    
    try:
        with transaction.atomic():
            # Check borrowing eligibility
            current_borrowed = Transaction.objects.filter(
                user=request.user,
                return_date__isnull=True
            )
            overdue = current_borrowed.filter(due_date__lt=timezone.now()).exists()
            
            if current_borrowed.count() >= 3:
                raise ValidationError("Maximum borrowing limit reached")
            if overdue:
                raise ValidationError("Cannot borrow with overdue books")
            if book.copies_available < 1:
                raise ValidationError("No copies available")
            
            # Create transaction
            Transaction.objects.create(
                user=request.user,
                book=book,
                due_date=timezone.now() + timezone.timedelta(days=14)
            )
            
            # Update book copies
            book.copies_available -= 1
            book.save()
            
            messages.success(request, f'Successfully borrowed "{book.title}"')
            
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('student-books')