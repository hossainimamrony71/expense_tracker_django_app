from django.urls import path
from .views import FinanceReportView,dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('finance-report/', FinanceReportView.as_view(), name='finance_report'),
]
