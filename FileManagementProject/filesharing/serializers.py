from rest_framework import serializers
from .models import User, File
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import hashlib
import base64

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_ops_user')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_ops_user')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        sha256_hash = hashlib.sha256()
        sha256_hash.update(validated_data['username']+validated_data['password'].encode('utf-8'))
        db_hash_digest = sha256_hash.hexdigest()
        if validated_data['is_ops_user']:
            user.is_ops_user = True
        user.save()

        
        # Generate verification URL
        verification_token = hashlib.sha256(user.email.encode()).hexdigest()
        verification_url = f"{settings.SITE_URL}/verify-email/{verification_token}"
        
        # Send verification email
        send_mail(
            'Verify your email',
            f'Please verify your email using the following link: {verification_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    sha256_hash = hashlib.sha256()
    sha256_hash.update(username+password.encode('utf-8'))
    req_hash_digest = sha256_hash.hexdigest()
    

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'file', 'upload_time', 'uploaded_by')