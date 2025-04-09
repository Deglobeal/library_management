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
    path('student/dashboard/', student_home, name='student-home'),
    path('student/books/', views.student_all_books, name='student-books'),
    path('student/books/borrowed/', views.current_borrowed_books, name='student-borrowed'),
    path('student/books/history/', views.borrowing_history, name='student-history'),
    path('student/status/', views.borrowing_status, name='student-status'),
    path('student/profile/', views.student_profile, name='student-profile'),
    path('student/return-request/', views.request_return, name='return-request'),
    
    # Librarian Endpoints
    path('librarians/', LibrarianViewSet.as_view({'get': 'list', 'post': 'create'}), name='librarian-list'),
    path('librarians/<int:pk>/', LibrarianViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='librarian-detail'),
    
    
    path('librarian/students/', views.librarian_section, {'section': 'students'}, name='librarian-students'),
    path('librarian/books/', views.BookListView.as_view(), name='librarian-books'),
    path('librarian/books/add/', views.BookCreateView.as_view(), name='book-create'),
    path('librarian/books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('librarian/books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('librarian/overdue-books/', views.librarian_section, {'section': 'overdue-books'}, name='overdue-books'),
    path('librarian/returned-books/', views.librarian_section, {'section': 'returned-books'}, name='returned-books'),
    path('librarian/approved-librarians/', views.librarian_section, {'section': 'approved-librarians'}, name='approved-librarians'),
    path('librarian/students/toggle-status/', views.toggle_student_status, name='toggle-student-status'),
    path('librarian/books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('librarian/approve-books/', views.pending_approvals, name='pending-approvals'),
    path('librarian/approve-transaction/<int:pk>/', views.approve_transaction, name='approve-transaction'),
    path('librarian/reject-transaction/<int:pk>/', views.reject_transaction, name='reject-transaction'),
        
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
