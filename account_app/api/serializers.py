from rest_framework import serializers
from django.contrib.auth.models import User
from main_app.models import RoleUser, Booker, Scheduler


class RoleSelectionSerializer(serializers.Serializer):
    """
    Serializer to handle user role selection during registration.
    Choices include 'booker' and 'scheduler'.
    """
    role = serializers.ChoiceField(choices=[('booker', 'Booker'), ('scheduler', 'Scheduler')])


class RegisterBookerWithPhoneSerializer(serializers.Serializer):
    """
    Serializer for registering a new booker using phone number and personal details.
    """
    phone = serializers.CharField(max_length=11)
    name = serializers.CharField(max_length=64)
    family = serializers.CharField(max_length=64)

    def validate_phone(self, value):
        """
        Ensure the phone number is exactly 11 digits and not already registered.
        """
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Phone number must be exactly 11 digits.")
        if Booker.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        """
        Create a new User, assign 'booker' role, and create a Booker profile.
        """
        user = User.objects.create(username=validated_data['phone'])
        role_user = RoleUser.objects.create(user=user, role='booker')
        return Booker.objects.create(owner=role_user, **validated_data)


class RegisterSchedulerWithPhoneSerializer(serializers.Serializer):
    """
    Serializer for registering a new scheduler using phone number and personal details.
    """
    phone = serializers.CharField(max_length=11)
    name = serializers.CharField(max_length=64)
    family = serializers.CharField(max_length=64)
    bio = serializers.CharField()

    def validate_phone(self, value):
        """
        Ensure the phone number is exactly 11 digits and not already registered.
        """
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Phone number must be exactly 11 digits.")
        if Scheduler.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        """
        Create a new User, assign 'scheduler' role, and create a Scheduler profile.
        """
        user = User.objects.create(username=validated_data['phone'])
        role_user = RoleUser.objects.create(user=user, role='scheduler')
        return Scheduler.objects.create(owner=role_user, **validated_data)


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP codes for registration or login.
    """
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)


class PhoneLoginSerializer(serializers.Serializer):
    """
    Serializer for initiating login using a phone number.
    Sends an OTP if the phone number is valid.
    """
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        """
        Ensure the phone number format is correct (11 digits only).
        """
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Invalid phone number format.")
        return value
