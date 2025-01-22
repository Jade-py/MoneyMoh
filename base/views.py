from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BaseModel
from .serializers import BaseSerializer as bs
from django.utils import timezone
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world!")

@api_view(['GET'])
def get_data(request, year, month, day, user):
    try:
        # Create date range in UTC
        start_date = timezone.datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)
        end_date = timezone.datetime(year, month, day, 23, 59, 59, 999999, tzinfo=timezone.utc)

        data = BaseModel.objects.filter(
            date__range=(start_date, end_date),
            user=user
        ).values("event", "price", "date")

        serializer = bs(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def post_data(request):
    serializer = bs(data=request.data)
    if serializer.is_valid():
        try:
            # Ensure timezone awareness for the date field
            if 'date' in request.data and not timezone.is_aware(request.data['date']):
                request.data['date'] = timezone.make_aware(request.data['date'])
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_today(request):
    try:
        # Use timezone.now() instead of date.today()
        today = timezone.now().date()
        data = BaseModel.objects.filter(
            date__year=today.year,
            date__month=today.month,
            date__day=today.day
        ).values("event", "price", "date")
        serializer = bs(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})