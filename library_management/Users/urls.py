from django.urls import include, path
from . import views
from .views import StudentView, LibrarianViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # Student Endpoints
    path('students/', StudentView.as_view({'get': 'list', 'post': 'create'}), name='student-list'),
    path('students/<int:pk>/', StudentView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='student-detail'),

    # Librarian Endpoints
    path('librarians/', LibrarianViewSet.as_view({'get': 'list', 'post': 'create'}), name='librarian-list'),
    path('librarians/<int:pk>/', LibrarianViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='librarian-detail'),
]
