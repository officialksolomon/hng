from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import CustomUser
from api.models import Organisation




class TokenTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="password123",
            phone="1234567890",
        )

    def test_token_generation(self):
        token = AccessToken.for_user(self.user)
        self.assertEqual(token["user_id"], str(self.user.pk))
        self.assertGreater(token["exp"], int(timezone.now().timestamp()))


class OrganisationAccessTest(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = CustomUser.objects.create_user(
            first_name="user1",
            last_name="user1",
            email="user1@example.com",
            password="password123",
            phone="0000000009",
        )
        self.user2 = CustomUser.objects.create_user(
            first_name="user2",
            last_name="user2",
            email="user2@example.com",
            password="password123",
            phone="0000000001",
        )

        # Create organisations
        self.org1 = Organisation.objects.create(name="Organisation 1")
        self.org2 = Organisation.objects.create(name="Organisation 2")

        # add users to organization
        self.org1.users.add(self.user1)
        self.org2.users.add(self.user2)

        # URLs
        self.detail_url_org1 = reverse("api:organisation-detail", args=[self.org1.pk])
        self.detail_url_org2 = reverse("api:organisation-detail", args=[self.org2.pk])

    # def test_organisation_access(self):
    #     # Scenario 1: User1 accessing their own organisation
    #     self.client = APIClient()
    #     self.client.force_authenticate(user=self.user1)
    #     response = self.client.get(self.detail_url_org1)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["name"], self.org1.name)

    #     # Scenario 2: User1 trying to access User2's organisation
    #     self.client.force_authenticate(user=self.user1)
    #     response = self.client.get(self.detail_url_org2)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RegisterEndpointTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("api:register")

    def test_register_user_successfully(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "passw@@ord123",
                "phone": "1234567890",
            },
            format="json",
        )
        # Print response data for debugging
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(response.data)  # Print the error details

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Registration successful")
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("user", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["firstName"], "John")
        self.assertEqual(response.data["data"]["user"]["lastName"], "Doe")
        self.assertEqual(response.data["data"]["user"]["email"], "john.doe@example.com")
        self.assertEqual(response.data["data"]["user"]["phone"], "1234567890")
        self.assertTrue(
            Organisation.objects.filter(name="John's Organisation").exists()
        )

    def test_register_user_validation_error(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "passw@@ord123",
                "phone": "1234567890",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_user_duplicate_email(self):
        CustomUser.objects.create_user(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="password123",
            phone="0987654321",
        )

        response = self.client.post(
            self.register_url,
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "password": "password123",
                "phone": "1234567890",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
