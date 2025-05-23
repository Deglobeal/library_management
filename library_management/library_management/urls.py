"""
URL configuration for library_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from Users.views import home_view, librarian_home
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    
    path('api/books/', include('books.urls')),
    path('api/transactions/', include('transactions.urls')),
    
    
    
    
    
    
    
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('Users/', include('Users.urls')),    
    path('librarian-home/', librarian_home, name='librarian_home'), 
    path('admin/logout/', LogoutView.as_view(next_page='home'), name='admin_logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)