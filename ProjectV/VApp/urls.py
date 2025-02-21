
from django.conf import settings
from django.contrib import admin
from django.urls import path
from .views import *

from django.conf.urls.static import static
urlpatterns = [
   path('register/', RegisterUser.as_view(), name='register'),
#    path('login_auth/', DataLogin.as_view(), name='login_auth'),
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

   
    
   path('product_detail/', ProductDetail.as_view(), name='product_detail'),

   path('product_like/', ProductLikeAPIView.as_view(), name='product_like'),
 
   path('product_list/', ProductListView.as_view(), name='product_list'),
   # path('product_category/', ProductCategoryView.as_view(), name='product_category'),
   path('product_category_filter/', CategoriesProductFilterView.as_view(), name='product_category_filter'),

   # path('dicounted_product_list/', DiscountedProducts.as_view(), name='dicounted_product_list'),
   path('random_product_list/', RandomProductList.as_view(), name='random_product_list'),

   path('dicounted_product/', DiscountedDetailedProductView.as_view(), name='dicounted_product'),
   
   path('search_product/', ProductSearchView.as_view(), name='search_product'),
   path('search_dashboard/', SearchDashboardView.as_view(), name='search_dashboard'),







]# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
