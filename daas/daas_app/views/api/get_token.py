from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='post',
    operation_id='login',
    security=[],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['username', 'password']
    ),
    responses={
        status.HTTP_202_ACCEPTED: openapi.Response(
            description='Request accepted. Files will be reprocessed soon.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description='Missing username or password.',
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description='Invalid credentials.'
        )
    }
)
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def get_token_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username is None or password is None:
        return Response({'message': 'Please provide both username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'message': 'Invalid Credentials'},
                        status=status.HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)
