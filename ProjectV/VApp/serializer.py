from .models import *
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    profile_picture = serializers.ImageField(required=True, allow_null=True)  # ✅ Add profile_picture

    class Meta:
        model = User
        fields = ['profile_picture', 'email', 'phone', 'password']

    def validate(self, data):
        errors = {}

        if 'email' in data and User.objects.filter(email=data['email']).exists():
            errors['username'] = _("Email already exists.")
        if 'phone' in data and User.objects.filter(phone=data['phone']).exists():
            errors['phone'] = _("Phone number already exists.")

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        profile_picture = validated_data.get('profile_picture', None)

        user = User(
            email=validated_data['email'],
            phone=validated_data['phone'],
            profile_picture=profile_picture
        )
        user.set_password(validated_data['password'])  # ✅ Hash password
        user.save()
        return user
