
from django.conf import settings
from django.contrib import admin
from django.urls import path
from .views import *

from django.conf.urls.static import static
urlpatterns = [
   path('register/', RegisterUser.as_view(), name='register'),
   path('login_auth/', DataLogin.as_view(), name='login_auth'),
   path('login/', LoginUser.as_view(), name='login'),

   path('logout/', LogoutUser.as_view(), name='logout'),

    # OTP Sending (for existing users or after registration)
    path('send_otp/', SendOTP.as_view(), name='send_otp'),

    # OTP Verification and Registration completion
    path('verify_otp/', VerifyOTP.as_view(), name='verify_otp'),
    path('forgot_password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),

    # API endpoints for user's data
    path('edit_user/', EditUserProfile.as_view(), name='edit_user'),

    path('payment_card/', PaymentCardView.as_view(), name='payment-card-list'),

    # Update a payment card using GET parameter 'id'
    path('payment_card_update/', PaymentCardView.as_view(), name='payment-card-update'),


]# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
