import random
import re
import string
from django import views
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTPSave  # Assuming these models exist
from .serializer import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from ProjectV.settings import *
from django.utils.crypto import get_random_string
from django.core.files.storage import default_storage
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
  

    @csrf_exempt
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
                if profile_picture:
                    file_extension = profile_picture.name.split('.')[-1]
                    unique_suffix = get_random_string(8)
                    file_name = f"profile_pics/{user.id}_{unique_suffix}.{file_extension}"
                    path = default_storage.save(file_name, profile_picture)
                    user.profile_picture = path
                    user.save()

                # Generate OTP and store it
                # otp = generate_otp()
                # OTPSave.objects.update_or_create(phone=phone, defaults={'OTP': otp})
                refresh = RefreshToken.for_user(user)

        # Prepare the response data
                data = {
                    'status': 1,
                    'message': 'User Register successfully.',
                    'data': {
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token),
                        'user': get_user_data(user, request),
                    }
                }

                return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataLogin(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Validate email format
        if not email:
            return Response({
                'status': 0,
                'message': _('Email is required.')
            }, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'status': 0, 'message': _('User not found.')}, status=status.HTTP_400_BAD_REQUEST)
        
        # Simple email validation regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({
                'status': 0,
                'message': _('Invalid email format.')
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Here you can perform any database operations if needed
                request.session['user_email'] = email
                return Response({
                    'status': 1,
                
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUser(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        email = request.session.get('user_email')
        password = request.data.get('password')

        # Validate required fields
        if not password:
            return Response({
                'status': 0,
                'message': _('password is required.')
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if user is None:
                return Response({
                    'status': 0,
                    'message': _('Invalid email or password.')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Log the user in
            auth_login(request, user)

                # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Prepare the response data
            data = {
                'status': 1,
                'message': 'User logged in successfully.',
                'data': {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'user': get_user_data(user, request),
                }
            }

            return Response(data, status=status.HTTP_200_OK)


          

        except Exception as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class LogoutUser(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            # Log the user out
            auth_logout(request)

            return Response({
                'status': 1,
                'message': _('User logged out successfully.')
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Class for Sending OTP
class SendOTP(APIView):
    permission_classes = [AllowAny]

    
    def post(self, request, *args, **kwargs):
        # Get the email from the session
        email = request.session.get('user_email')
        is_phone = request.query_params.get('is_phone', False)  # Properly get the query param

        if not email:
            return Response({'status': 0, 'message': _('User not logged in.')}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user associated with the email
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'status': 0, 'message': _('User not found.')}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()  # Generate OTP once and reuse

        if is_phone:
            phone = user.phone  # Get the phone number from the user record
            if not phone:
                return Response({'status': 0, 'message': _('Phone number is required.')}, status=status.HTTP_400_BAD_REQUEST)

            # Save OTP for phone
            OTPSave.objects.update_or_create(phone=phone, defaults={'OTP': otp})

            # Here, integrate with an SMS service to send the OTP to the phone

            return Response({
                'status': 1,
                'message': _('OTP sent successfully via SMS.'),
                'otp': otp  # For development/debugging, remove in production
            }, status=status.HTTP_200_OK)
        else:
            # Save OTP for email
            OTPSave.objects.update_or_create(email=email, defaults={'OTP': otp})

            # Send OTP email
            try:
                send_mail(
                    _('Your OTP Code'),  # Subject of the email
                    f'Your OTP code is: {otp}',  # Body of the email
                    DEFAULT_FROM_EMAIL,  # From email (configured in settings)
                    [email],  # To email
                    fail_silently=False,  # Fail loudly for debugging
                )
            except Exception:
                return Response({'status': 0, 'message': _('Failed to send OTP email.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'status': 1,
                'message': _('OTP sent successfully via email.'),
                'otp': otp  # For development/debugging, remove in production
            }, status=status.HTTP_200_OK)

# # Class for Verifying OTP and Completing Registration

class VerifyOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get necessary data from request
        email = request.session.get('user_email')
        is_phone = request.query_params.get('is_phone', False)  # Properly get the query param
        otp_input = request.data.get("otp")

        # Validate OTP input
        if not otp_input:
            return Response({'status': 0, 'message': _('OTP is required.')}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email session
        if not email:
            return Response({'status': 0, 'message': _('User not registered.')}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user associated with the email
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'status': 0, 'message': _('User not found.')}, status=status.HTTP_400_BAD_REQUEST)

        # Determine whether to verify phone or email
        if is_phone:
            phone = user.phone  # Get the phone number from the user record

            if not phone:
                return Response({'status': 0, 'message': _('User does not have a registered phone number.')},
                                status=status.HTTP_400_BAD_REQUEST)

            filter_params = {'phone': phone}
            success_message = _('Phone number verified successfully.')
        else:
            filter_params = {'email': email}
            success_message = _('Email verified successfully.')

        # Validate OTP
        try:
            otp_record = OTPSave.objects.get(**filter_params, OTP=otp_input)
        except OTPSave.DoesNotExist:
            return Response({'status': 0, 'message': _('Invalid OTP.')}, status=status.HTTP_400_BAD_REQUEST)

        # Delete OTP record after successful verification
        otp_record.delete()

        return Response({
            'status': 1,
            'message': success_message,
        }, status=status.HTTP_200_OK)


class ForgotPasswordAPIView(APIView):
   
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Get the email from the session
        user_email = request.session.get('user_email')

        if not user_email:
            return Response({
                'status': 0,
                'message': _('User not logged in.'),
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get new passwords from request data
        new_password = request.data.get('new_password')
        new_password_1 = request.data.get('new_password_1')

        if not new_password or not new_password_1:
            return Response({
                'status': 0,
                'message': _('Both password fields are required.'),
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user based on the email in the session
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({
                'status': 0,
                'message': _('User not found.'),
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password
        if len(new_password) < 8 or len(new_password_1) < 8:
            return Response({
                'status': 0,
                'message': _('New password must be at least 8 characters long.'),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != new_password_1:
            return Response({
                'status': 0,
                'message': _('New passwords do not match.'),
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update the password
        user.password = make_password(new_password)
        user.save()
        request.session.clear()

        return Response({
            'status': 1,
            'message': _('Password changed successfully.'),
        }, status=status.HTTP_200_OK)
    


class EditUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def patch(self, request, *args, **kwargs):  
        user = request.user

        try:
            # Fetch user instance
            user_data = User.objects.get(id=user.id)

            # Always update username, if provided
            username = request.data.get('username')
            if username:
                user_data.username = username

            # Always update phone, if provided
            phone = request.data.get('phone')
            if phone:
                user_data.phone = phone

            # Always update email, if provided
            email = request.data.get('email')
            if email:
                user_data.email = email

            # Always update password, if provided
            password = request.data.get('password')
            if password:
                user_data.set_password(password)

            # Handle profile picture update if provided
            if "profile_picture" in request.FILES:
                profile_picture = request.FILES["profile_picture"]
                old_profile_picture = user_data.profile_picture

                # Remove old profile picture if it exists
                if old_profile_picture:
                    old_picture_path = os.path.join(settings.MEDIA_ROOT, str(old_profile_picture))
                    if os.path.isfile(old_picture_path):
                        os.remove(old_picture_path)

                # Generate a unique file name for new profile picture
                file_extension = profile_picture.name.split('.')[-1]
                unique_suffix = get_random_string(8)
                file_name = f"profile_pics/{user.id}_{unique_suffix}.{file_extension}"

                # Save the new profile picture
                path = default_storage.save(file_name, profile_picture)
                user_data.profile_picture = path

            # Save updated user details immediately
            user_data.save()

            # Return updated user data in the response
            return Response({'status': 1, 'message': 'Profile updated successfully.', 'user': get_user_data(user_data, request)}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'status': 0, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PaymentCardView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def get(self, request, *args, **kwargs):
        cards = PaymentCard.objects.all()
        if not cards:
            return Response({
                'status': 0,
                'message': 'No payment cards found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentCardRetrieveSerializer(cards, many=True)
        return Response({
            'status': 1,
            'message': 'Payment cards retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PaymentCardCreateSerializer(data=request.data)
     
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 1,
                'message': 'Payment card created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 0,
            'message': 'Validation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        # Retrieve the card ID from the GET parameters
        card_id = request.data.get('id')
        
        if not card_id:
            return Response({
                'status': 0,
                'message': 'Card ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Fetch the payment card using the ID from GET parameters
            card = PaymentCard.objects.get(id=card_id)
        except PaymentCard.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Payment card not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentCardCreateSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            # Update the card information
            serializer.save()
            return Response({
                'status': 1,
                'message': 'Payment card updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 0,
            'message': 'Validation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
