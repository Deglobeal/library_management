from django.urls import path
from . import views

librarian_urlpatterns = [
    path('librarians/', views.LibrarianList.as_view(), name='librarian-list'),
    path('librarians/<int:pk>/', views.LibrarianDetail.as_view(), name='librarian-detail'),
]

student_urlpatterns = [
    path('students/', views.StudentList.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetail.as_view(), name='student-detail'),
]

urlpatterns = librarian_urlpatterns + student_urlpatterns