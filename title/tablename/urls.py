from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, EmployeeViewSet, RequestViewSet, LeaveViewSet, SalaryViewSet, PayrollViewSet, register, login_view, verify_identity, forgot_password

router = DefaultRouter()
router.register(r'sites', SiteViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'salary', SalaryViewSet)
router.register(r'payroll', PayrollViewSet)

urlpatterns = [
    path('auth/register/', register),
    path('auth/login/', login_view),
    path('auth/verify-identity/', verify_identity),
    path('auth/forgot-password/', forgot_password),
    path('', include(router.urls)),
]
