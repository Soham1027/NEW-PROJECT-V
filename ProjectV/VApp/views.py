import random
import re
import string
from django import views
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext as _, activate
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
from rest_framework.generics import ListAPIView
from django.db.models import Prefetch, Count
from django.db.models import Count, Prefetch, OuterRef, Subquery, Value, IntegerField, Q
from django.db.models.functions import Coalesce
from AdminPanel.models import *
from django.db.models.functions import Lower

from django.db.models import Q



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
        # 'current_language': getattr(user, 'current_language', None),
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
               

                return Response(data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 0, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LoginUser(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

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
        email = request.data.get('email')
        is_phone = request.query_params.get('is_phone', False)  # Properly get the query param

        if not email:
            return Response({
                'status': 0,
                'message': _('Email is required.')
            }, status=status.HTTP_400_BAD_REQUEST)

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
        email = request.data.get('email')
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
        user_email = request.data.get('email')

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
    



# class ProductDetail(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request, *args, **kwargs):
#         product_id = request.query_params.get('id')  # Get ID from query params
#         if not product_id:
#             return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             product = Product.objects.prefetch_related('images').get(id=product_id)
#             product.recently_viewed = timezone.localtime(timezone.now())
#             product.save()

#             serializer = ProductDetailSerializer(product)
#             return Response({
#                 'status': 1,
#                 'message': 'Product fetched successfully.',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
         
#         except Product.DoesNotExist:
#             return Response({
#                 'status': 0,
#                 'message': 'Product not found.',
#                 'errors': {}
#             }, status=status.HTTP_400_BAD_REQUEST)


# class ProductDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, *args, **kwargs):
#         product_id = request.query_params.get('id')  # Get ID from query params
#         if not product_id:
#             return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             product = Product.objects.prefetch_related('images', 'variants').get(id=product_id)
#             product.recently_viewed = timezone.localtime(timezone.now())
#             product.save()

#             serializer = ProductDetailSerializer(product)
            
#             # Fetch variants
#             variants = ProductVariant.objects.filter(product=product)
#             variants_data = [
#                 {
#                     "id": variant.id,
#                     "color": variant.color,
#                     "size": dict(ProductVariant.ITEM_SIZE_CHOICES).get(variant.size),
#                     "quantity": variant.quantity,
#                    "variant_images": [image.variant_image.url if image.variant_image else image.image.url for image in ProductImages.objects.filter(product_variants=variant)]
#                 }
#                 for variant in variants
#             ]
            
#             # Fetch product images separately
#             product_images = [image.image.url for image in ProductImages.objects.filter(product=product)]
            
#             return Response({
#                 'status': 1,
#                 'message': 'Product fetched successfully.',
#                 'data': serializer.data,
#                 # 'product_images': product_images,  # Now explicitly returning product images
#                 'variants': variants_data,
#             }, status=status.HTTP_200_OK)
         
#         except Product.DoesNotExist:
#             return Response({
#                 'status': 0,
#                 'message': 'Product not found.',
#                 'errors': {}
#             }, status=status.HTTP_400_BAD_REQUEST)

  


class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("id")  # Get ID from query params
        if not product_id:
            return Response(
                {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if the product has an active discount
            current_time=now()
            print(current_time)
            try:
                discount = ProductDiscount.objects.get(product__id=product_id,start_date__lte=current_time, end_date__gte=current_time)
                product = discount.product
                discounted_price = product.price - (
                    product.price * discount.discount_percentage / 100
                )
            except ProductDiscount.DoesNotExist:
                product = Product.objects.prefetch_related("images", "variants").get(
                    id=product_id
                )
                discounted_price = None

            product.recently_viewed = timezone.localtime(timezone.now())
            product.save()

            serializer = ProductDetailSerializer(product)

            # Fetch product variants
            variants = ProductVariant.objects.filter(product=product)
            variants_data = [
                {
                    "id": variant.id,
                    "color": variant.color,
                    "size": dict(ProductVariant.ITEM_SIZE_CHOICES).get(variant.size),
                    "quantity": variant.quantity,
                    "variant_images": [
                        image.variant_image.url if image.variant_image else image.image.url
                        for image in ProductImages.objects.filter(product_variants=variant,is_default=True)
                    ],
                }
                for variant in variants
            ]

            # Fetch product images separately
            product_images = [image.image.url for image in ProductImages.objects.filter(product=product)]

            response_data = {
                "id": product.id,
                "name": product.product_name,
                "price": float(product.price),
                "discounted_price": round(float(discounted_price), 2) if discounted_price else None,
                "discount": discount.discount_percentage if discounted_price else None,
                "color": product.color,
                "size": dict(Product.ITEM_SIZE_CHOICES).get(product.size) if product.size else None,
                "shoes_size": dict(Product.SHOES_SIZE_CHOICES).get(product.shoes_size)
                if product.shoes_size
                else None,
                "quantity": product.quantity,
                "category": product.category.category_name if product.category else None,
                "images": product_images,
                "variants": variants_data,
            }

            # Add discount details if applicable
            if discounted_price:
                response_data.update(
                    {
                        "start_date": discount.start_date.date(),
                        "end_date": discount.end_date.date(),
                        "start_time": discount.start_date.time(),
                        "end_time": discount.end_date.time(),
                    }
                )

            return Response(
                {
                    "status": 1,
                    "message": "Product fetched successfully.",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "status": 0,
                    "message": "Product not found.",
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

###################### Product LIKE ##################################
class ProductLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get('Language', 'en')
        if language in ['en', 'ar']:
            activate(language)

        # Get product ID from request data
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'status': 0,
                'message': _('Product ID is required.')
            }, status=400)

        # Validate if the product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'status': 0,
                'message': _('Product not found.')
            }, status=404)

        # Get user ID (defaults to authenticated user)
        created_by_id = request.data.get('created_by_id', request.user.id)

        # Validate liker (ensure user exists)
        try:
            liker = User.objects.get(id=created_by_id)
        except User.DoesNotExist:
            return Response({
                'status': 0,
                'message': _('Invalid user ID.')
            }, status=400)

        # Toggle Like/Unlike
        product_like, created = ProductLike.objects.get_or_create(
            created_by_id=created_by_id, products=product
        )

        if not created:
            # Unlike the product
            product_like.delete()
            message = _('Product unliked successfully.')
        else:
            # Like the product
            product_like.date_liked = timezone.localtime(timezone.now())
            product_like.save()
            message = _('Product liked successfully.')

        # Serialize product details
        # serializer = ProductDetailSerializer(product, context={'request': request})

        serialized_products=[]
      
        default_image = ProductImages.objects.filter(product=product, is_default=True).first()
        image_url = default_image.image.url if default_image else None

        product_data = {
            "id": product.id,
            "product_name": product.product_name,
            "price": str(product.price),  # Convert Decimal to string for JSON
            "description": product.description,
            "recently_viewed": product.recently_viewed,
            "image": image_url,
            'gender': product.gender,
            'size': product.size,
            'color': product.color,
            'category': product.category.category_name,
            'subcategory': product.subcategory.sub_category_name,
            'quantity': product.quantity,
            'item_view': product.item_view,
            
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            

            
        }
        serialized_products.append(product_data)

        return Response({
            'status': 1,
            'message': message,
            'data': serialized_products
        }, status=status.HTTP_200_OK)

        


class ProductListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Prefetch default images for optimization
        default_images_prefetch = Prefetch(
            "images",
            queryset=ProductImages.objects.filter(is_default=True),
            to_attr="default_images",
        )

        # Fetch recent products with default images
        recent_products = (
            Product.objects.prefetch_related(default_images_prefetch)
            .order_by("-recently_viewed")[:10]
        )

        # Fetch new products with default images
        new_products = (
            Product.objects.prefetch_related(default_images_prefetch)
            .order_by("-created_at")[:10]
        )


        popular_products = Product.objects.annotate(
            like_count=Coalesce(
                Subquery(
                    ProductLike.objects.filter(products=OuterRef("id"))
                    .values("products")
                    .annotate(like_count=Count("products"))
                    .values("like_count")
                ),
                Value(0),  # Default value if no likes exist
                output_field=IntegerField(),
            )
        ).prefetch_related(default_images_prefetch).order_by("-like_count")[:10]

        current_time = now()
        discounted_products = ProductDiscount.objects.filter(start_date__lte=current_time, end_date__gte=current_time)[:10]

        # Categorize products
        all_products = Product.objects.all()
        categorized_products = {"clothing": [], "shoes": [], "accessories": [], "bags": []}

        for product in all_products:
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None

            product_data = {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": image_url,
                'gender': product.gender,
                "size": product.get_size_display() if product.size else None,

                "shoes_size": product.get_shoes_size_display() if product.shoes_size else None,

                'color': product.color,
                'category': product.category.category_name,
                'subcategory': product.subcategory.sub_category_name,
                'quantity': product.quantity,
                'item_view': product.item_view,
              
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                  
            }

            if product.category:
                category_name = product.category.category_name.lower()
                if "shoes" in category_name:
                    categorized_products["shoes"].append(product_data)
                elif "accessory" in category_name or "accessories" in category_name:
                    categorized_products["accessories"].append(product_data)
                elif "bag" in category_name or "bags" in category_name:
                    categorized_products["bags"].append(product_data)
                else:
                    categorized_products["clothing"].append(product_data)

        # Format response for discounted products
        formatted_discounted_products = [
            {
                "id": discount.product.id,
                "name": discount.product.product_name,
                "price": float(discount.product.price),
                "discounted_price": round(float(discount.product.price - (discount.product.price * discount.discount_percentage / 100)), 2),
                "discount": discount.discount_percentage,
                "color": discount.product.color,
                "size": discount.product.get_size_display() if discount.product.size else None,
                "shoes_size": discount.product.get_shoes_size_display() if discount.product.shoes_size else None,
                "quantity": discount.product.quantity,
                "category": discount.product.category.category_name if discount.product.category else None,
                "image": ProductImages.objects.filter(product=discount.product, is_default=True).first().image.url if ProductImages.objects.filter(product=discount.product, is_default=True).exists() else None,
                "start_date": discount.start_date.date(),
                "end_date": discount.end_date.date(),
                "start_time": discount.start_date.time(),
                "end_time": discount.end_date.time(),
            }
            for discount in discounted_products
        ]


        # Fetch popular products
        # product_likes = (
        #     ProductLike.objects.values("products")
        #     .annotate(like_count=Count("products"))
        #     .order_by("-like_count")[:10]
        # )

        # # Extract product IDs for popular products
        # product_ids = [p["products"] for p in product_likes]

        # # Fetch popular products and prefetch default images
        # popular_products = ProductItem.objects.filter(id__in=product_ids).prefetch_related(default_images_prefetch)

        # # Create a mapping of product ID to like_count
        # like_count_map = {p["products"]: p["like_count"] for p in product_likes}

        # # Sort products manually based on like count
        # sorted_products = sorted(
        #     popular_products, key=lambda p: like_count_map.get(p.id, 0), reverse=True
        # )

        # Format response for popular products
        formatted_popular_products = [
            {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                # "default_images": [img.image.url for img in product.default_images],  # Access preloaded default images
                "image": ProductImages.objects.filter(product=product, is_default=True).first().image.url if ProductImages.objects.filter(product=product, is_default=True).exists() else None,

                'gender': product.gender,
                'size': product.size,
                "shoes_size": product.get_shoes_size_display() if product.shoes_size else None,

                'color': product.color,
                'category': product.category.category_name,
                'subcategory': product.subcategory.sub_category_name,
                'quantity': product.quantity,
                'item_view': product.item_view,
                
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "like_count": product.like_count,  
            }
            for product in popular_products
              
        ]

        # Format response for recent products
        formatted_recent_products = [
            {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": ProductImages.objects.filter(product=product, is_default=True).first().image.url if ProductImages.objects.filter(product=product, is_default=True).exists() else None,
  # Access preloaded default images
                'gender': product.gender,
                'size': product.size,
                "shoes_size": product.get_shoes_size_display() if product.shoes_size else None,

                'color': product.color,
                'category': product.category.category_name,
                'subcategory': product.subcategory.sub_category_name,
                'quantity': product.quantity,
                'item_view': product.item_view,
              
                "created_at": product.created_at,
                "updated_at": product.updated_at,
              
            }
            for product in recent_products
        ]

        # Format response for new products
        formatted_new_products = [
            {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": ProductImages.objects.filter(product=product, is_default=True).first().image.url if ProductImages.objects.filter(product=product, is_default=True).exists() else None,
                'gender': product.gender,
                'size': product.size,
                "shoes_size": product.get_shoes_size_display() if product.shoes_size else None,

                'color': product.color,
                'category': product.category.category_name if product.category else None,
                'subcategory': product.subcategory.sub_category_name if product.subcategory else None,
                'quantity': product.quantity,
                'item_view': product.item_view,
               
                "created_at": product.created_at,
                "updated_at": product.updated_at,
             
            }
            for product in new_products
        ]

        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": {
                    "recent_products": formatted_recent_products,
                    "new_products": formatted_new_products,
                    "popular_products": formatted_popular_products,
                    "discounted_products": formatted_discounted_products,
                    "categorized_products": categorized_products,
                },
            },
            status=status.HTTP_200_OK,
        )

