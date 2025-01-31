
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
   path('register/', RegisterUser.as_view(), name='register'),

    # OTP Sending (for existing users or after registration)
    # path('send-otp/', SendOTP.as_view(), name='send_otp'),

    # # OTP Verification and Registration completion
    # path('verify-otp/', VerifyOTP.as_view(), name='verify_otp'),
]
