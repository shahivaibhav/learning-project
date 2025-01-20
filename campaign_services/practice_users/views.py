from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import PracticeUser
from .serializers import UserSerializer, NewPracticeSerializer
from .services import Sessionhelper

class PracticeUserViewSet(viewsets.ViewSet):

    
    def list(self, request, *arg, **kwargs):

        session = Sessionhelper.create_session()
        practice_user = session.query(PracticeUser).all()
        serializer = NewPracticeSerializer(practice_user, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):

        session = Sessionhelper.create_session()

        practice_user_data = request.data
        user_serializer = UserSerializer(data=practice_user_data)

        if user_serializer.is_valid():
            user = user_serializer.save()
            remaining_user_data = {
                'role' : practice_user_data['role'],
                # 'id' : practice_user_data.id,
                "user_id": user.id,
            }

            new_user = PracticeUser(**remaining_user_data)
            session.add(new_user)
            session.commit()
            session.close()

            return Response({
                "user_id" : user.id,
                "practice_user_id" : new_user.id,
                "message" : "User and Practice User are linked up!"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )




