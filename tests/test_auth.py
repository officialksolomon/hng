from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from api.models import  Organisation

class TokenTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="password123",
            phone="1234567890"
        )

    def test_token_generation(self):
        token = AccessToken.for_user(self.user)
        self.assertEqual(token["user_id"], self.user.pk)
        self.assertGreater(token["exp"], int(timezone.now().timestamp()))

class OrganisationAccessTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = CustomUser.objects.create_user(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            password="password123",
            phone="1234567890"
        )
        self.user2 = CustomUser.objects.create_user(
            first_name="Bob",
            last_name="Jones",
            email="bob@example.com",
            password="password123",
            phone="0987654321"
        )
        
        self.org1 = Organisation.objects.create(
            name="Alice's Organisation",
            description="",
        )
        self.org1.users.add(self.user1)

        self.org2 = Organisation.objects.create(
            name="Bob's Organisation",
            description="",
        )
        self.org2.users.add(self.user2)

    def test_organisation_access(self):
        token = RefreshToken.for_user(self.user1).access_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
        
        response = self.client.get(reverse('organisation-detail', args=[self.org2.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden

class RegisterEndpointTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth-register')

    def test_register_user_successfully(self):
        response = self.client.post(self.register_url, {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Registration successful")
        self.assertIn("accessToken", response.data["data"])
        self.assertIn("user", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["firstName"], "John")
        self.assertEqual(response.data["data"]["user"]["lastName"], "Doe")
        self.assertEqual(response.data["data"]["user"]["email"], "john.doe@example.com")
        self.assertEqual(response.data["data"]["user"]["phone"], "1234567890")
        self.assertTrue(Organisation.objects.filter(name="John's Organisation").exists())

    def test_register_user_validation_error(self):
        response = self.client.post(self.register_url, {
            "firstName": "",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }, format='json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["errors"][0]["field"], "firstName")
        self.assertEqual(response.data["errors"][0]["message"], "This field may not be blank.")

    def test_register_user_duplicate_email(self):
        CustomUser.objects.create_user(
            user_id="existinguser",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="password123",
            phone="0987654321"
        )
        
        response = self.client.post(self.register_url, {
            "firstName": "John",
            "lastName": "Doe",
            "email": "jane.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }, format='json')

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["errors"][0]["field"], "email")
        self.assertEqual(response.data["errors"][0]["message"], "user with this email address already exists.")
