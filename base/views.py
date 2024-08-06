from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import BaseModel
from .serializers import BaseSerializer as bs
from datetime import date
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world!")


@api_view(['GET'])
def get_data(request, year, month, day):
    try:
        data = BaseModel.objects.filter(date__year=year, date__month=month, date__day=day).values("event", "price", "date")
        serializer = bs(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response(f'{e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
