import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_returns_access_and_refresh_tokens(django_user_model):
    django_user_model.objects.create_user(
        username="thalisson",
        password="strong-test-password",
    )

    response = APIClient().post(
        reverse("auth-login"),
        {
            "username": "thalisson",
            "password": "strong-test-password",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["access"]
    assert response.data["refresh"]


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(django_user_model):
    django_user_model.objects.create_user(
        username="thalisson",
        password="strong-test-password",
    )

    response = APIClient().post(
        reverse("auth-login"),
        {
            "username": "thalisson",
            "password": "wrong-password",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in response.data
    assert "refresh" not in response.data
