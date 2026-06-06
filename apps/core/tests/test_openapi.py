from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@override_settings(ALLOWED_HOSTS=["testserver"])
def test_openapi_schema_returns_api_metadata():
    response = APIClient().get(reverse("schema"))

    assert response.status_code == 200
    assert response.data["info"]["title"] == "Personal Finance API"
    assert response.data["info"]["version"] == "0.1.0"
    assert "/api/categories/" in response.data["paths"]


@override_settings(ALLOWED_HOSTS=["testserver"])
def test_openapi_docs_page_returns_success():
    response = APIClient().get(reverse("docs"))

    assert response.status_code == 200
