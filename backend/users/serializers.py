# Path: backend/users/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the custom User model."""
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'designation', 'phone_number', 'is_active', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        """
        Create a new user, ensuring the password is properly hashed.
        """
        # Use create_user to handle password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'viewer'),
            designation=validated_data.get('designation', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user

    def update(self, instance, validated_data):
        """
        Update an existing user, with special handling for the password.
        """
        # Update standard fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.role = validated_data.get('role', instance.role)
        instance.designation = validated_data.get('designation', instance.designation)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
          
        # Update password if provided
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
              
        instance.save()
        return instance