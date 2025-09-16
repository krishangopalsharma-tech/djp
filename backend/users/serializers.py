from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Define the fields to be exposed in the API
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'designation', 'is_active', 'password')
        # Make the password write-only so it is not sent back in API responses
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        # Use Django's create_user method to ensure the password is properly hashed
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'viewer'),
            designation=validated_data.get('designation', '')
        )
        return user

    def update(self, instance, validated_data):
        # Allow username (PF Number) to be updated
        instance.username = validated_data.get('username', instance.username)
        
        # Handle regular field updates
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.role = validated_data.get('role', instance.role)
        instance.designation = validated_data.get('designation', instance.designation)
        instance.is_active = validated_data.get('is_active', instance.is_active)
          
        # Handle password updates separately to ensure hashing
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
              
        instance.save()
        return instance
