from datetime import time, date, datetime
from rest_framework import serializers
from main_app.models import Booker, Scheduler, Appointment


class SchedulerBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for the Scheduler model.
    Provides common fields used across different scheduler-related serializers.
    """
    class Meta:
        model = Scheduler
        fields = ['name', 'family', 'phone', 'bio']


# region ----- Admin -----

class SchedulerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing schedulers with basic contact info.
    """
    class Meta:
        model = Scheduler
        fields = ['name', 'family', 'phone']


class SchedulerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed scheduler information including role and username.
    """
    role = serializers.CharField(source='owner.role', read_only=True)
    username = serializers.CharField(source='owner.user.username', read_only=True)

    class Meta:
        model = Scheduler
        fields = ['role', 'username', 'name', 'family', 'phone', 'bio']


class BookerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing bookers with their contact info and assigned scheduler.
    """
    class Meta:
        model = Booker
        fields = ['name', 'family', 'phone', 'scheduler']


class BookerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed booker info including role and associated scheduler details.
    """
    role = serializers.CharField(source='owner.role', read_only=True)
    scheduler_id = serializers.IntegerField(source='scheduler.id', read_only=True)
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)

    class Meta:
        model = Booker
        fields = ['role', 'name', 'family', 'phone', 'scheduler_id', 'scheduler_username']


class AppointmentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing appointments with booker and scheduler usernames.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)
    booker_username = serializers.CharField(source='booker.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['booker_username', 'scheduler_username', 'date', 'time']


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed appointment information including note.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)
    booker_username = serializers.CharField(source='booker.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['booker_username', 'scheduler_username', 'date', 'time', 'note']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create a new appointment.
    Validates the appointment time is within allowed hours (8:00 - 20:00)
    and checks that the selected time slot is not already booked.
    """
    booker = serializers.PrimaryKeyRelatedField(
        queryset=Booker.objects.all(), write_only=True
    )

    class Meta:
        model = Appointment
        fields = ['id', 'booker', 'date', 'time', 'scheduler', 'note']

    def validate_time(self, value):
        """
        Ensure the appointment time is between 8 AM and 8 PM.
        """
        if value < time(8, 0) or value >= time(20, 0):
            raise serializers.ValidationError("Appointments can only be booked between 08:00 and 20:00.")
        return value

    def validate(self, data):
        """
        Check if the appointment slot (scheduler, date, time) is already booked.
        """
        exists = Appointment.objects.filter(
            scheduler=data['scheduler'],
            date=data['date'],
            time=data['time']
        ).exists()
        if exists:
            raise serializers.ValidationError("This time slot has already been booked.")
        return data

# endregion


# region ----- Scheduler -----

class SchedulerPanelProfileSerializer(SchedulerBaseSerializer):
    """
    Serializer for Scheduler profile data in the panel view.
    Inherits fields from SchedulerBaseSerializer.
    """
    pass


class SchedulerPanelUpdateProfileSerializer(SchedulerBaseSerializer):
    """
    Serializer for updating Scheduler profile in the panel.
    Partial updates allowed.
    """
    pass


class SchedulerPanelBookersProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for listing bookers associated with a scheduler.
    Includes basic booker contact info.
    """
    class Meta:
        model = Booker
        fields = ['name', 'family', 'phone']


class SchedulerPanelAppointmentsProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for listing scheduler's appointments with
    booker and scheduler usernames included.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)
    booker_username = serializers.CharField(source='booker.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['booker_username', 'scheduler_username', 'date', 'time', 'note']


class SchedulerPanelAppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating appointments from scheduler panel.
    Supports linking to an existing booker or specifying a booker name.
    Validates overlapping appointments for the same scheduler.
    """
    booker = serializers.PrimaryKeyRelatedField(queryset=Booker.objects.all(), required=False, allow_null=True)
    booker_name = serializers.CharField(required=False, allow_blank=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'date', 'time', 'booker', 'booker_name', 'display_name', 'note']
        extra_kwargs = {
            'scheduler': {'read_only': True},  # Scheduler field is read-only; set via context
        }

    def get_display_name(self, obj):
        """
        Returns full name of the linked booker or the custom booker_name.
        """
        if obj.booker:
            return f"{obj.booker.name} {obj.booker.family}"
        return obj.booker_name or "Unnamed"

    def validate(self, data):
        """
        Ensure at least one of 'booker' or 'booker_name' is provided.
        Check if the appointment slot is already booked for this scheduler.
        """
        if not data.get('booker') and not data.get('booker_name'):
            raise serializers.ValidationError("At least one of 'booker' or 'booker_name' must be provided.")

        scheduler = self.context.get('scheduler')
        if scheduler and not self.instance:
            exists = Appointment.objects.filter(
                scheduler=scheduler,
                date=data['date'],
                time=data['time']
            ).exists()
            if exists:
                raise serializers.ValidationError("This time slot has already been booked.")
        return data


class SchedulerPanelAppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing appointment from scheduler panel.
    Similar to create serializer with validation to prevent time conflicts.
    """
    booker = serializers.PrimaryKeyRelatedField(queryset=Booker.objects.all(), required=False, allow_null=True)
    booker_name = serializers.CharField(required=False, allow_blank=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'date', 'time', 'booker', 'booker_name', 'display_name', 'note']
        extra_kwargs = {
            'scheduler': {'read_only': True},  # Scheduler field is read-only
        }

    def get_display_name(self, obj):
        """
        Returns full name of the linked booker or the custom booker_name.
        """
        if obj.booker:
            return f"{obj.booker.name} {obj.booker.family}"
        return obj.booker_name or "Unnamed"

    def validate(self, data):
        """
        Ensure at least one of 'booker' or 'booker_name' is provided.
        Check if the appointment slot is already booked for this scheduler when creating.
        """
        if not data.get('booker') and not data.get('booker_name'):
            raise serializers.ValidationError("At least one of 'booker' or 'booker_name' must be provided.")

        scheduler = self.context.get('scheduler')
        if scheduler and not self.instance:
            exists = Appointment.objects.filter(
                scheduler=scheduler,
                date=data['date'],
                time=data['time']
            ).exists()
            if exists:
                raise serializers.ValidationError("This time slot has already been booked.")
        return data


class SchedulerDashboardProfileSerializer(SchedulerBaseSerializer):
    """
    Serializer for scheduler profile info displayed in the dashboard.
    """
    pass


class SchedulerDashboardBookersProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for bookers list shown in the scheduler dashboard.
    """
    class Meta:
        model = Booker
        fields = ['name', 'family', 'phone']


class SchedulerDashboardAppointmentsProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for appointments list displayed on scheduler dashboard.
    Shows usernames for both booker and scheduler.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)
    booker_username = serializers.CharField(source='booker.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['booker_username', 'scheduler_username', 'date', 'time']

# endregion


# region ----- Booker -----

class BookerPanelProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Booker profile data in the panel.
    Includes linked scheduler's username.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)

    class Meta:
        model = Booker
        fields = ['name', 'family', 'phone', 'scheduler_username']


class BookerPanelUpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Booker profile data in the panel.
    Scheduler username is read-only.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)

    class Meta:
        model = Booker
        fields = ['name', 'family', 'phone', 'scheduler_username']


class BookerPanelAppointmentsProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for listing a booker's appointments on their panel.
    Includes scheduler's username.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['scheduler_username', 'date', 'time', 'note']
        extra_kwargs = {
            'scheduler': {'read_only': True},
        }


class BookerPanelUpdateAppointmentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing appointment from the booker panel.
    Validates date and time similarly to creation serializer.
    """
    scheduler_username = serializers.CharField(source='scheduler.owner.user.username', read_only=True)

    class Meta:
        model = Appointment
        fields = ['scheduler_username', 'date', 'time', 'note']
        extra_kwargs = {
            'scheduler': {'read_only': True},
        }

    def validate_date(self, value):
        """
        Validate that the new appointment date is not in the past.
        """
        if value < date.today():
            raise serializers.ValidationError("The selected date is in the past. Only future dates are allowed.")
        return value

    def validate_time(self, value):
        """
        Validate appointment time is between allowed hours.
        """
        if value < time(8, 0) or value >= time(20, 0):
            raise serializers.ValidationError("Appointment time must be between 8:00 and 20:00.")
        return value

    def validate(self, data):
        """
        Validate time conflicts when updating an appointment.
        Ensures time is in future if appointment is for today.
        Checks for conflicts excluding the current appointment.
        """
        selected_date = data.get('date', self.instance.date)
        selected_time = data.get('time', self.instance.time)
        scheduler = self.instance.scheduler  # read_only, so taken from instance

        # For today's date, time must be in the future
        if selected_date == date.today():
            now = datetime.now().time()
            if selected_time <= now:
                raise serializers.ValidationError(
                    "You cannot book an appointment in the past or at the current time."
                )

        # Check for conflicting appointments excluding current one
        conflict = Appointment.objects.filter(
            scheduler=scheduler,
            date=selected_date,
            time=selected_time
        ).exclude(id=self.instance.id).exists()

        if conflict:
            raise serializers.ValidationError("This time slot has already been booked.")

        return data


class AddSchedulerSerializer(serializers.Serializer):
    """
    Serializer to add a scheduler to a booker's list using a scheduler's phone number code.
    Only schedulers with public search enabled can be added.
    """
    scheduler_code = serializers.CharField(max_length=100)

    def validate_scheduler_code(self, value):
        """
        Validate the scheduler code corresponds to a publicly searchable scheduler.
        """
        try:
            scheduler = Scheduler.objects.get(phone=value, is_public_search=True)
        except Scheduler.DoesNotExist:
            raise serializers.ValidationError("Scheduler not found or not publicly visible.")
        return scheduler

    def save(self, **kwargs):
        """
        Add the validated scheduler to the booker's list.
        """
        booker = self.context['booker']
        scheduler = self.validated_data['scheduler_code']  # This is now a Scheduler instance
        booker.schedulers.add(scheduler)
        return scheduler


class BookerAppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for bookers to create appointments only with schedulers they have added.
    Validates that the selected scheduler is in the booker's list.
    Also validates date and time constraints.
    """
    scheduler = serializers.PrimaryKeyRelatedField(queryset=Scheduler.objects.none())

    class Meta:
        model = Appointment
        fields = ['date', 'time', 'scheduler', 'note']

    def __init__(self, *args, **kwargs):
        """
        Limit scheduler queryset to those added by the booker.
        """
        super().__init__(*args, **kwargs)
        booker = self.context.get('booker')
        if booker:
            self.fields['scheduler'].queryset = booker.schedulers.all()

    def validate(self, data):
        """
        Validate that the scheduler is in booker's list,
        the date and time are valid and not in the past,
        and that the time slot is not already booked.
        """
        scheduler = data['scheduler']
        booker = self.context['booker']
        selected_date = data['date']
        selected_time = data['time']

        if scheduler not in booker.schedulers.all():
            raise serializers.ValidationError(
                "You can only book appointments with schedulers you have added."
            )

        # If appointment is for today, time must be in the future
        if selected_date == date.today():
            now = datetime.now().time()
            if selected_time <= now:
                raise serializers.ValidationError(
                    "You cannot book an appointment in the past or at the current time."
                )

        # Date must not be in the past
        if selected_date < date.today():
            raise serializers.ValidationError(
                "You cannot book an appointment on a past date."
            )

        # Check if time slot is already booked for this scheduler
        if Appointment.objects.filter(
            scheduler=scheduler,
            date=selected_date,
            time=selected_time
        ).exists():
            raise serializers.ValidationError("This time slot has already been booked.")

        return data


# endregion