# class ProductCategoryView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Set language preference
#         language = request.headers.get("Language", "en")
#         if language in ["en", "ar"]:
#             activate(language)

#         # Fetch all products
#         products = Product.objects.all()

#         # Categorize products
#         categorized_products = {
#             "clothing": [],
#             "shoes": [],
#             "accessories": [],
#             "bags": [],
           
#         }

#         for product in products:
#             # Get default product image
#             default_image = ProductImages.objects.filter(product=product, is_default=True).first()
#             image_url = default_image.image.url if default_image else None

#             product_data = {
#                 "id": product.id,
#                 "name": product.product_name,
#                 "price": float(product.price),
#                 "color": product.color,
#                 "size": product.get_size_display() if product.size else None,
#                 "shoes_size": product.get_shoes_size_display() if product.shoes_size else None,
#                 "quantity": product.quantity,
              
#                 "category": product.category.category_name if product.category else None,
#                 "image": image_url
#             }

#             if product.category:
#                 category_name = product.category.category_name.lower()

#                 if "shoes" in category_name:
#                     categorized_products["shoes"].append(product_data)
#                 elif "accessory" in category_name or "accessories" in category_name:
#                     categorized_products["accessories"].append(product_data)
#                 elif "bag" in category_name or "bags" in category_name:
#                     categorized_products["bags"].append(product_data)
#                 else:
#                     categorized_products["clothing"].append(product_data)
#             else:
#                 return Response(
#                     {
#                         "status": 0,
#                         "message": "There are no products.",
#                         "data": {},
#                     },
#                     status=status.HTTP_200_OK,
#                 )
                
