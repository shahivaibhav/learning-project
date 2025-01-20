from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PracticeUser

class CustomUserSerializer(serializers.Serializer):
    class Meta:
        def create(self, validated_data):
            pass


        def update(self, instance, validated_data):
            pass

        def to_representation(self, instance):
            return {
                column.key: getattr(instance, column.key)
                for column in instance.__table__.columns
            }
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','password']
        extra_kwargs = {
            'password' : {'write_only' : True}
        }

class NewPracticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeUser
        fields = ['id', 'roles']