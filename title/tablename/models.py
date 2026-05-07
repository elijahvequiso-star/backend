from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('employee', 'Employee'),
    ('mason', 'Mason'),
    ('electrician', 'Electrician'),
    ('driver', 'Driver'),
    ('foreman', 'Foreman'),
    ('admin', 'Admin'),
    ('hr', 'HR'),
]

EMPLOYEE_ROLES = ['employee', 'mason', 'electrician', 'driver', 'foreman']
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'location'], name='unique_site_name_location')
        ]
        ordering = ['name', 'location']

    def __str__(self):
        return f"{self.name} ({self.location})"


class Employee(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('ACTIVE', 'Active')]
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    role_locked = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_record')
    identity_verified = models.BooleanField(default=False)
    identity_document_name = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        computed = " ".join(part for part in parts if part).strip()
        return computed or self.name

    def save(self, *args, **kwargs):
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        if self.status == 'Active':
            self.status = 'ACTIVE'
        elif self.status == 'Inactive':
            self.status = 'PENDING'
        if self.mobile_number:
            self.mobile_number = self.mobile_number.strip()
        if not self.name:
            self.name = self.full_name
        elif self.first_name or self.last_name or self.middle_name:
            self.name = self.full_name
        if not self.position:
            self.position = 'Employee'
        if not self.department:
            self.department = 'Operations'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.TextField(default='General')
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
    type = models.TextField(default='Leave request')
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
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='payrolls')
    week_start = models.DateField()
    week_end = models.DateField(null=True, blank=True)
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
        constraints = [
            models.UniqueConstraint(fields=['employee', 'site', 'week_start'], name='unique_employee_site_week_payroll')
        ]
        indexes = [
            models.Index(fields=['site', 'week_start'], name='tablename_p_site_i_913165_idx'),
            models.Index(fields=['week_start', 'site'], name='tablename_p_week_st_ff5995_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.site_id and self.employee_id:
            self.site = self.employee.site
        self.total_hours = self.mon + self.tue + self.wed + self.thu + self.fri + self.sat + self.sun
        self.gross_pay = self.hourly_rate * self.total_hours
        self.net_pay = self.gross_pay - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} — Week of {self.week_start}"


class PasswordResetRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Completed', 'Completed'), ('Rejected', 'Rejected')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='password_reset_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.status}"