#         return Response(
#             {
#                 "status": 1,
#                 "message": "Products fetched successfully.",
#                 "data": {
                  
#                     "products": categorized_products,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )

        


class CategoriesProductFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        category = request.query_params.get("category", "").strip().lower()
        sub_category = request.query_params.get("sub_category", "").strip().lower()
        gender=request.query_params.get("gender","").strip().lower()

        # Fetch products matching the category and subcategory

        products = Product.objects.filter(
            Q(category__category_name=category) |
            Q(subcategory__sub_category_name=sub_category) |
            Q(gender__iexact=gender)
        )

        
        # Serialize products and include default image
        serialized_products = []
        for product in products:
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None

            product_data = {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": image_url,
                'gender': product.gender,
                'size': product.size,
                'color': product.color,
                'category': product.category.category_name,
                'subcategory': product.subcategory.sub_category_name,
                'quantity': product.quantity,
                'item_view': product.item_view,
              
                "created_at": product.created_at,
                "updated_at": product.updated_at,
              
            }
            serialized_products.append(product_data)

        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": serialized_products,
            },
            status=status.HTTP_200_OK,
        )



# class DiscountedProducts(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Set language preference
#         language = request.headers.get("Language", "en")
#         if language in ["en", "ar"]:
#             activate(language)

