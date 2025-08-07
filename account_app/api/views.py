from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from main_app.models import RoleUser, Scheduler, Booker, OTP
from .serializers import (
    RoleSelectionSerializer,
    RegisterBookerWithPhoneSerializer,
    RegisterSchedulerWithPhoneSerializer,
    VerifyOTPSerializer,
    PhoneLoginSerializer,
)
from account_app.api.utils import generate_otp


class RoleSelectionView(APIView):
    """
    Allows users to select a role (booker or scheduler) during onboarding.
    """
    def post(self, request):
        serializer = RoleSelectionSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Role selected", "role": serializer.validated_data['role']})
        return Response(serializer.errors, status=400)


class RegisterBookerWithPhoneView(APIView):
    """
    Registers a new booker using their phone number and basic personal details.
    Generates and sends an OTP after successful registration.
    """
    def post(self, request):
        serializer = RegisterBookerWithPhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            serializer.save()
            code = generate_otp()
            OTP.objects.create(phone=phone, code=code)
            print(f"[OTP to booker {phone}]: {code}")  # Debug log for development
            return Response({"message": "OTP sent"})
        return Response(serializer.errors, status=400)


class RegisterSchedulerWithPhoneView(APIView):
    """
    Registers a new scheduler with phone number and bio.
    Sends OTP after saving the profile.
    """
    def post(self, request):
        serializer = RegisterSchedulerWithPhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            serializer.save()
            code = generate_otp()
            OTP.objects.create(phone=phone, code=code)
            print(f"[OTP to scheduler {phone}]: {code}")  # Debug log for development
            return Response({"message": "OTP sent"})
        return Response(serializer.errors, status=400)


class VerifyOTPView(APIView):
    """
    Verifies the OTP sent during registration.
    Returns JWT tokens if successful.
    """
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']

            otp = OTP.objects.filter(phone=phone, code=code).last()

            if not otp:
                return Response({'error': 'OTP not found'}, status=400)

            if otp.is_expired():
                return Response({'error': 'OTP has expired'}, status=400)

            # Retrieve the RoleUser instance by matching phone number to either role
            role_user = RoleUser.objects.filter(
                Q(booker_owner__phone=phone) | Q(scheduler_owner__phone=phone)
            ).first()

            if role_user:
                refresh = RefreshToken.for_user(role_user.user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })

            return Response({'error': 'User not found for this phone'}, status=404)

        return Response(serializer.errors, status=400)


class OTPLoginView(APIView):
    """
    Initiates login by sending an OTP to a registered phone number.
    """
    def post(self, request):
        serializer = PhoneLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']

            # Check if user with this phone exists
            try:
                RoleUser.objects.get(Q(booker_owner__phone=phone) | Q(scheduler_owner__phone=phone))
            except RoleUser.DoesNotExist:
                return Response({'error': 'User not registered'}, status=404)

            # Generate and send OTP
            code = generate_otp()
            OTP.objects.create(phone=phone, code=code)
            print(f"[OTP for login {phone}]: {code}")  # Debug log for development
            return Response({'message': 'OTP sent'})

        return Response(serializer.errors, status=400)


class OTPLoginVerifyView(APIView):
    """
    Verifies OTP for login.
    If valid, returns access and refresh tokens.
    """
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']

            # Check if OTP is correct
            if OTP.objects.filter(phone=phone, code=code).exists():
                role_user = RoleUser.objects.filter(
                    Q(booker_owner__phone=phone) | Q(scheduler_owner__phone=phone)
                ).first()

                if role_user:
                    refresh = RefreshToken.for_user(role_user.user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })

                return Response({'error': 'User not found'}, status=404)

            return Response({'error': 'Invalid OTP'}, status=400)

        return Response(serializer.errors, status=400)


class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    """
    Logs out the user by blacklisting the provided refresh token.
    Requires the user to be authenticated.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid or expired refresh token."}, status=400)
