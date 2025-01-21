from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PracticeUser

class CustomUserSerializer(serializers.Serializer):

    def create(self, validated_data):
        pass


    def update(self, instance, validated_data):
        pass

    def to_representation(self, instance):
        return {
            column.key: getattr(instance, column.key)
            for column in instance.__table__.columns
        }
        

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data):
        # Create a new User instance
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        user.set_password(validated_data['password'])  # We do not need to has here as django automatically does it for us
        user.save()
        return user

    def update(self, instance, validated_data):
        
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()
        return instance

    def to_representation(self, instance):
        # Custom representation of the object (optional)
        return {
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'password': instance.password  # Don't expose password in the response
        }


class NewPracticeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    roles = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        # Create a new PracticeUser instance
        return PracticeUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update an existing PracticeUser instance
        instance.roles = validated_data.get('roles', instance.roles)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.save()
        return instance

    def to_representation(self, instance):
        # Custom representation of the object (optional)
        return {
            'id': instance.id,
            'roles': instance.roles,
            'user_id': instance.user_id
        }