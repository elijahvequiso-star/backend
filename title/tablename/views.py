from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Site, Employee, Request, Leave, Salary, Payroll, UserProfile, EMPLOYEE_ROLES
from .serializers import SiteSerializer, EmployeeSerializer, RequestSerializer, LeaveSerializer, SalarySerializer, PayrollSerializer

ROLE_DEPARTMENT_MAP = {
    'mason': ('Mason', 'Construction'),
    'electrician': ('Electrician', 'Engineering'),
    'driver': ('Driver', 'Operations'),
    'foreman': ('Foreman', 'Construction'),
    'admin': ('Administrator', 'Management'),
    'hr': ('HR Manager', 'Human Resources'),
}


@api_view(['POST'])
def register(request):
    full_name = request.data.get('full_name', '').strip()
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    role = request.data.get('role', '').strip()

    if not all([full_name, username, password, role]):
        return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if role not in EMPLOYEE_ROLES:
        return Response({'error': 'Invalid role.'}, status=status.HTTP_403_FORBIDDEN)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    name_parts = full_name.split(' ', 1)
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=name_parts[0],
        last_name=name_parts[1] if len(name_parts) > 1 else ''
    )
    UserProfile.objects.create(user=user, role=role)
    position, department = ROLE_DEPARTMENT_MAP.get(role, (role.title(), 'General'))
    Employee.objects.create(name=full_name, position=position, department=department, status='Active')

    return Response({'message': 'Account created successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not all([username, password]):
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': 'No role assigned.'}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        'message': 'Login successful.',
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'role': profile.role,
            'email': user.email,
        }
    })


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('site__name', 'name')
    serializer_class = EmployeeSerializer


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all().order_by('-created_at')
    serializer_class = RequestSerializer


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all().order_by('-created_at')
    serializer_class = LeaveSerializer


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all().order_by('employee__site__name', 'employee__name')
    serializer_class = SalarySerializer


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all().order_by('-week_start', 'employee__site__name', 'employee__name')
    serializer_class = PayrollSerializer
