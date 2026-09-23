from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def basic_auth_view(request):
    # TODO: Extract and print the header
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    print(f"Incoming Header: {auth_header}")
    return Response({"message": "Check your terminal!"})