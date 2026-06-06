from django.urls import path

from apps.reports.views import monthly_summary


urlpatterns = [
    path("reports/monthly-summary/", monthly_summary, name="monthly-summary"),
]