#         # Get all discounted products where the discount is active
#         current_time = now()
#         print(current_time)
#         discounted_products = ProductDiscount.objects.filter(start_date__lte=current_time, end_date__gte=current_time)[:10]

#         response_data = []
#         for discount in discounted_products:
#             product = discount.product
#             default_image = ProductImages.objects.filter(product=product, is_default=True).first()
#             image_url = default_image.image.url if default_image else None

#             discounted_price = product.price - (product.price * discount.discount_percentage / 100)

#             response_data.append({
#                 "id": product.id,
#                 "name": product.product_name,
#                 "price": float(product.price),
#                 "discounted_price": round(float(discounted_price), 2),
#                 "discount": discount.discount_percentage,
#                 "color": product.color,
#                 "size": dict(Product.ITEM_SIZE_CHOICES).get(product.size) if product.size else None,
#                 "shoes_size": dict(Product.SHOES_SIZE_CHOICES).get(product.shoes_size) if product.shoes_size else None,
#                 "quantity": product.quantity,
#                 "category": product.category.category_name if product.category else None,
#                 "image": image_url,
#                 "start_date": discount.start_date.date(),
#                 "end_date": discount.end_date.date(),
#                 "start_time": discount.start_date.time(),
#                 "end_time": discount.end_date.time(),
#             })

      
#         return Response(
#             {
#                 "status": 1,
#                 "message": "Products fetched successfully.",
#                 "data": response_data,
#             },
#             status=status.HTTP_200_OK,
#         )


