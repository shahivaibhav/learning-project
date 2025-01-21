from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import PracticeUser
from .serializers import UserSerializer, NewPracticeSerializer
from .services import Sessionhelper
from rest_framework.authentication import SessionAuthentication , BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login

class RegisterView(APIView):

    def post(self, request, *args, **kwargs):
        practice_user_data = request.data

        if User.objects.filter(username=practice_user_data['username']).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(data=practice_user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            # Create new PracticeUser
            session = Sessionhelper.create_session()
            remaining_user_data = {
                'roles': practice_user_data.get('roles', ''),
                'user_id': user.id,
            }
            new_user = PracticeUser(**remaining_user_data)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return Response({
                "user_id": user.id,
                "practice_user_id": new_user.id,
                "message": "User and Practice User are linked up!"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            session = Sessionhelper.create_session()

            # Query the PracticeUser using SQLAlchemy
            practice_user = session.query(PracticeUser).filter_by(user_id=user.id).first()

            if not practice_user:
                return Response({"error": "PracticeUser not found"}, status=status.HTTP_404_NOT_FOUND)

            
            role = practice_user.roles
            
            
            return Response({"message": "Login successful", "role": role})

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class PracticeUserViewSet(viewsets.ViewSet):
    
    def list(self, request, *arg, **kwargs):

        session = Sessionhelper.create_session()
        practice_user = session.query(PracticeUser).all()
        print(practice_user)
        serializer = NewPracticeSerializer(practice_user, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):

        session = Sessionhelper.create_session()

        practice_user_data = request.data
        print(practice_user_data)
        user_serializer = UserSerializer(data=practice_user_data)

        if user_serializer.is_valid():
            user = user_serializer.save()
            remaining_user_data = {
                'roles': practice_user_data.get('roles', ''),  # Default to an empty string if role is missing
                'user_id': user.id,
            }

            new_user = PracticeUser(**remaining_user_data)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return Response({
                "user_id" : user.id,
                "practice_user_id" : new_user.id,
                "message" : "User and Practice User are linked up!"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        
   