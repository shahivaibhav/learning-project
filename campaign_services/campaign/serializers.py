import logging
from rest_framework import serializers
from practice_users.services import Sessionhelper

logger = logging.getLogger(__name__)

class CustomUserSerializer(serializers.Serializer):

    def create(self, validated_data):
        
        session = Sessionhelper.create_session()

        model_class = self.Meta.model
        instance = model_class(**validated_data)

        session.add(instance)
        session.commit()
        session.close()

        print(instance)

        return instance

    def update(self, instance, validated_data):
        pass

    def to_representation(self, instance):
        representation =  {
            column.key: getattr(instance, column.key)
            for column in instance.__table__.columns
        }
        logger.debug(f"to_representation output :{representation}")
        return representation
        

class UserCampaignSerializer(CustomUserSerializer):
    type = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(default='pending', required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    created_by = serializers.IntegerField(required=True)

    def create(self, validated_data):

        validated_data['status'] = validated_data.get('status', 'pending')
        validated_data['created_at'] = validated_data.get('created_at', None)
        validated_data['updated_at'] = validated_data.get('updated_at', None)

        logger.debug(f"Validdation here, validated_data : {validated_data}")

        try:
            instance = super().create(validated_data)
            print(instance)
            return instance
        except Exception as e:
            logger.error(f"Error encounter during creation of usercampaign here , the error is : {e}")

class EmailSerializer(CustomUserSerializer):
    on_email = serializers.BooleanField(default=True)
    
class UserCampaignScheduleSerializer(CustomUserSerializer):
    user_campaign_id = serializers.IntegerField(required=True)
    scheduled_datetime = serializers.DateTimeField(required=True)

    