class RandomProductList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Fetch all products and shuffle them
        products = list(Product.objects.all())
        random.shuffle(products)

        if not products:
            return Response(
                {
                    "status": 0,
                    "message": "No products available.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serialized_products=[]
        for product in products:
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None

            product_data = {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),  # Convert Decimal to string for JSON
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": image_url,
                'gender': product.gender,
                'size': product.size,
                'color': product.color,
                'category': product.category.category_name,
                'subcategory': product.subcategory.sub_category_name,
                'quantity': product.quantity,
                'item_view': product.item_view,
              
                "created_at": product.created_at,
                "updated_at": product.updated_at,
              

                
            }
            serialized_products.append(product_data)
      

      

        # Serialize the products
        # serializer = ProductDetailSerializer(products, many=True)

        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": serialized_products,
            }
        )

class DiscountedDetailedProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Get all discounted products where the discount is active
        discount=request.query_params.get('discount')


        current_time = now()
        if discount:
            discounted_products = ProductDiscount.objects.filter(start_date__lte=current_time, end_date__gte=current_time,discount_percentage=discount)
            if not discounted_products or discount==0:
                return Response(
                    {
                        "status": 0,
                        "message": "No products available with this discount.",
                        "data": [],
                    }
                )
        else:
            discounted_products = ProductDiscount.objects.filter(start_date__lte=current_time, end_date__gte=current_time)
            if not discounted_products:
                return Response(
                    {
                        "status": 0,
                        "message": "Currently There is no Offer Available",
                        "data": [],
                    }
                )
        response_data = []
        print(discounted_products)
        for discount in discounted_products:
            product = discount.product
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None

            discounted_price = product.price - (product.price * discount.discount_percentage / 100)

            response_data.append({
                "id": product.id,
                "name": product.product_name,
                "price": float(product.price),
                "discounted_price": round(float(discounted_price), 2),
                "discount": discount.discount_percentage,
                "color": product.color,
                "size": dict(Product.ITEM_SIZE_CHOICES).get(product.size) if product.size else None,
                "shoes_size": dict(Product.SHOES_SIZE_CHOICES).get(product.shoes_size) if product.shoes_size else None,
                "quantity": product.quantity,
                "category": product.category.category_name if product.category else None,
                "image": image_url,
                "start_date": discount.start_date.date(),
                "end_date": discount.end_date.date(),
                "start_time": discount.start_date.time(),
                "end_time": discount.end_date.time(),
            })

        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": response_data,
            }
        )
        
        
class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        search_query = request.query_params.get("search", "").strip().lower()
        if not search_query:
            return Response(
                {
                    "status": 0,
                    "message": "Please provide a search query.",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        product_search=ProductSerach.objects.create(search=search_query)
        # Get all products that match the search query
        products = Product.objects.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__category_name__icontains=search_query) | Q(subcategory__sub_category_name=search_query))
        if not products:
            return Response(
                {
                    "status": 0,
                    "message": "No products found matching your search query.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        response_data = []
        for product in products:
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None
            response_data.append({
                "id": product.id,
                "product_name": product.product_name,
                "price": float(product.price),
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": image_url,
                "gender": product.gender,
                "size": product.size,
                "color": product.color,
                "category": product.category.category_name,
                "subcategory": product.subcategory.sub_category_name,
                "quantity": product.quantity,
                "item_view": product.item_view,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
          
            })

        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": response_data,
            }
        )

class SearchDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        search_queries = ProductSerach.objects.all()[:10]
       
        # products = Product.objects.filter(
        #     Q(product_name__icontains__in=search_queries) | 
        #     Q(description__icontains__in=search_queries) | 
        #     Q(category__category_name__icontains__in=search_queries) | 
        #     Q(subcategory__sub_category_name__icontains__in=search_queries)
        # )
        query = Q()
        for term in search_queries:
            print(term)
            query |= (
                Q(product_name__icontains=term) |
                Q(description__icontains=term) |
                Q(category__category_name__icontains=term) |
                Q(subcategory__sub_category_name__icontains=term)
            )
        products = Product.objects.filter(query)
        


        search_history = []
        recommandations=[]
        discover=[]
        for search_query in search_queries:
            search_history.append({
                "search_query": search_query.search,
                "timestamp": search_query.created_at,
            })
        
        for product in products:
                recommandations.append({
                    "id": product.id,
                    "category": product.category.category_name,
                })
                recommandations.append({
                    "id": product.id,
                    "subcategory": product.subcategory.sub_category_name,
                })
       
        for product in products:
            default_image = ProductImages.objects.filter(product=product, is_default=True).first()
            image_url = default_image.image.url if default_image else None
            discover.append({
                "id": product.id,
                "product_name": product.product_name,
                "price": float(product.price),
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": image_url,
                "gender": product.gender,
                "size": product.size,
                "color": product.color,
                "category": product.category.category_name,
                "subcategory": product.subcategory.sub_category_name,
                "quantity": product.quantity,
                "item_view": product.item_view,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
          
            })
          
               
        # for produ
        random.shuffle(recommandations)
        random.shuffle(discover)
        print(recommandations)

        return Response(
            {
                "status": 1,
                "message": "Search queries fetched successfully.",
                "data": {
                    "search_history": search_history,
                    "recommandations": recommandations,
                    "discover": discover,
                }
            }
        )
            



