from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    CORS_ALLOWED_ORIGINS=["http://localhost:3000"],
)
def test_allowed_origin_receives_cors_header():
    response = APIClient().get(
        reverse("health-check"),
        HTTP_ORIGIN="http://localhost:3000",
    )

    assert response.status_code == 200
    assert response["access-control-allow-origin"] == "http://localhost:3000"
