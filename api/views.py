from knox.models import AuthToken
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser
from api.models import Organisation
from api.utils import get_location_and_temperature

from api.serializers import LoginSerializer, OrganisationSerializer, RegisterSerializer, UserSerializer


class GreetingView(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get(self, request):
        visitor_name = request.query_params.get("visitor_name", "Visitor")
        client_ip = self.get_client_ip(request)
        location, temperature = get_location_and_temperature(client_ip)
        greeting = None
        if location and temperature:
            greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"

        data = {"client_ip": client_ip, "location": location, "greeting": greeting}
        return Response(data, status=status.HTTP_200_OK)


# Task 2
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        Organisation.objects.create(
            name=f"{user.first_name}'s Organisation",
            description=f"{user.first_name}'s default organisation"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            refresh = RefreshToken.for_user(serializer.instance)
            data = {
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': serializer.data
                }
            }
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError:
            return Response(
                {
                    'status': 'Bad request',
                    'message': 'Registration unsuccessful',
                    'statusCode': 400,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")
        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            _, token = AuthToken.objects.create(user)
            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": token,
                        "user": UserSerializer(
                            user, context=self.get_serializer_context()
                        ).data,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request._auth.delete()
        return Response(
            {"status": "success", "message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )


class OrganisationView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=kwargs['uuid'])
        except CustomUser.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)

        UserSerializer(user)
        response_data = {
            'status': 'success',
            'message': 'User details retrieved successfully',
            'data': {
                'userId': user.user_id,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email,
                'phone': user.phone
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)



class OrganisationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming you have a way to get the user's organisations
        organisations = Organisation.objects.filter(users=request.user)
        serializer = OrganisationSerializer(organisations, many=True)

        response_data = {
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)


class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        try:
            # Fetch the organisation details based on orgId
            organisation = Organisation.objects.get(org_id=org_id, users=request.user)
            serializer = OrganisationSerializer(organisation)

            response_data = {
                "status": "success",
                "message": "Organisation details retrieved successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Organisation.DoesNotExist:
            return Response({
                "status": "fail",
                "message": "Organisation not found",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)


class OrganisationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                    "orgId": str(organisation.pk),
                    "name": organisation.name,
                    "description": organisation.description
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id, *args, **kwargs):
        user_id = request.data.get("userId")
        user = CustomUser.objects.get(user_id=user_id)
        organisation = Organisation.objects.get(org_id=org_id)
        organisation.users.add(user)
        return Response(
            {
                "status": "success",
                "message": "CustomUser added to organisation successfully",
            },
            status=status.HTTP_200_OK,
        )
