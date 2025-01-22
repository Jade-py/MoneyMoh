from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BaseModel
from .serializers import BaseSerializer as bs
from datetime import date
from django.http import HttpResponse
import pytz


def index(request):
    return HttpResponse("Hello, world!")


from django.utils import timezone
from datetime import datetime
from django.db.models import Q


@api_view(['GET'])
def get_data(request, year, month, day, user):
    try:
        # Create date range in UTC
        start_date = timezone.datetime(year, month, day, 0, 0, 0, tzinfo=timezone.timezone.utc)
        end_date = timezone.datetime(year, month, day, 23, 59, 59, 999999, tzinfo=timezone.timezone.utc)

        # Query using date range instead of individual fields
        data = BaseModel.objects.filter(
            date__range=(start_date, end_date),
            user=user
        ).values("event", "price", "date")

        local_tz = pytz.timezone('Asia/Kolkata')
        data_list = list(data)
        for item in data_list:
            item['date'] = timezone.datetime.astimezone(item['date'], local_tz)

        serializer = bs(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def post_data(request):
    serializer = bs(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_today(request):
    try:
        data = BaseModel.objects.filter(date=date.today()).values("event", "price", "date")
        serializer = bs(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})
