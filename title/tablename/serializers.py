from rest_framework import serializers
from .models import Site, Employee, Request, Leave, Salary, Payroll


class SiteSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = '__all__'

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True, default='Unassigned')

    class Meta:
        model = Employee
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
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
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.CharField(source='employee.site.name', read_only=True, default='Unassigned')

    class Meta:
        model = Salary
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_position = serializers.CharField(source='employee.position', read_only=True)
    site_name = serializers.CharField(source='employee.site.name', read_only=True, default='Unassigned')

    class Meta:
        model = Payroll
        fields = '__all__'
