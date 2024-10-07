# core/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['GET'])
def get_destinations(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    print("token:-", token)
    if not token:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=token)
        print(account)
    except Account.DoesNotExist:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    print("DATA", data)
    if not isinstance(data, dict):
        print("JHKHKKK")
        return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    for destination in account.destinations.all():
        headers = destination.headers
        method = destination.http_method
        url = destination.url
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
            print("Get")
            print("GET",response)
        elif method in ['POST', 'PUT']:
            response = requests.request(method, url, headers=headers, json=data)
            print("Post, Put")
            print(response)
        if response.status_code not in [200, 201]:
            return Response({"error": f"Failed to send data to {url}"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "Data sent successfully"})
