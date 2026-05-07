from rest_framework import serializers
from .models import Site, Employee, Request, Leave, Salary, Payroll
import re


class SiteSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = '__all__'

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True, default='Unassigned')
    site_location = serializers.CharField(source='site.location', read_only=True, default='No location')
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['role_locked', 'user', 'is_registered', 'identity_verified', 'identity_document_name']

    def validate_employee_id(self, value):
        if not value:
            return value
        normalized = value.strip().upper()
        if not re.match(r'^[A-Z0-9-]+$', normalized):
            raise serializers.ValidationError('Employee ID may contain only letters, numbers, and dashes.')
        duplicate = Employee.objects.filter(employee_id__iexact=normalized)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError('Invalid existing ID number. This Employee ID is already registered.')
        return normalized

    def validate_mobile_number(self, value):
        if not value:
            return value
        normalized = value.strip()
        if not re.match(r'^(\+?63|0)?9\d{9}$', normalized):
            raise serializers.ValidationError('Enter a valid Philippine mobile number.')
        return normalized

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if not attrs.get('employee_id'):
                raise serializers.ValidationError({'employee_id': 'Employee ID is required.'})
            if not attrs.get('first_name'):
                raise serializers.ValidationError({'first_name': 'First name is required.'})
            if not attrs.get('last_name'):
                raise serializers.ValidationError({'last_name': 'Last name is required.'})
            if not attrs.get('role'):
                raise serializers.ValidationError({'role': 'Role / position is required.'})
        if self.instance and self.instance.role_locked and 'role' in attrs and attrs['role'] != self.instance.role:
            raise serializers.ValidationError({'role': 'Role is system-controlled after account activation.'})
        return attrs


class RequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = '__all__'

    def get_site_name(self, obj):
        # Show site from request.site or fallback to employee.site
        if obj.site:
            return obj.site.name
        if obj.employee.site:
            return obj.employee.site.name
        return 'Unassigned'


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.SerializerMethodField()

    class Meta:
        model = Leave
        fields = '__all__'

    def get_site_name(self, obj):
        if obj.site:
            return obj.site.name
        if obj.employee.site:
            return obj.employee.site.name
        return 'Unassigned'


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.CharField(source='employee.site.name', read_only=True, default='Unassigned')

    class Meta:
        model = Salary
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.SerializerMethodField()
    site_id = serializers.SerializerMethodField()
    site_location = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = '__all__'

    def get_site(self, obj):
        return obj.site or obj.employee.site

    def get_site_name(self, obj):
        site = self.get_site(obj)
        return site.name if site else 'Unassigned'

    def get_site_id(self, obj):
        site = self.get_site(obj)
        return site.id if site else None

    def get_site_location(self, obj):
        site = self.get_site(obj)
        return site.location if site else 'No location'

    def validate(self, attrs):
        employee = attrs.get('employee') or getattr(self.instance, 'employee', None)
        site = attrs.get('site')
        if employee and site is None:
            attrs['site'] = employee.site
        if employee and attrs.get('site') and employee.site_id and attrs['site'].id != employee.site_id:
            raise serializers.ValidationError({'site': 'Payroll site must match the employee assigned site.'})
        return attrs
