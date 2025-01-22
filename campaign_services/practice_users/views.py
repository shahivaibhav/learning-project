 
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import PracticeUser
from .serializers import UserSerializer, NewPracticeSerializer
from .services import Sessionhelper
 
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from .models import auth_user
from django.contrib.auth.hashers import make_password, check_password


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .models import auth_user
from .services import Sessionhelper

class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a session using your custom session helper
        session = Sessionhelper.create_session()
        data = request.data
        username = data.get('username')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if the user exists in the auth_user table
        user = session.query(auth_user).filter_by(username=username).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current password is correct using Django's check_password
        if not check_password(current_password, user.password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the new password and confirm password match
        if new_password != confirm_password:
            return Response({"error": "New password and confirm password do not match"}, status=status.HTTP_400_BAD_REQUEST)

        # Hash the new password using Django's make_password (automatically handles salting)
        hashed_new_password = make_password(new_password)

        # Check if the new password is the same as the old one
        if check_password(new_password, user.password):
            return Response({"error": "New password cannot be the same as the old password"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password in the database
        session.query(auth_user).filter_by(username=username).update({"password": hashed_new_password})
        session.commit()

        # Close the session after making changes
        session.close()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)



class RegisterView(APIView):

    def post(self, request, *args, **kwargs):
        practice_user_data = request.data

        if User.objects.filter(username=practice_user_data['username']).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=practice_user_data['email']).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

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
        
   