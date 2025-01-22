from sqlalchemy import String, Integer, DateTime, create_engine, ForeignKey, Column, func, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()
metadata = MetaData()
DATABASE_URL = "postgresql://practice_user:Vaibhav1@localhost/campaigdb"

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


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
