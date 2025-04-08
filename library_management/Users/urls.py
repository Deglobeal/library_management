from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from . import views
from .views import (
    StudentView, 
    LibrarianViewSet,
    StudentRegistrationView,
    LibrarianRegistrationView,
    CustomLoginView,  
    home_view,
    student_home,
    librarian_home
)
urlpatterns = [
    # Student Endpoints
    path('students/<str:pk>/', StudentView.as_view({'get': 'list', 'post': 'create'}), name='student-list'),
    path('students/<str:pk>/', StudentView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='student-detail'),
    path('student/books/all/', views.student_all_books, name='all-library-books'),
    path('student/books/borrowed/', views.current_borrowed_books, name='current-borrowed'),
    path('student/books/history/', views.borrowing_history, name='borrowing-history'),
    path('student/status/', views.borrowing_status, name='borrowing-status'),

    # Librarian Endpoints
    path('librarians/', LibrarianViewSet.as_view({'get': 'list', 'post': 'create'}), name='librarian-list'),
    path('librarians/<int:pk>/', LibrarianViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='librarian-detail'),
    
    # Use only the custom login view
    path('login/', CustomLoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # Registration URLs
    path('register/', TemplateView.as_view(template_name='auth/choice.html'), name='register-choice'),
    path('register/student/', StudentRegistrationView.as_view(), name='student-register'),
    path('register/librarian/', LibrarianRegistrationView.as_view(), name='librarian-register'),
    
    
    path('', home_view, name='home'),
    path('librarian-home/', librarian_home, name='librarian-home'),
    path('student-home/', student_home, name='student-home'),
    
    ]
