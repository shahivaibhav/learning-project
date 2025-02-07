from celery import Celery, shared_task
from datetime import datetime
from django.core.mail import send_mail
from practice_users.services import Sessionhelper
from .models import UserCampaign, SendCampaign
from practice_users.models import PracticeUser
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)



@shared_task
def send_campaign_at_scheduled_time(campaign_id, sent_at):
    session = Sessionhelper.create_session()
    try:
        campaign = session.query(UserCampaign).filter(UserCampaign.id == campaign_id).first()

        logger.info(f"Finding campaign in tasks")

        if campaign:
            logger.info(f"Campaign Found")
            
            subject = campaign.text
            message = campaign.description
            practice_users = session.query(PracticeUser).filter(PracticeUser.roles == 'practice user').all()
            practice_users_ids = [user.user_id for user in practice_users]
            practice_user_emails = User.objects.filter(id__in=practice_users_ids).values_list('email', flat=True)

            send_mail(
                subject=subject,
                message=message,
                from_email="vaibhav.shahi@practicenumbers.com",
                recipient_list=practice_user_emails
            )

            # Insert the record into the SendCampaign table with sender_id
            sent_mail_entry = SendCampaign(user_campaign_id=campaign_id, sent_by=sender_id, sent_at=sent_at)
            session.add(sent_mail_entry)
            session.commit()

            logger.info(f"Sent from scheduled tasks! {sent_mail_entry}")

            return {"success": "Email sent successfully!"}

        else:
            logger.info(f"No campaigns were found in tasks!")
            return {"error": "No campaign found"}

    except Exception as e:
        logger.error(f"Error while sending campaign: {str(e)}")
        return {"error": str(e)}

    finally:
        session.close()
