
from django.conf import settings
from django.contrib import admin
from django.urls import path
from .views import *

from django.conf.urls.static import static
urlpatterns = [
     
    # signup
    path('Adminlogin/', LoginUser.as_view(), name='Adminlogin'),
 
    path('dashboard/', Home.as_view(), name='dashboard'),
    path('product_create/', ProductCreateView.as_view(), name='product_create'),
    path('product_variant_create/', ProductVariantCreateView.as_view(), name='product_variant_create'),

    



]# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
