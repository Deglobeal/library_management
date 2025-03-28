from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, CheckoutBook, ReturnBook

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('checkout/', CheckoutBook.as_view(), name='checkout-book'),
    path('return/', ReturnBook.as_view(), name='return-book'),
] + router.urls