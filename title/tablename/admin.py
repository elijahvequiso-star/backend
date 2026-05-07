from django.contrib import admin
from .models import Site, Employee, Request, Leave, Salary, Payroll, UserProfile, PasswordResetRequest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'mobile_number', 'role', 'identity_verified', 'position', 'department', 'site', 'status']
    search_fields = ['employee_id', 'first_name', 'last_name', 'name', 'mobile_number']
    readonly_fields = ['role_locked', 'identity_verified', 'identity_document_name']

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'site', 'type', 'date', 'status']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'site', 'type', 'start_date', 'end_date', 'status']

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'hourly_rate', 'hours_worked', 'computed_salary']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'site', 'week_start', 'total_hours', 'net_pay']
    list_filter = ['site', 'week_start']
    search_fields = ['employee__employee_id', 'employee__name', 'site__name', 'site__location']

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'status', 'created_at']
    list_filter = ['status', 'created_at']
