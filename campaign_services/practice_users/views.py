 
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import PracticeUser, NewPractices, engine
from .serializers import UserSerializer, NewPracticeSerializer,LoginSerializer
from .services import Sessionhelper
from sqlalchemy import Table, MetaData
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from .models import auth_user
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.tokens import RefreshToken
from sqlalchemy import select

metadata = MetaData()
auth_user = Table(
        'auth_user', metadata, autoload_with = engine
)


def session_status(request):
    if request.user.is_authenticated:
        return JsonResponse({"active": True}, status=200)
    return JsonResponse({"active": False}, status=400)
    
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)  # Log out and clear session
    return JsonResponse({"message": "Logged out successfully"}, status=200)


class GetUserRoleView(APIView):
    def post(self, request):
        # Assuming 'username' is passed in the request (or you can get it from the request headers, etc.)
        username = request.user.username  # or you can get username from request.query_params if needed
        
        if username:
            # Query the model to check if username exists
            user = User.objects.filter(username=username).first()
            if user:
                # User exists, check the role
                session = Sessionhelper.create_session()
                practice_user = session.query(PracticeUser).filter_by(user_id=user.id).first()
                if practice_user is not None:
                    return Response({"message": "Get user role successfully", "role": practice_user.roles}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Practice User not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Username not provided"}, status=status.HTTP_400_BAD_REQUEST)

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
    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username', "")
            password = serializer.validated_data.get('password', "")

            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                session = Sessionhelper.create_session()
                role = None
                practice_user = session.query(PracticeUser).filter_by(user_id=user.id).first()

                if practice_user:
                    role = practice_user.roles
                    email = user.email
                return Response({
                    "refresh": str(refresh), "access": str(refresh.access_token), 
                    "role" : role,
                    "email" : email,
                    "message ": "Login successfull"})
                
            
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        is_new_practice = practice_user_data.get("is_new_practice", True)  # Default is new practice

        user_serializer = UserSerializer(data=practice_user_data)

        if user_serializer.is_valid():
            user = user_serializer.save()

            if is_new_practice:
                # Create new practice user (Already implemented)
                remaining_user_data = {
                    "roles": practice_user_data.get("roles", ""),  
                    "user_id": user.id,
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
                # Associate with an existing practice
                existing_practice_id = practice_user_data.get("existing_practice_id")
                
                if not existing_practice_id:
                    return Response({"error": "existing_practice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

                # Validate if practice exists
                existing_practice = session.query(PracticeUser).filter_by(id=existing_practice_id).first()
                if not existing_practice:
                    return Response({"error": "Invalid existing practice ID"}, status=status.HTTP_404_NOT_FOUND)

                # Link user to existing practice
                new_association = NewPractices(existing_user_id=user.id)
                session.add(new_association)
                session.commit()
                session.refresh(new_association)

                return Response({
                    "user_id": user.id,
                    "existing_practice_id": existing_practice_id,
                    "association_id": new_association.id,
                    "message": "User associated with existing practice!"
                }, status=status.HTTP_201_CREATED)

        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class AllPracticeUser(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        session = Sessionhelper.create_session()

        # Query all practice users with the role 'practice user'
        practice_users = session.query(PracticeUser).filter(PracticeUser.roles == 'practice user').all()

        # Extract the user IDs from practice users and query the User table
        user_ids = [practice_user.user_id for practice_user in practice_users]
        print(user_ids)
        
        stmt = select(auth_user.c.first_name, auth_user.c.id).where(auth_user.c.id.in_(user_ids))
        result = session.execute(stmt).fetchall()

        # Prepare response data
        response_data = [{"name": row.first_name, "id": row.id} for row in result]

        return Response(response_data, status=status.HTTP_200_OK)