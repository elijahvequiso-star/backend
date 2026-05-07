from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import ProgrammingError, OperationalError
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Site, Employee, Request, Leave, Salary, Payroll, UserProfile, PasswordResetRequest, EMPLOYEE_ROLES
from .serializers import SiteSerializer, EmployeeSerializer, RequestSerializer, LeaveSerializer, SalarySerializer, PayrollSerializer
import re

ROLE_DEPARTMENT_MAP = {
    'employee': ('Employee', 'Operations'),
    'mason': ('Mason', 'Construction'),
    'electrician': ('Electrician', 'Engineering'),
    'driver': ('Driver', 'Operations'),
    'foreman': ('Foreman', 'Construction'),
    'admin': ('Administrator', 'Management'),
    'hr': ('HR Manager', 'Human Resources'),
}


def get_or_create_login_profile(user):
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        if user.is_superuser:
            return UserProfile.objects.create(user=user, role='admin')
        if user.is_staff:
            return UserProfile.objects.create(user=user, role='hr')
        return None


@api_view(['POST'])
def register(request):
    employee_id = request.data.get('employee_id', '').strip().upper()
    mobile_number = request.data.get('mobile_number', '').strip()
    password = request.data.get('password', '').strip()
    confirm_password = request.data.get('confirm_password', '').strip()

    if not all([employee_id, mobile_number, password, confirm_password]):
        return Response({'error': 'Employee ID, mobile number, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if not re.match(r'^(\+?63|0)?9\d{9}$', mobile_number):
        return Response({'error': 'Enter a valid Philippine mobile number.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as exc:
        return Response({'error': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    employee = Employee.objects.filter(employee_id=employee_id).first()
    if employee is None:
        return Response({'error': 'Employee ID not found. Please contact HR.'}, status=status.HTTP_404_NOT_FOUND)

    if employee.is_registered or employee.user_id or User.objects.filter(username__iexact=employee_id).exists():
        return Response({'error': 'Account already exists for this Employee ID.'}, status=status.HTTP_400_BAD_REQUEST)

    role = employee.role if employee.role in EMPLOYEE_ROLES else 'employee'

    user = User.objects.create_user(
        username=employee_id,
        password=password,
        first_name=employee.first_name,
        last_name=employee.last_name
    )
    UserProfile.objects.create(user=user, role=role)
    employee.user = user
    employee.role = role
    employee.role_locked = True
    employee.is_registered = True
    employee.status = 'ACTIVE'
    employee.mobile_number = mobile_number
    employee.position, employee.department = ROLE_DEPARTMENT_MAP.get(role, ('Employee', 'Operations'))
    employee.save()

    return Response({'message': 'Account created successfully. You can now sign in.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('employee_id', request.data.get('username', '')).strip()
    password = request.data.get('password', '').strip()

    if not all([username, password]):
        return Response({'error': 'Employee ID and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    matching_usernames = list(
        User.objects.filter(username__iexact=username).values_list('username', flat=True)
    )
    login_candidates = [username]
    login_candidates.extend(name for name in matching_usernames if name not in login_candidates)

    user = None
    for candidate in login_candidates:
        user = authenticate(username=candidate, password=password)
        if user is not None:
            break

    if user is None:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    profile = get_or_create_login_profile(user)
    if profile is None:
        return Response({'error': 'No role assigned.'}, status=status.HTTP_403_FORBIDDEN)

    employee = None
    if profile.role in EMPLOYEE_ROLES:
        try:
            employee = Employee.objects.filter(user=user).first() or Employee.objects.filter(employee_id=username.upper()).first()
        except (ProgrammingError, OperationalError):
            return Response({
                'error': 'Employee database fields are missing. Please run backend migrations.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'message': 'Login successful.',
        'user': {
            'id': user.id,
            'username': user.username,
            'employee_id': employee.employee_id if employee else user.username,
            'full_name': employee.full_name if employee else f"{user.first_name} {user.last_name}".strip(),
            'role': profile.role,
            'position': employee.position if employee else profile.role,
            'status': employee.status if employee else 'ACTIVE',
            'email': user.email,
        }
    })


@api_view(['POST'])
def verify_identity(request):
    employee_id = request.data.get('employee_id', '').strip().upper()
    uploaded_file = request.FILES.get('identity_file')

    if not employee_id:
        return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not uploaded_file:
        return Response({'error': 'Please upload a clear image or PDF of your real ID.'}, status=status.HTTP_400_BAD_REQUEST)

    employee = Employee.objects.filter(employee_id=employee_id).first()
    if employee is None:
        return Response({'error': 'Employee record not found.'}, status=status.HTTP_404_NOT_FOUND)

    employee.identity_verified = True
    employee.identity_document_name = uploaded_file.name[:255]
    employee.save(update_fields=['identity_verified', 'identity_document_name'])

    profile = employee.user.profile if employee.user and hasattr(employee.user, 'profile') else None
    return Response({
        'message': 'Identity verified.',
        'user': {
            'id': employee.user.id if employee.user else None,
            'username': employee.user.username if employee.user else employee.employee_id,
            'employee_id': employee.employee_id,
            'full_name': employee.full_name,
            'role': profile.role if profile else employee.role,
        }
    })


@api_view(['POST'])
def forgot_password(request):
    employee_id = request.data.get('employee_id', '').strip().upper()
    mobile_number = request.data.get('mobile_number', '').strip()
    new_password = request.data.get('new_password', '').strip()
    confirm_password = request.data.get('confirm_password', '').strip()
    if not employee_id:
        return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    employee = Employee.objects.filter(employee_id=employee_id).first()
    if employee is None or employee.user_id is None:
        return Response({'error': 'No active account found for that Employee ID.'}, status=status.HTTP_404_NOT_FOUND)

    reset_request = PasswordResetRequest.objects.create(employee=employee)
    if new_password or confirm_password or mobile_number:
        if not all([mobile_number, new_password, confirm_password]):
            return Response({'error': 'Employee ID, mobile number, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if employee.mobile_number and employee.mobile_number != mobile_number:
            return Response({'error': 'Mobile number does not match HR records.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, user=employee.user)
        except ValidationError as exc:
            return Response({'error': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        employee.user.set_password(new_password)
        employee.user.save(update_fields=['password'])
        reset_request.status = 'Completed'
        reset_request.save(update_fields=['status'])
        return Response({'message': 'Password reset successful. You can now sign in with your new password.'})

    return Response({
        'message': 'Password reset request recorded. Please contact HR to complete identity verification.'
    })


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all().order_by('name', 'location')
    serializer_class = SiteSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('site', 'user').all().order_by('site__name', 'site__location', 'name')
    serializer_class = EmployeeSerializer


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.select_related('employee', 'site', 'employee__site').all().order_by('-created_at')
    serializer_class = RequestSerializer


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.select_related('employee', 'site', 'employee__site').all().order_by('-created_at')
    serializer_class = LeaveSerializer


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.select_related('employee', 'employee__site').all().order_by('employee__site__name', 'employee__site__location', 'employee__name')
    serializer_class = SalarySerializer


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer

    def get_queryset(self):
        queryset = Payroll.objects.select_related('employee', 'site', 'employee__site').all()
        site_id = self.request.query_params.get('site_id') or self.request.query_params.get('site')
        location = self.request.query_params.get('location')
        week_start = self.request.query_params.get('week_start')
        employee_id = self.request.query_params.get('employee_id')

        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if location:
            queryset = queryset.filter(site__location__iexact=location.strip())
        if week_start:
            queryset = queryset.filter(week_start=week_start)
        if employee_id:
            queryset = queryset.filter(employee__employee_id__iexact=employee_id.strip())

        return queryset.order_by('-week_start', 'site__name', 'site__location', 'employee__name')
