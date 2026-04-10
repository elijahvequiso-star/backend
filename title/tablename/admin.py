from django.contrib import admin
from .models import Site, Employee, Request, Leave, Salary, Payroll, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'department', 'site', 'status']

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
    list_display = ['employee', 'week_start', 'total_hours', 'net_pay']
