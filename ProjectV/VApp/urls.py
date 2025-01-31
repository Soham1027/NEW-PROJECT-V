
from django.contrib import admin
from django.urls import path
from .views import *

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

]
