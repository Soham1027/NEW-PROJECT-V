from datetime import datetime
from .models import *
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


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
    
    