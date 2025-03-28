from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView
from rest_framework import viewsets, permissions, status
from books.models import Book 
from .models import Student, Librarian
from rest_framework.permissions import AllowAny 
from .serializers import StudentSerializer, LibrarianSerializer 
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.urls import reverse
from rest_framework.views import APIView
from .permissions import IsApprovedLibrarian, IsAdminOrSelf

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
    return render(request, 'general/librarian_home.html')

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