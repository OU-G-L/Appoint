from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class OTP(models.Model):
    """
    Stores one-time passwords (OTPs) for phone number verification.
    Each OTP is linked to a phone number and expires after 3 minutes.
    """
    phone = models.CharField(max_length=11)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """
        Checks whether the OTP has expired (valid for 3 minutes).
        """
        return timezone.now() > self.created_at + datetime.timedelta(minutes=3)

    def __str__(self):
        return f'{self.phone} - {self.code}'


class RoleUser(models.Model):
    """
    Connects a Django User to a specific role: 'booker' or 'scheduler'.
    """
    ROLE_CHOICES = (
        ('scheduler', 'Scheduler'),
        ('booker', 'Booker'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='role_profile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='booker'
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Scheduler(models.Model):
    """
    Profile for schedulers.
    Stores personal info and bio. Connected to a RoleUser instance.
    """
    owner = models.OneToOneField(
        RoleUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='scheduler_owner'
    )
    name = models.CharField(max_length=64, verbose_name='نام')
    family = models.CharField(max_length=64, verbose_name='نام خانوادگی')
    phone = models.CharField(max_length=11, unique=True, verbose_name='شماره تلفن')
    bio = models.TextField()
    is_public_search = models.BooleanField(
        default=True,
        verbose_name="نمایش در جستجو مشتری ناشناس"
    )

    def __str__(self):
        return f'{self.name}'


class Booker(models.Model):
    """
    Profile for bookers.
    Connected to RoleUser and linked to multiple Schedulers via M2M relationship.
    """
    owner = models.OneToOneField(
        RoleUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='booker_owner'
    )
    schedulers = models.ManyToManyField(
        Scheduler,
        related_name='bookers'
    )
    name = models.CharField(max_length=64, verbose_name='نام')
    family = models.CharField(max_length=64, verbose_name='نام خانوادگی')
    phone = models.CharField(max_length=11, unique=True, verbose_name='شماره تلفن')

    def __str__(self):
        scheduler_names = ", ".join([f"{h.name} {h.family}" for h in self.schedulers.all()])
        return f'{self.name} | آرایشگر(ها): {scheduler_names if scheduler_names else "-"}'


class Appointment(models.Model):
    """
    Represents a booking between a booker and a scheduler.
    Each appointment has a date, time, and optional note.
    """
    scheduler = models.ForeignKey(
        Scheduler,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    booker = models.ForeignKey(
        Booker,
        on_delete=models.CASCADE,
        related_name='appointments',
        null=True,
        blank=True
    )
    booker_name = models.CharField(
        max_length=100,
        blank=True
    )  # For anonymous or temporary bookings
    date = models.DateField()
    time = models.TimeField()
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent double booking (same time and scheduler)
        unique_together = ('scheduler', 'date', 'time')
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.date} - {self.time} | {self.scheduler} ← {self.booker}'
