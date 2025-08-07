from datetime import date, datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from main_app.models import Scheduler, Booker, Appointment
from main_app.api import serializers
from main_app.pagination import AppointmentsCPagination
from main_app.permissions import IsScheduler, IsBooker
from main_app import pagination

# region ----- Admin -----

class AdminPanelViewSet(viewsets.ViewSet):
    """
    ViewSet for admin users to manage Schedulers, Bookers, and Appointments.
    Provides endpoints to list, retrieve, update, delete, and create resources.
    Only accessible to authenticated admin users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'], url_path='schedulers')
    def list_schedulers(self, request):
        """
        Retrieve a list of all schedulers.
        """
        queryset = Scheduler.objects.all()
        serializer = serializers.SchedulerListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'delete'], url_path='scheduler')
    def scheduler_detail(self, request, pk=None):
        """
        Retrieve, update, or delete a specific scheduler by primary key.

        GET: Return scheduler details.
        PUT: Partially update scheduler details.
        DELETE: Delete the scheduler.
        """
        scheduler = get_object_or_404(Scheduler, pk=pk)

        if request.method == 'GET':
            serializer = serializers.SchedulerDetailSerializer(scheduler)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.SchedulerDetailSerializer(scheduler, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            scheduler.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='bookers')
    def list_bookers(self, request):
        """
        Retrieve a list of all bookers.
        """
        queryset = Booker.objects.all()
        serializer = serializers.BookerListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'delete'], url_path='booker')
    def booker_detail(self, request, pk=None):
        """
        Retrieve, update, or delete a specific booker by primary key.

        GET: Return booker details.
        PUT: Partially update booker details.
        DELETE: Delete the booker.
        """
        booker = get_object_or_404(Booker, pk=pk)

        if request.method == 'GET':
            serializer = serializers.BookerDetailSerializer(booker)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.BookerDetailSerializer(booker, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            booker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='appointments')
    def list_appointments(self, request):
        """
        Retrieve a paginated list of all appointments, ordered by creation date descending.
        """
        queryset = Appointment.objects.all().order_by('-created_at')

        paginator = AppointmentsCPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = serializers.AppointmentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'delete'], url_path='appointment')
    def appointment_detail(self, request, pk=None):
        """
        Retrieve, update, or delete a specific appointment by primary key.

        GET: Return appointment details.
        PUT: Partially update appointment details.
        DELETE: Delete the appointment.
        """
        appointment = get_object_or_404(Appointment, pk=pk)

        if request.method == 'GET':
            serializer = serializers.AppointmentDetailSerializer(appointment)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.AppointmentDetailSerializer(appointment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create-appointment')
    def create_appointment(self, request):
        """
        Create a new appointment.
        """
        serializer = serializers.AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# endregion


# region ----- Scheduler -----

class SchedulerPanelViewSet(viewsets.ViewSet):
    """
    ViewSet for schedulers to manage their profile, bookers, and appointments.
    Only accessible by authenticated users with Scheduler role.
    """
    permission_classes = [IsAuthenticated, IsScheduler]

    def get_scheduler(self, request):
        """
        Helper method to retrieve the Scheduler instance associated with the current user.
        """
        role_user = request.user.role_profile
        return get_object_or_404(Scheduler, owner=role_user)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Retrieve the scheduler's profile data.
        """
        scheduler = self.get_scheduler(request)
        serializer = serializers.SchedulerPanelProfileSerializer(scheduler)
        return Response(serializer.data)

    @profile.mapping.put
    def update_profile(self, request):
        """
        Partially update the scheduler's profile.
        """
        scheduler = self.get_scheduler(request)
        serializer = serializers.SchedulerPanelUpdateProfileSerializer(scheduler, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bookers(self, request):
        """
        Retrieve the list of bookers assigned to the scheduler.
        """
        scheduler = self.get_scheduler(request)
        bookers = Booker.objects.filter(scheduler=scheduler)
        serializer = serializers.SchedulerPanelBookersProfileSerializer(bookers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def appointments(self, request):
        """
        Retrieve a paginated list of the scheduler's appointments, ordered by date descending.
        """
        scheduler = self.get_scheduler(request)
        queryset = Appointment.objects.filter(scheduler=scheduler).order_by('-date')

        # Instantiate the custom pagination class
        paginator = pagination.AppointmentsCPagination()  # must instantiate to get an object

        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = serializers.SchedulerPanelAppointmentsProfileSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If pagination is not applied
        serializer = serializers.SchedulerPanelAppointmentsProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='manage-appointments')
    def manage_appointments(self, request):
        """
        Manage scheduler's appointments with create, update, and delete actions.

        Expected POST data:
          - action: one of "create", "update", or "delete"
          - id: required for "update" and "delete"
          - other appointment fields depending on the action
        """
        scheduler = self.get_scheduler(request)
        action_type = request.data.get("action")

        if action_type == "create":
            serializer = serializers.SchedulerPanelAppointmentCreateSerializer(
                data=request.data,
                context={'scheduler': scheduler}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(scheduler=scheduler)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif action_type == "update":
            appointment_id = request.data.get("id")
            appointment = get_object_or_404(Appointment, id=appointment_id, scheduler=scheduler)
            serializer = serializers.SchedulerPanelAppointmentUpdateSerializer(
                appointment, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif action_type == "delete":
            appointment_id = request.data.get("id")
            appointment = get_object_or_404(Appointment, id=appointment_id, scheduler=scheduler)
            appointment.delete()
            return Response({"detail": "Appointment deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Invalid action type."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Retrieve aggregated data for the scheduler dashboard, including profile, bookers, and appointments.
        """
        scheduler = self.get_scheduler(request)

        # Profile information
        profile_data = serializers.SchedulerDashboardProfileSerializer(scheduler).data

        # Bookers related to the scheduler
        bookers = Booker.objects.filter(scheduler=scheduler)
        bookers_data = serializers.SchedulerDashboardBookersProfileSerializer(bookers, many=True).data

        # Appointments related to the scheduler
        appointments = Appointment.objects.filter(scheduler=scheduler)
        appointments_data = serializers.SchedulerDashboardAppointmentsProfileSerializer(appointments, many=True).data

        return Response({
            'profile': profile_data,
            'bookers': bookers_data,
            'appointments': appointments_data,
        })


# endregion


# region ----- Booker -----

class BookerPanelViewSet(viewsets.ViewSet):
    """
    ViewSet for bookers to manage their profile, appointments, and schedulers.
    Only accessible by authenticated users with Booker role.
    """
    permission_classes = [IsAuthenticated, IsBooker]

    def get_booker(self, request):
        """
        Helper method to retrieve the Booker instance associated with the current user.
        """
        role_user = request.user.role_profile
        return get_object_or_404(Booker, owner=role_user)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Retrieve the booker's profile data.
        """
        booker = self.get_booker(request)
        serializer = serializers.BookerPanelProfileSerializer(booker)
        return Response(serializer.data)

    @profile.mapping.put
    def update_profile(self, request):
        """
        Partially update the booker's profile.
        """
        booker = self.get_booker(request)
        serializer = serializers.BookerPanelUpdateProfileSerializer(booker, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-appointment')
    def my_appointment(self, request):
        """
        Retrieve the booker's upcoming active appointment (date/time not passed yet).
        """
        booker = self.get_booker(request)
        now = datetime.now()
        today = date.today()
        current_time = now.time()

        appointment = Appointment.objects.filter(
            booker=booker
        ).filter(
            Q(date__gt=today) |
            Q(date=today, time__gt=current_time)
        ).first()

        if not appointment:
            return Response({'detail': 'You do not have any active appointment.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.BookerPanelAppointmentsProfileSerializer(appointment)
        return Response(serializer.data)

    @my_appointment.mapping.put
    def update_my_appointment(self, request):
        """
        Partially update the booker's upcoming active appointment.
        """
        booker = self.get_booker(request)
        now = datetime.now()
        today = date.today()
        current_time = now.time()

        appointment = Appointment.objects.filter(
            booker=booker
        ).filter(
            Q(date__gt=today) |
            Q(date=today, time__gt=current_time)
        ).first()

        if not appointment:
            return Response({'detail': 'No appointment found to update.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.BookerPanelUpdateAppointmentProfileSerializer(
            appointment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='reserve-appointment')
    def reserve_appointment(self, request):
        """
        Reserve a new appointment if the booker does not have any active appointment.
        """
        booker = self.get_booker(request)
        now = datetime.now()

        active_appointment_exists = Appointment.objects.filter(
            booker=booker
        ).filter(
            Q(date__gt=now.date()) |
            Q(date=now.date(), time__gt=now.time())
        ).exists()

        if active_appointment_exists:
            return Response(
                {"detail": "You already have an active appointment and cannot reserve a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = serializers.BookerAppointmentCreateSerializer(data=request.data, context={'booker': booker})
        serializer.is_valid(raise_exception=True)
        serializer.save(booker=booker)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='past-appointments')
    def past_appointments(self, request):
        """
        Retrieve the list of booker's past appointments (date/time passed).
        """
        booker = self.get_booker(request)
        now = datetime.now()

        queryset = Appointment.objects.filter(
            booker=booker
        ).filter(
            Q(date__lt=now.date()) |
            Q(date=now.date(), time__lte=now.time())
        ).order_by('-date', '-time')

        serializer = serializers.AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-scheduler')
    def add_scheduler(self, request):
        """
        Add a scheduler to the booker's personal scheduler list.
        Only schedulers with is_public_search=True are allowed to be added.
        """
        booker = self.get_booker(request)

        allowed_schedulers = Scheduler.objects.filter(is_public_search=True)

        serializer = serializers.AddSchedulerSerializer(
            data=request.data,
            context={'booker': booker, 'allowed_schedulers': allowed_schedulers}
        )
        serializer.is_valid(raise_exception=True)
        scheduler = serializer.save()
        return Response({'detail': f'Scheduler {scheduler.name} has been added to your list.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='list-schedulers')
    def list_schedulers(self, request):
        """
        List all schedulers added by the booker.
        """
        booker = self.get_booker(request)
        schedulers = booker.schedulers.all()
        serializer = serializers.SchedulerListSerializer(schedulers, many=True)
        return Response(serializer.data)


# endregion
