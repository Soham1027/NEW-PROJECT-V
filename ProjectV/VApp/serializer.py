from datetime import datetime
from .models import *
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from AdminPanel.models import *

class PaymentCardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment cards (POST)"""

    class Meta:
        model = PaymentCard
        fields = ['card_number', 'card_holder_name', 'expiration_date', 'cvv', 'is_default']

    



class PaymentCardRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving payment cards (GET)"""
    masked_card_number = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCard
        fields = ['masked_card_number', 'card_holder_name', 'expiration_date', 'cvv', 'is_default', 'created_at', 'updated_at']

    def get_masked_card_number(self, obj):
        return "**** **** **** " + obj.card_number[-4:]
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['expiration_date']=instance.expiration_date.strftime('%m-%y')
        ret['created_at']=instance.created_at.strftime('%Y-%m-%d')
        ret['updated_at']=instance.updated_at.strftime('%Y-%m-%d')
        
   
        return ret
    
# Serializer for product items
class ProductItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductItem
        fields = ['product_name', 'price', 'image']

    def get_image(self, obj):
        # Get the default image related to this product
        default_image = obj.images.filter(is_default=True).first()
        if default_image:
            return default_image.image.url
        return None
    


class ProductDetailImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ['image']

class ProductVariantSerializer(serializers.ModelSerializer):
    size_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['color', 'size', 'size_display', 'quantity']

    def get_size_display(self, obj):
        return dict(ProductVariant.ITEM_SIZE_CHOICES).get(obj.size)

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductDetailImageSerializer(many=True, read_only=True)
    variations = ProductVariantSerializer(many=True, read_only=True, source='variants')

    class Meta:
        model = ProductItem
        fields = ['id', 'product_name', 'price', 'description', 'images', 'variations']
