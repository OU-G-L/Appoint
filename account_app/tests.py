from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from main_app.models import RoleUser, Booker, Scheduler, OTP
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


class AccountAPITestCase(TestCase):
    """
    Test suite for Account-related API endpoints including
    registration, login, and OTP verification for Booker and Scheduler users.
    """

    def setUp(self):
        """
        Setup runs before each test method.
        Initializes API client and sample phone numbers.
        """
        self.client = APIClient()
        self.booker_phone = '09123456789'
        self.scheduler_phone = '09987654321'

    def test_register_booker_with_phone(self):
        """
        Test Booker registration endpoint.
        Sends POST request with Booker info and expects
        HTTP 200 OK with message "OTP sent".
        """
        url = reverse('otp-register-booker')
        data = {
            "phone": self.booker_phone,
            "name": "John",
            "family": "Doe"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "OTP sent")

    def test_register_scheduler_with_phone(self):
        """
        Test Scheduler registration endpoint.
        Sends POST request with Scheduler info and expects
        HTTP 200 OK with message "OTP sent".
        """
        url = reverse('otp-register-scheduler')
        data = {
            "phone": self.scheduler_phone,
            "name": "Alice",
            "family": "Smith",
            "bio": "Scheduler bio"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "OTP sent")

    def test_otp_login(self):
        """
        Test OTP login endpoint.
        First, creates a Booker user in DB.
        Sends POST request to login with phone number and expects
        HTTP 200 OK with message "OTP sent".
        """
        # Create user and role
        user = User.objects.create(username=self.booker_phone)
        role_user = RoleUser.objects.create(user=user, role='booker')
        Booker.objects.create(owner=role_user, phone=self.booker_phone, name='John', family='Doe')

        url = reverse('otp-login')
        data = {"phone": self.booker_phone}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "OTP sent")

    def test_verify_otp_success(self):
        """
        Test OTP verification success scenario.
        Creates a user and a valid OTP entry.
        Sends POST request with correct phone and OTP code.
        Expects HTTP 200 OK and JWT tokens (access & refresh) in response.
        """
        # Create user and role
        user = User.objects.create(username=self.booker_phone)
        role_user = RoleUser.objects.create(user=user, role='booker')
        Booker.objects.create(owner=role_user, phone=self.booker_phone, name='John', family='Doe')

        # Create a valid OTP
        otp = OTP.objects.create(phone=self.booker_phone, code='123456')

        url = reverse('verify-otp')
        data = {"phone": self.booker_phone, "code": "123456"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_verify_otp_invalid(self):
        """
        Test OTP verification failure with invalid OTP code.
        Sends POST request with incorrect OTP code.
        Expects HTTP 400 Bad Request.
        """
        url = reverse('verify-otp')
        data = {"phone": self.booker_phone, "code": "000000"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_expired(self):
        """
        Test OTP verification failure due to expired OTP.
        Creates an OTP with a created_at time older than expiry threshold.
        Sends POST request with expired OTP code.
        Expects HTTP 400 Bad Request.
        """
        # Create OTP and manually set created_at to 4 minutes ago (expired)
        otp = OTP.objects.create(phone=self.booker_phone, code='654321')
        otp.created_at = timezone.now() - datetime.timedelta(minutes=4)
        otp.save()

        url = reverse('verify-otp')
        data = {"phone": self.booker_phone, "code": "654321"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
