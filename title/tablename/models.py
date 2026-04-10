from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('mason', 'Mason'),
    ('electrician', 'Electrician'),
    ('driver', 'Driver'),
    ('foreman', 'Foreman'),
    ('admin', 'Admin'),
    ('hr', 'HR'),
]

EMPLOYEE_ROLES = ['mason', 'electrician', 'driver', 'foreman']
ADMIN_ROLES = ['admin', 'hr']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Site(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')]
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=100, default='General')
    date = models.DateField(default='2026-01-01')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-assign site from employee's site if not explicitly set
        if not self.site_id and self.employee.site:
            self.site = self.employee.site
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.employee.name}"


class Leave(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=100, default='Sick Leave')
    start_date = models.DateField(default='2026-01-01')
    end_date = models.DateField(default='2026-01-01')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-assign site from employee's site
        if not self.site_id and self.employee.site:
            self.site = self.employee.site
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.type}"


class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    computed_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.computed_salary = (self.hourly_rate * self.hours_worked) - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - ₱{self.computed_salary}"


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    week_start = models.DateField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mon = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tue = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wed = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    thu = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fri = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sun = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'week_start')

    def save(self, *args, **kwargs):
        self.total_hours = self.mon + self.tue + self.wed + self.thu + self.fri + self.sat + self.sun
        self.gross_pay = self.hourly_rate * self.total_hours
        self.net_pay = self.gross_pay - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} — Week of {self.week_start}"
