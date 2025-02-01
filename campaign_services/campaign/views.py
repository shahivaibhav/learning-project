from django.shortcuts import render
from .serializers import UserCampaignSerializer, EmailSerializer, UserCampaignScheduleSerializer
from rest_framework import viewsets
from .models import UserCampaign, UserMessages, SendCampaign, UserCampaignSequence
from practice_users.models import PracticeUser
from practice_users.services import Sessionhelper
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from django.core.mail import send_mail
from celery import Celery
from .tasks import send_campaign_at_scheduled_time
from django.utils import timezone
from pytz import timezone as pytz_timezone  # Only use pytz for actual timezone conversion
from datetime import timedelta


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
            if role == "admin":
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
    

def If_User_Practice_User(user_id_):

    session = Sessionhelper.create_session()
    
    try:
        user = session.query(PracticeUser).filter_by(user_id = user_id_).first()

        if user is not None:
            role = user.roles
            if role == "practice user":
                return True
            else:
                return False
            
        else:
            return False

    except Exception as e:
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


class IsPracticeUser(BasePermission):

    def has_permission(self, request, view):
        
        if If_User_Practice_User(request.user.id):
            return True
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
        finally:
            session.close()
        
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            campaign = session.query(UserCampaign).filter(UserCampaign.id == pk).first()

            if not campaign:
                return Response({"error message" : "There is no campaign"}, status=status.HTTP_404_NOT_FOUND)
            
            queryset = UserCampaignSerializer(campaign)
            return Response(queryset.data)
        
        except Exception as e:
            return Response({"error message" : str(e)}, status=status.HTTP_404_NOT_FOUND)
        finally :
            session.close()

    def update(self, request, pk = None, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            campaign = session.query(UserCampaign).filter(UserCampaign.id == pk).first()
            if not campaign:
                return Response({"error message" : "There is no campaign"}, status=status.HTTP_404_NOT_FOUND)
            
            request.data["created_by"] = request.user.id
            serializer = UserCampaignSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"error message" : serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)
            
            campaign.type = request.data.get('type', campaign.type)
            campaign.text = request.data.get('text', campaign.text)
            campaign.description = request.data.get('description', campaign.description)
            campaign.status = request.data.get('status', campaign.status)
            campaign.created_by = request.user.id or campaign.created_by

            session.commit()

            response_serializer = UserCampaignSerializer(campaign)
            return Response( response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)
        finally:
            session.close()
    
    def delete(self, request, pk=None, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            campaign = session.query(UserCampaign).filter(UserCampaign.id == pk).first()

            if not campaign:
                return Response({"error message": "There is no campaign to delete"}, status=status.HTTP_404_NOT_FOUND)

            session.delete(campaign)
            session.commit()

            return Response({"message": "Campaign deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()

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
        finally:
            session.close()
        
class UserMessagesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) :

        user_id = request.user.id
        session = Sessionhelper.create_session()

        if not user_id :
            return Response({"message" : "User_id not found!"}, status=status.HTTP_404_NOT_FOUND)
        
        try :
            messages = (
                session.query(UserMessages).filter(user_id=user_id).distinct().all()
            )

            if len(messages) == 0:
                return Response({"warning" : "No messages found for this user"}, status=status.HTTP_204_NO_CONTENT)
            
            camapign_ids = [message.user_campaign_id for message in messages]

            if len(camapign_ids) == 0:
                return Response({"error" : "No campaign ids found for this user"}, status=status.HTTP_404_NOT_FOUND)
            
            campaigns = (
                session.query(UserCampaign).filter_by(UserCampaign.id.in_(camapign_ids)).all()
            )

            if len(campaigns) == 0:
                return Response({"error" : "No campaigns found for this user"}, status=status.HTTP_404_NOT_FOUND)
            
            queryset = UserCampaignSerializer(campaigns, many=True)
            
            return Response({"message" : "Successfull getting messages!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error" : "Error in finding user messages"},status=status.HTTP_404_NOT_FOUND)
        
        finally:
            session.close()

class SendEmailViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Extract campaign_id from the URL
        campaign_id = kwargs.get('campaign_id')
        if not campaign_id:
            return Response({"error": "Campaign ID not found in URL!"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate request data using serializer
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            # Check whether to send via email or as messages
            send_via_email = serializer.validated_data['on_email']
            session = Sessionhelper.create_session()

            print("i am here")

            try:
                # Fetch campaign using campaign_id
                campaign = session.query(UserCampaign).filter(
                    UserCampaign.id == campaign_id,
                    UserCampaign.status == 'pending'
                ).first()

                if not campaign:
                    return Response({"error": "No campaign found!"}, status=status.HTTP_404_NOT_FOUND)

                if send_via_email:
                    # Email sending logic
                    subject = campaign.text
                    message = campaign.description
                    practice_users = session.query(PracticeUser).filter(PracticeUser.roles == 'practice user').all()
                    practice_user_ids = [user.user_id for user in practice_users]
                    practice_user_emails = User.objects.filter(id__in=practice_user_ids).values_list('email', flat=True)

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email="vaibhav.shahi@practicenumbers.com",
                        recipient_list=practice_user_emails
                    )

                    sent_mail_entry = SendCampaign(user_campaign_id=campaign_id)
                    session.add(sent_mail_entry)
                    session.commit()

                    return Response({"success": "Email sent successfully!"}, status=status.HTTP_201_CREATED)

                else:
                    # Message sending logic
                    practice_users = session.query(PracticeUser).filter(PracticeUser.roles == 'practice user').all()
                    practice_user_ids = [user.user_id for user in practice_users]

                    print(len(practice_user_ids), "user ids")

                    for user_id in practice_user_ids:
                        # Avoid duplicate messages
                        existing_message = session.query(UserMessages).filter_by(
                            user_id=user_id,
                            user_campaign_id=campaign.id
                        ).first()

                        if not existing_message:
                            new_message = UserMessages(user_id=user_id, user_campaign_id=campaign.id)
                            session.add(new_message)
                            session.commit()

                    return Response({"message": "Message sent successfully!"}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            finally:
                session.close()
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AllSentCampaigns(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Create a session to query the database
        session = Sessionhelper.create_session()

        try:
            
            sent_campaigns_email = session.query(SendCampaign).all()
            sent_campaigns_messages = session.query(UserMessages).all()

            # Collect the text and description for each sent campaign via email
            response_data = []
            for sent_campaign in sent_campaigns_email:
                campaign = session.query(UserCampaign).filter(UserCampaign.id == sent_campaign.user_campaign_id).first()
                if campaign:
                    response_data.append({
                        "status": campaign.status,
                        "campaign_id": campaign.id,
                        "text": campaign.text,
                        "description": campaign.description,
                        "sent_via": "email"
                    })

            # Collect the text and description for each sent campaign via messages
            for sent_message in sent_campaigns_messages:
                campaign = session.query(UserCampaign).filter(UserCampaign.id == sent_message.user_campaign_id).first()
                if campaign:
                    response_data.append({
                        "status": campaign.status,
                        "campaign_id": campaign.id,
                        "text": campaign.text,
                        "description": campaign.description,
                        "sent_via": "message"
                    })

            # Return the list of campaigns with text and description
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        finally:
            session.close()

class AcceptOrRejectCampaignViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsPracticeUser]

    def create(self, request, *args, **kwargs):
        # Placeholder for your create method
        pass

    def update(self, request, *args, **kwargs):
        # Get campaign_id from request data
        campaign_id = kwargs.get('pk')

        if not campaign_id:
            return Response({"error": "Campaign ID not found!"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a session to query the database
            session = Sessionhelper.create_session()

            # Fetch the campaign object using the passed campaign_id
            campaign = session.query(UserCampaign).filter_by(id=campaign_id).first()  # Fix: Add parentheses after first()

            if not campaign:
                return Response({"error": "Campaign ID not found!"}, status=status.HTTP_404_NOT_FOUND)

            # Check the current status of the campaign
            campaign_status = campaign.status

            # If the campaign is already active
            if campaign_status == "active":
                return Response({"message": "Campaign already active!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            # If the campaign is pending, update the status to active
            if campaign_status == "pending":
                campaign.status = "active"  # Fix: Directly update the campaign status
                session.commit()  # Commit the changes to the database
                return Response({"message": "Campaign status updated to active!"}, status=status.HTTP_200_OK)
            
            else:
                return Response({"error": "Unexpected campaign status!"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # If any exception occurs, return error message
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        finally:
            # Close the session after the operation
            session.close()


class ScheduleCampaignsViewSet(viewsets.ViewSet):
    
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):

        campaign_id = kwargs.get('campaign_id')
        serializer = UserCampaignScheduleSerializer(data=request.data)

        if not campaign_id:
            return Response({"error message" : "Campaign id not found"}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            scheduled_datetime = serializer.validated_data.get('scheduled_datetime')
            
        
            try:
                session = Sessionhelper.create_session()
                campaign = session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()

                if campaign:
                    # Convert to Indian Standard Time (IST)
                    ist = pytz_timezone('Asia/Kolkata')
                    if timezone.is_naive(scheduled_datetime):
                        scheduled_datetime = timezone.make_aware(scheduled_datetime)  # Make it aware in the system's timezone (UTC)
                    
                    scheduled_datetime = scheduled_datetime.astimezone(ist)  # Convert it to IST

                    # Create the schedule entry (if needed)
                    schedule_entry = UserCampaignSequence(
                        user_campaign_id=campaign_id,
                        scheduled_date=scheduled_datetime
                    )

                    session.add(schedule_entry)
                    session.commit()

                    # Schedule the task with specific IST time
                    send_campaign_at_scheduled_time.apply_async(
                        args=[campaign_id],
                        eta=scheduled_datetime
                    )

                    return Response(
                        {"success": f"Campaign scheduled for {scheduled_datetime}!"}, 
                        status=status.HTTP_201_CREATED
                    )
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
            finally:
                session.close()
        else :
            return Response({"error" : "Serializer not valid!"}, status=status.HTTP_400_BAD_REQUEST)
