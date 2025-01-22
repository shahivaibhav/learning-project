from django.shortcuts import render
from .serializers import UserCampaignSerializer
from rest_framework import viewsets
from .models import UserCampaign
from practice_users.models import PracticeUser
from practice_users.services import Sessionhelper
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def If_User_SuperAdmin(user_id_):
    session = Sessionhelper.create_session()

    logger.info(f"Checking if the user is superadmin or not, id : {user_id_}")

    try:
        # Querying using 'user_id' because that's the foreign key to the auth_user
        user = session.query(PracticeUser).filter_by(user_id=user_id_).first()  # Use user_id here instead of id
        print("practice user", PracticeUser)
        print("hii", print(session.query(PracticeUser)))
        print(user)

        if user is not None:
            role = user.roles
            print("role is :", role)
            if role == 'super_admin':
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False


def If_User_Admin(user_id_):

    session = Sessionhelper.create_session()

    logger.info(f"Checking if the user is superadmin or not, id : {user_id_}")

    try:
        
        user = session.query(PracticeUser).filter_by(user_id=user_id_).first()
        print(user)
        if user is not None:
            role = user.roles
            if(role == "admin"):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()    
    

class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        
        print("request", request.user.id)
        if If_User_SuperAdmin(request.user.id):
            # print("request", request)
            return True
        
        print("Error in isSuperAddmin Function.. ")
        return False

class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        
        if If_User_Admin(request.user.id):
            return True
        
        print("Error in isSuperAddmin Function.. ")
        return False

class UserCampaignSuperAdminViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def create(self, request, *args, **kwargs):
        created_by = request.user.id
        print(request.data, "User Campaign Viewset request.data")
        print(created_by, "created_by")

        request.data['created_by'] = created_by

        serializer = UserCampaignSerializer(data=request.data)

        if not serializer.is_valid():
            Response({"message": "Error in creating campaign"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            session = Sessionhelper.create_session()
            user_campaign_data = serializer.validated_data

            new_campaign = UserCampaign(
                type=user_campaign_data['type'],
                text=user_campaign_data['text'],
                description=user_campaign_data.get('description', ''),
                created_by=user_campaign_data['created_by'],
                status=user_campaign_data['status'],
            )
            
            session.add(new_campaign)
            session.commit()

            response = UserCampaignSerializer(new_campaign)

            return Response(response.data, status=status.HTTP_201_CREATED)
        
        except Exception as e :

            return Response({"error message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()

    def list(self, request, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            campaigns = session.query(UserCampaign).all()

            serializer = UserCampaignSerializer(campaigns, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_405_METHOD_NO)
        
        
class UserCampaignAdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            campaigns = session.query(UserCampaign).all()

            serializer = UserCampaignSerializer(campaigns, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)