class ProductMainFilter(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Prefetch default images
        default_images_prefetch = Prefetch(
            "images",
            queryset=ProductImages.objects.filter(is_default=True),
            to_attr="default_images",
        )

        def parse_int_list(param):
            """Safely parse a comma-separated list of integers from query parameters."""
            values = request.query_params.get(param, "")
            return [int(x) for x in values.split(",") if x.strip().isdigit()]

        # Extract query parameters
        category_raw = request.query_params.get("category", "")
        category = [c.strip().lower() for c in category_raw.split(",") if c.strip()]

        sub_category_raw = request.query_params.get("sub_category", "")
        sub_category = [s.strip().lower() for s in sub_category_raw.split(",") if s.strip()]


     
        size_raw = request.query_params.get("size", "")
        size = [s.strip().lower() for s in size_raw.split(",") if s.strip()]

        shoes_size_raw = request.query_params.get("shoes_size", "")
        shoes_size = [s.strip().lower() for s in shoes_size_raw.split(",") if s.strip()]

        color_raw = request.query_params.get("color", "")
        color = [c.strip().lower() for c in color_raw.split(",") if c.strip()]


      
  
        price_min = request.query_params.get("price_min")
        price_max = request.query_params.get("price_max")
        sorting = request.query_params.get("sorting", "").strip().lower()

        # Filtering logic
        filters = Q()
        if category:
            filters &= Q(category__category_name__in=category)
        if sub_category:
            filters &= Q(subcategory__sub_category_name__in=sub_category)
        if size:
            filters &= Q(size__in=size)
        if shoes_size:
            filters &= Q(shoes_size__in=shoes_size)
        if color:
            filters &= Q(color__in=color)
        if price_min and price_min.isdigit():
            filters &= Q(price__gte=int(price_min))
        if price_max and price_max.isdigit():
            filters &= Q(price__lte=int(price_max))

        # Get filtered products
        products = Product.objects.filter(filters).prefetch_related(default_images_prefetch)
        print(products)

        # Shoes category validation (AFTER filtering)
        if "shoes" in category and not shoes_size:

            return Response(
                {"status": 0, "message": "Shoes size is required when category is 'shoes'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Apply sorting
        if sorting == "popular":
            products = products.annotate(
                like_count=Coalesce(
                    Subquery(
                        ProductLike.objects.filter(products=OuterRef("id"))
                        .values("products")
                        .annotate(like_count=Count("products"))
                        .values("like_count")
                    ),
                    Value(0),
                    output_field=IntegerField(),
                )
            ).order_by("-like_count")

        elif sorting == "new":
            products = products.order_by("-created_at")

        elif sorting == "price_high_to_low":
            products = products.order_by("-price")

        elif sorting == "price_low_to_high":
            products = products.order_by("price")

        # Serialize products
        serialized_products = [
            {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": product.default_images[0].image.url if product.default_images else None,
                "gender": product.gender,
                "size": product.size,
                "color": product.color,
                "category": product.category.category_name,
                "subcategory": product.subcategory.sub_category_name,
                "quantity": product.quantity,
                "item_view": product.item_view,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                # "like_count": product.like_count  if sorting == "popular" else None,
            }
            for product in products
        ]

        if  sorting == "popular":
             serialized_products = [
            {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),
                "description": product.description,
                "recently_viewed": product.recently_viewed,
                "image": product.default_images[0].image.url if product.default_images else None,
                "gender": product.gender,
                "size": product.size,
                "color": product.color,
                "category": product.category.category_name,
                "subcategory": product.subcategory.sub_category_name,
                "quantity": product.quantity,
                "item_view": product.item_view,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "like_count": product.like_count,
            }
            for product in products
        ]


        return Response(
            {
                "status": 1,
                "message": "Products fetched successfully.",
                "data": serialized_products,
            },
            status=status.HTTP_200_OK,
        )



class PurchaseProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Extract data from request
        product_id = request.data.get("product_id")
        product_variant_id = request.data.get("product_variant_id", None)
        quantity = request.data.get("quantity")
        color = request.data.get("color")
        size = request.data.get("size", None)
        shoes_size = request.data.get("shoes_size", None)

        # Validate required fields
        if not product_id or not quantity or not color:
            return Response(
                {"status": 0, "message": "Product ID, quantity, and color are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch product
            product = Product.objects.get(id=product_id)

            # Ensure sufficient stock in the main product (if variant not used)
            if not product_variant_id:
                if int(product.quantity) < int(quantity):
                    return Response(
                        {"status": 0, "message": "Not enough quantity in stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if product.quantity == 0:
                    return Response(
                        {"status": 0, "message": "Product out of stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Handle category-specific validation
            if product.category.category_name.lower() == "shoes":
                if not shoes_size:
                    return Response(
                        {"status": 0, "message": "Shoes size is required when category is 'Shoes'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                size = None  # Ensure size is not used for shoes

            # If variant ID is provided, fetch the variant
            if product_variant_id:
                try:
                    variant = ProductVariant.objects.get(
                        id=product_variant_id)
                    print(variant.quantity)
                   

                    # Check variant stock
                    if int(variant.quantity) < int(quantity):
                        return Response(
                            {"status": 0, "message": "Not enough quantity in stock for this variant."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if variant.quantity == 0:
                        return Response(
                            {"status": 0, "message": "Product variant out of stock."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Reduce stock
                    variant.quantity -= int(quantity)
                    variant.save()

                    # Save purchase record
                    PurchasedProduct.objects.create(
                        product=product,
                        product_variant=variant,
                        quantity=quantity,
                        color=color,
                        size=size,
                        shoes_size=shoes_size,
                    )

                    return Response(
                        {"status": 1, "message": "Product variant purchased successfully."},
                        status=status.HTTP_200_OK,
                    )

                except ProductVariant.DoesNotExist:
                    return Response(
                        {"status": 0, "message": "Product variant not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # If no variant ID, process main product purchase
            product.quantity -= int(quantity)
            product.save()

            # Save purchase record
            PurchasedProduct.objects.create(
                product=product,
                product_variant=None,
                quantity=quantity,
                color=color,
                size=size,
                shoes_size=shoes_size,
            )

            return Response(
                {
                    "status": 1,
                    "message": "Products fetched successfully.",
                    # "data": ,
                },
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {"status": 0, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )




class PurchaseDiscountedProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Set language preference
        language = request.headers.get("Language", "en")
        if language in ["en", "ar"]:
            activate(language)

        # Extract data from request
        product_id = request.data.get("product_id")
        product_variant_id = request.data.get("product_variant_id")
        quantity = request.data.get("quantity")
        color = request.data.get("color")
        size = request.data.get("size")
        shoes_size = request.data.get("shoes_size")

        # Validate required fields
        if not product_id or not quantity or not color:
            return Response(
                {"status": 0, "message": "Product ID, quantity, and color are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch product
            product = Product.objects.get(id=product_id)

            # Check if the product has an active discount
            active_discount = ProductDiscount.objects.filter(
                product=product,
                start_date__lte=now(),
                end_date__gte=now()
            ).order_by('-discount_percentage').first()

            discount_percentage = int(active_discount.discount_percentage) if active_discount else 0
            original_price = int(product.price)
            discounted_price = original_price * (1 - discount_percentage / 100)

            # Ensure sufficient stock in the main product (if variant not used)
            if not product_variant_id:
                if int(product.quantity) < int(quantity):
                    return Response(
                        {"status": 0, "message": "Not enough quantity in stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if product.quantity == 0:
                    return Response(
                        {"status": 0, "message": "Product out of stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Handle category-specific validation
            if product.category.category_name.lower() == "shoes" and not shoes_size:
                return Response(
                    {"status": 0, "message": "Shoes size is required when category is 'Shoes'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If variant ID is provided, fetch the variant
            if product_variant_id:
                try:
                    variant = ProductVariant.objects.get(id=product_variant_id,product__id=product.id)

                    # Check variant stock
                    if int(variant.quantity) < int(quantity):
                        return Response(
                            {"status": 0, "message": "Not enough quantity in stock for this variant."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if variant.quantity == 0:
                        return Response(
                            {"status": 0, "message": "Product variant out of stock."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Reduce stock
                    variant.quantity -= int(quantity)
                    variant.save()

                    # Save purchase record
                    PurchasedProduct.objects.create(
                        product=product,
                        product_variant=variant,
                        quantity=quantity,
                        color=color,
                        size=None,  # Ensuring size is not used for shoes
                        shoes_size=shoes_size,
                    )

                    response_data = {
                        "status": 1,
                        "message": "Product variant purchased successfully.",
                        "data": {
                            "id": product.id,
                            "name": product.product_name,
                            "price": original_price,
                            "discounted_price": round(discounted_price, 2) if active_discount else None,
                            "discount": discount_percentage if active_discount else None,
                            "color": product.color,
                            "size": dict(Product.ITEM_SIZE_CHOICES).get(product.size) if product.size else None,
                            "shoes_size": dict(Product.SHOES_SIZE_CHOICES).get(product.shoes_size) if product.shoes_size else None,
                            "quantity": product.quantity,
                            "category": product.category.category_name if product.category else None,
                            "variant": {
                                "variant_id": variant.id,
                                "variant_color": variant.color,
                                "variant_size": variant.size,
                                "variant_shoes_size": variant.shoes_size,
                                "variant_price": float(variant.product.price),
                                "variant_discounted_price": round(discounted_price, 2) if active_discount else None,
                                "variant_quantity": variant.quantity,
                            },
                        },
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

                except ProductVariant.DoesNotExist:
                    return Response(
                        {"status": 0, "message": "Product variant not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # If no variant ID, process main product purchase
            product.quantity -= int(quantity)
            product.save()

            # Save purchase record
            PurchasedProduct.objects.create(
                product=product,
                product_variant=None,
                quantity=quantity,
                color=color,
                size=size,
                shoes_size=shoes_size,
            )

            response_data = {
                "status": 1,
                "message": "Product purchased successfully.",
                "data": {
                    "id": product.id,
                    "name": product.product_name,
                    "price": original_price,
                    "discounted_price": round(discounted_price, 2) if active_discount else None,
                    "discount": discount_percentage if active_discount else None,
                    "color": product.color,
                    "size": dict(Product.ITEM_SIZE_CHOICES).get(product.size) if product.size else None,
                    "shoes_size": dict(Product.SHOES_SIZE_CHOICES).get(product.shoes_size) if product.shoes_size else None,
                    "quantity": product.quantity,
                    "category": product.category.category_name if product.category else None,
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {"status": 0, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
