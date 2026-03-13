from django.contrib import admin
from .models import Employee, Request, Leave, SalaryPayment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'position', 'department', 'hire_date']

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'status', 'created_at']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'status']

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'amount', 'month', 'year', 'paid_date']
