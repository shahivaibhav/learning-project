from django.shortcuts import render
from .serializers import UserCampaignSerializer, EmailSerializer, UserCampaignScheduleSerializer
from rest_framework import viewsets
from .models import UserCampaign, UserMessages, SendCampaign, UserCampaignSequence
from practice_users.models import engine
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
from rest_framework.pagination import PageNumberPagination
from sqlalchemy import asc, desc
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

logger = logging.getLogger(__name__)

metadata = MetaData()
Base = declarative_base(metadata=metadata)
DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"
engine = create_engine(DATABASE_URL)

auth_user = Table(
    'auth_user', metadata, autoload_with = engine
)

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


def If_User_SuperAdmin_Or_Admin(user_id_):
    session = Sessionhelper.create_session()

    try:
        if If_User_SuperAdmin(user_id_) or If_User_Admin(user_id_):
            return True
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

class IsSuperAdminOrAdmin(BasePermission):

    def has_permission(self, request, view):
        
        if If_User_SuperAdmin_Or_Admin(request.user.id):
            return True
        return False

class UserCampaignSuperAdminViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    

    class CustomPagination(PageNumberPagination):
        page_size = 6
        page_size_query_param = 'page_size'
        max_page_size = 100


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
            search_query = request.GET.get('search', '')  # Get search term from request
            order = request.GET.get('order', 'desc').lower()
            sort_by = request.GET.get('sort_by', 'created_at')

            campaigns = session.query(UserCampaign).filter(UserCampaign.is_deleted == False)

            if search_query:
                campaigns = campaigns.filter(UserCampaign.type.ilike(f"%{search_query}%"))

            if hasattr(UserCampaign, sort_by):
                order_func = desc if order == 'desc' else asc
                campaigns = campaigns.order_by(order_func(getattr(UserCampaign, sort_by)))

            paginator = self.CustomPagination()
            result_page = paginator.paginate_queryset(campaigns.all(), request, view=self)
            serializer = UserCampaignSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

            campaign.is_deleted = True
            session.commit()

            return Response({"message": "Campaign deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()

class UserCampaignAdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    class CustomPagination(PageNumberPagination):
        page_size = 5  # Default page size
        page_size_query_param = 'page_size'
        max_page_size = 100

    def list(self, request, *args, **kwargs):
        try:
            session = Sessionhelper.create_session()
            search_query = request.GET.get('search', '')  # Get search term from request
            sort_by = request.GET.get('sort_by', 'created_at')
            order = request.GET.get('order', 'desc')

            campaigns = session.query(UserCampaign).filter(UserCampaign.is_deleted == False)
            if search_query:
                campaigns = campaigns.filter(UserCampaign.type.ilike(f"%{search_query}%")) 

            if hasattr(UserCampaign, sort_by):
                order_func = desc if order == 'desc' else asc
                campaigns = campaigns.order_by(order_func(getattr(UserCampaign, sort_by)))

            # Apply pagination
            paginator = self.CustomPagination()
            result_page = paginator.paginate_queryset(campaigns.all(), request, view=self)
            serializer = UserCampaignSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        campaign_ids = request.data.get("campaign_ids", [])
        practice_user_ids = request.data.get('practice_users_ids', [])

        if not campaign_ids or not isinstance(campaign_ids, list):
            return Response({"error": "Invalid or missing campaign IDs!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not practice_user_ids or not isinstance(practice_user_ids, list):
            return Response({"error": "Invalid or missing campaign IDs!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        send_via_email = serializer.validated_data["on_email"]
        session = Sessionhelper.create_session()

        # Get the logged-in user's ID
        sender_id = request.user.id
        sent_at = datetime.now()

        print(request.user)
        print(vars(request.user))

        print(sender_id)

        try:
            # Fetch all campaigns
            campaigns = session.query(UserCampaign).filter(
                UserCampaign.id.in_(campaign_ids),
                UserCampaign.status == "pending"
            ).all()

            if not campaigns:
                return Response({"error": "No valid campaigns found!"}, status=status.HTTP_404_NOT_FOUND)

            if send_via_email:
                practice_user_emails = User.objects.filter(id__in=practice_user_ids).values_list("email", flat=True)                

                for campaign in campaigns:
                    already_sent = session.query(SendCampaign).filter_by(user_campaign_id=campaign.id).first()

                    if already_sent:
                        return Response({"message" : "Campaign already sent to users"}, status=status.HTTP_400_BAD_REQUEST)

                    send_mail(
                        subject=campaign.text,
                        message=campaign.description,
                        from_email="vaibhav.shahi@practicenumbers.com",
                        recipient_list=practice_user_emails
                    )

                    # Save the campaign with `sent_by`
                    session.add(SendCampaign(user_campaign_id=campaign.id, sent_by=sender_id, sent_at = sent_at))

                session.commit()
                return Response({"success": "Emails sent successfully!"}, status=status.HTTP_201_CREATED)

            else:
                # Check if any messages have already been sent
                if session.query(UserMessages).filter(
                    UserMessages.user_campaign_id.in_(campaign_ids),
                    UserMessages.user_id.in_(practice_user_ids)
                ).first():
                    return Response({"error": "One or more messages have already been sent for the selected campaigns!"}, status=status.HTTP_400_BAD_REQUEST)

                # Send messages
                for campaign in campaigns:
                    for user_id in practice_user_ids:
                        session.add(UserMessages(user_id=user_id, user_campaign_id=campaign.id, sent_by = sender_id, sent_at = sent_at))    

                session.commit()
                return Response({"message": "Messages sent successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            session.rollback()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        finally:
            session.close()

class AllSentCampaigns(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    class CustomPagination(PageNumberPagination):
        page_size = 12
        page_size_query_param = 'page_size'
        max_page_size = 100

    def list(self, request, *args, **kwargs):
        session = Sessionhelper.create_session()

        try:
            sent_campaigns_email = session.query(SendCampaign).order_by(SendCampaign.sent_at.desc()).all()
            sent_campaigns_messages = session.query(UserMessages).order_by(UserMessages.sent_at.desc()).all()

            # Use separate sets to track unique IDs for email and messages
            unique_email_campaign_ids = set()
            unique_message_campaign_ids = set()
            response_data = []
            # Process email campaigns
            for sent_campaign in sent_campaigns_email:
                # print(sent_campaign)
                # print(vars(sent_campaign))
                campaign = session.query(UserCampaign).filter(UserCampaign.id == sent_campaign.user_campaign_id).first()
                sender = session.query(auth_user).filter_by(id=sent_campaign.sent_by).first()


                sender_info = sender.username
                sent_at = sent_campaign.sent_at
                seen = sent_campaign.seen

                sent_date = sent_at.strftime('%Y-%m-%d') if sent_at else None
                sent_time = sent_at.strftime('%H:%M:%S') if sent_at else None

                if campaign and campaign.id not in unique_email_campaign_ids:
                    response_data.append({
                        "status": campaign.status,
                        "campaign_id": campaign.id,
                        "text": campaign.text,
                        "description": campaign.description,
                        "sent_via": "email",
                        "sender" : sender_info,
                        "sent_date": sent_date,
                        "sent_time": sent_time,
                        "seen" : seen
                    })
                    unique_email_campaign_ids.add(campaign.id)

            # Process message campaigns
            for sent_message in sent_campaigns_messages:
                campaign = session.query(UserCampaign).filter(UserCampaign.id == sent_message.user_campaign_id).first()

                sender = session.query(auth_user).filter_by(id=sent_message.sent_by).first()

                sender_info = sender.username
                sent_at = sent_message.sent_at
                seen = sent_message.seen

                sent_date = sent_at.strftime('%Y-%m-%d') if sent_at else None
                sent_time = sent_at.strftime('%H:%M:%S') if sent_at else None

                if campaign and campaign.id not in unique_message_campaign_ids:
                    response_data.append({
                        "status": campaign.status,
                        "campaign_id": campaign.id,
                        "text": campaign.text,
                        "description": campaign.description,
                        "sent_via": "message",
                        "sender" : sender_info,
                        "sent_date": sent_date,
                        "sent_time": sent_time,
                        "seen" : seen
                    })
                    unique_message_campaign_ids.add(campaign.id)

            response_data.sort(key=lambda x: x["sent_date"] + x["sent_time"], reverse=True)


            paginator = self.CustomPagination()
            result_page = paginator.paginate_queryset(response_data, request, view=self)

            if result_page is not None:
                # Calculate the "previous" page URL
                if paginator.page.number == 1:
                    # No "previous" for the first page
                    paginator.previous_page = None
                else:
                    # Compute the correct previous page URL
                    paginator.previous_page = f'{request.scheme}://{request.get_host()}{request.path}?page={paginator.page.number - 1}'

                return paginator.get_paginated_response(result_page)
            else:
                # Return the list of campaigns if no pagination
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
    permission_classes = [IsAuthenticated, IsSuperAdminOrAdmin]

    def create(self, request, *args, **kwargs):

        campaign_id = kwargs.get('campaign_id')
        sender_id = request.user.id  # The ID of the logged-in user (sender)
        sent_at = datetime.now()
        serializer = UserCampaignScheduleSerializer(data=request.data)

        print(campaign_id)
        print(sender_id)
        print(sent_at)
        # print(campaign_id)

        if not campaign_id:
            return Response({"error message": "Campaign id not found"}, status=status.HTTP_404_NOT_FOUND)

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
                        args=[campaign_id, sender_id, sent_at],  # Pass sender_id to the task
                        eta=scheduled_datetime
                    )

                    return Response(
                        {
                            "success": f"Campaign scheduled for {scheduled_datetime}!",
                            "campaign_id": campaign_id,
                            "scheduled_time": str(scheduled_datetime),
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
            finally:
                session.close()
        else:
            return Response({"error": "Serializer not valid!"}, status=status.HTTP_400_BAD_REQUEST)


class AllPracticeUsersViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdminOrAdmin]

    def list(self, request, *args, **kwargs):
        session = Sessionhelper.create_session()

        try:
            # Fetch only practice users' IDs
            practice_user_ids = session.query(PracticeUser.user_id).filter(
                PracticeUser.roles == 'practice user'
            ).all()

            # Extract just the IDs from the query results
            practice_user_ids_list = [user_id[0] for user_id in practice_user_ids]

            if not practice_user_ids_list:
                return Response({"error message": "No practice user found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"practice_users_ids": practice_user_ids_list}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response({"error message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        finally:
            session.close()

class SendAllCampaignsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdminOrAdmin]

    def create(self, request, *args, **kwargs):
        session = Sessionhelper.create_session()

        campaigns = session.query(UserCampaign).filter(UserCampaign.status == 'pending').all()
        practice_user_ids = request.data.get("practice_user_ids", [])
        sender_id = request.user.id
        sent_at = datetime.now()

        print(campaigns)

        if not campaigns:
            return Response({"error message" : "No campaigns were found!"}, status=status.HTTP_404_NOT_FOUND)
        
        if not practice_user_ids or not isinstance(practice_user_ids, list):
            return Response({"error": "Invalid or missing PRactice IDs!"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EmailSerializer(data = request.data)

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        send_via_email = serializer.validated_data['on_email']

        try:
            if send_via_email:
                practice_user_emails = User.objects.filter(id__in=practice_user_ids).values_list("email", flat=True)

                for campaign in campaigns:
                    send_mail(
                        subject=campaign.text,
                        message=campaign.description,
                        from_email="vaibhav.shahi@practicenumbers.com",
                        recipient_list=practice_user_emails
                    )

                    session.add(SendCampaign(user_campaign_id=campaign.id, sent_by=sender_id, sent_at = sent_at))
                session.commit()

                return Response({"success": "Emails sent successfully!"}, status=status.HTTP_201_CREATED)
            else:
                for campaign in campaigns:
                    for user_id in practice_user_ids:
                        existing_message = session.query(UserMessages).filter_by(
                            user_id=user_id,
                            user_campaign_id=campaign.id
                        ).first()

                        if not existing_message:
                            session.add(UserMessages(user_id=user_id, user_campaign_id=campaign.id, sent_by = sender_id, sent_at = sent_at))

                session.commit()
                return Response({"message": "Messages sent successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            session.rollback()
            print("i am here")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()

class MarkAsSeenViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        session = Sessionhelper.create_session()
        campaign_id = request.data.get("campaign_id")
        print(campaign_id)

        if not campaign_id:
            return Response({"error": "campaign_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update seen status for emails
            sent_campaign = session.query(SendCampaign).filter(
                SendCampaign.user_campaign_id == campaign_id
            ).first()

            if sent_campaign:
                sent_campaign.seen = True

            # Update seen status for messages
            sent_message = session.query(UserMessages).filter(
                UserMessages.user_campaign_id == campaign_id
            ).first()

            if sent_message:
                sent_message.seen = True

            session.commit()
            return Response({"success": "Message marked as seen"}, status=status.HTTP_200_OK)

        except Exception as e:
            session.rollback()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            session.close()