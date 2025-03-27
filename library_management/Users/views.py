from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView
from rest_framework import viewsets, permissions, status
from .models import Student, Librarian
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser 
from .serializers import StudentSerializer, LibrarianSerializer 
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from .permissions import IsApprovedLibrarian

# Create your views here.


# viewset for student
class StudentView(viewsets.ModelViewSet): 
    queryset = Student.objects.all() 
    serializer_class = StudentSerializer 
    permission_classes = [permissions.IsAuthenticated]
    
    
# viewset for librarian
class LibrarianViewSet(viewsets.ModelViewSet):
    queryset =Librarian.objects.filter(is_approved=True)
    serializer_class = LibrarianSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedLibrarian] # type: ignore

# registration choice view for user
class RegistrationChoiceView(APIView):
    def get(self, request):
        return render(request, 'auth/choice.html')
    
# student registration view
class StudentRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'auth/student_register.html'

    def get(self, request):
        return Response(template_name=self.template_name)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect('login')
        return Response(
            {'errors': serializer.errors},
            template_name=self.template_name
        )
# librarian registration view
class LibrarianRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'auth/librarian_register.html'

    def get(self, request):
        return Response(template_name=self.template_name)

    def post(self, request):
        serializer = LibrarianSerializer(data=request.data)
        if serializer.is_valid():
            librarian = serializer.save()
            return redirect('login')
        return Response(
            {'errors': serializer.errors},
            template_name=self.template_name
        )
# admin registration view


# home view for each type of user

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        elif hasattr(request.user, 'student'):
            return redirect('student-home')
        elif hasattr(request.user, 'librarian'):
            return redirect('librarian-home')
    return render(request, 'general/home.html')

def student_home(request):
    return render(request, 'general/student_home.html')

def librarian_home(request):
    return render(request, 'general/librarian_home.html')


# to handle login 
class CustomLoginView(AuthLoginView):
    def get_success_url(self):
        user = self.request.user
        if self.request.user.is_superuser:
            return '/admin/'
        elif hasattr(self.request.user, 'student'):
            return '/student-home'
        elif hasattr(self.request.user, 'librarian'):
            return '/librarian-home'
        return super().get_success_url()