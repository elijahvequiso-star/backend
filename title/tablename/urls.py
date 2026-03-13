from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, RequestViewSet, LeaveViewSet, SalaryPaymentViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'salary-payments', SalaryPaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
