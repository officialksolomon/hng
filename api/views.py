from knox.models import AuthToken
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response(
            {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": token,
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                },
            },
            status=status.HTTP_201_CREATED,
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


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CustomUser.objects.filter(id=user.id)


class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()


class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()


class OrganisationCreateView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        organisation = serializer.save()
        organisation.users.add(self.request.user)


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
