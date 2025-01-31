import random
import string
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTPSave  # Assuming these models exist

# Helper function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Helper function to return user data
def get_user_data(user, request):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        # 'device_type': user.device_type,
        # 'device_token': user.device_token,
        'current_language': getattr(user, 'current_language', None),
    }

# Class for User Registration
class RegisterUser(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        profile_picture = request.data.get('profile_picture')
        # device_type = request.data.get('device_type')
        # device_token = request.data.get('device_token')

        # Validate required fields
        if not email or not phone or not password or not profile_picture:
            return Response({
                'status': 0,
                'message': _('Email, phone, password, and profile picture are required.')
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email or phone already exists
        if User.objects.filter(email=email).exists():
            return Response({'status': 0, 'message': _('Email already taken.')}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone=phone).exists():
            return Response({'status': 0, 'message': _('Phone number already in use.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    phone=phone,
                    profile_picture=profile_picture,
                    # device_type=device_type,
                    # device_token=device_token
                )
                user.set_password(password)
                user.save()

                # Generate OTP and store it
                # otp = generate_otp()
                # OTPSave.objects.update_or_create(phone=phone, defaults={'OTP': otp})

                return Response({
                    'status': 1,
                    'message': _('User registered successfully. OTP sent to phone.'),
                    # 'otp': otp  # For development/debugging
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Class for Sending OTP
# class SendOTP(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         phone = request.data.get('phone')

#         if not phone:
#             return Response({'status': 0, 'message': _('Phone number is required.')}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if phone exists
#         if not User.objects.filter(phone=phone).exists():
#             return Response({'status': 0, 'message': _('Phone number not found.')}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate OTP
#         otp = generate_otp()
#         OTPSave.objects.update_or_create(phone=phone, defaults={'OTP': otp})

#         return Response({
#             'status': 1,
#             'message': _('OTP sent successfully.'),
#             'otp': otp  # For development/debugging
#         }, status=status.HTTP_200_OK)


# # Class for Verifying OTP and Completing Registration
# class VerifyOTP(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         phone = request.data.get("phone")
#         otp_input = request.data.get("otp")

#         if not phone or not otp_input:
#             return Response({'status': 0, 'message': _('Phone and OTP are required.')}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             otp_record = OTPSave.objects.get(phone=phone, OTP=otp_input)
#         except OTPSave.DoesNotExist:
#             return Response({'status': 0, 'message': _('Invalid OTP.')}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if user exists
#         user = User.objects.filter(phone=phone).first()
#         if not user:
#             return Response({'status': 0, 'message': _('User not found.')}, status=status.HTTP_400_BAD_REQUEST)

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         # Delete OTP record after successful verification
#         otp_record.delete()

#         return Response({
#             'status': 1,
#             'message': _('Phone number verified successfully.'),
#             'data': {
#                 'refresh_token': str(refresh),
#                 'access_token': str(refresh.access_token),
#                 'user': get_user_data(user, request),
#             }
#         }, status=status.HTTP_200_OK)
