from sqlalchemy import String, Integer, DateTime, create_engine, ForeignKey, Column, func, Table, MetaData, Boolean
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)
DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"
engine = create_engine(DATABASE_URL)


auth_user = Table(
    'auth_user', metadata, autoload_with = engine
)


# UserCampaign
# This will be a normal user with no extra features just a type{admin, user, superuser}

class UserCampaign(Base):
    __tablename__ = 'user_campaign'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    text = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)#Whether the campaign is finished , pending or any other 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=False)# id of the super user who has created this campaign


#UserCampaignSequence :- In this model, we will make a relationship with userCampaign as one campaign can have sub-campaigns.So this model represents the sub-campaign


class UserCampaignSequence(Base):
    __tablename__ = 'user_campaign_sequence'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_campaign_id = Column(Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserMessages(Base):
    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_campaign_id = Column(Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('auth_user.id', ondelete='CASCADE'), nullable=False)
    is_selected = Column(Boolean, default=True)

class SendCampaign(Base):
    __tablename__ = 'send_campaigns'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_campaign_id = Column(Integer, ForeignKey('user_campaign.id', ondelete='CASCADE'), nullable=False)
    