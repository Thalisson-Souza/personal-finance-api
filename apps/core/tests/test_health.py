from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@override_settings(ALLOWED_HOSTS=["testserver"])
def test_health_check_returns_ok():
    response = APIClient().get(reverse("health-check"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
