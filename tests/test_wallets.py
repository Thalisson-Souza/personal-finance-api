from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.wallets.models import Wallet


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="thalisson-wallets",
        password="strong-test-password",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="other-wallets",
        password="strong-test-password",
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_wallets_require_authentication():
    response = APIClient().get(reverse("wallet-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_wallet_sets_authenticated_user(authenticated_client, user):
    response = authenticated_client.post(
        reverse("wallet-list"),
        {"name": "Nubank", "initial_balance": "150.75"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    wallet = Wallet.objects.get()
    assert wallet.user == user
    assert wallet.name == "Nubank"
    assert wallet.initial_balance == Decimal("150.75")
    assert response.data["initial_balance"] == "150.75"
    assert "user" not in response.data


@pytest.mark.django_db
def test_create_wallet_uses_zero_as_default_initial_balance(authenticated_client):
    response = authenticated_client.post(
        reverse("wallet-list"),
        {"name": "Cash"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Wallet.objects.get().initial_balance == Decimal("0.00")
    assert response.data["initial_balance"] == "0.00"


@pytest.mark.django_db
def test_list_wallets_returns_only_authenticated_user_wallets(
    authenticated_client,
    user,
    other_user,
):
    Wallet.objects.create(user=user, name="Nubank", initial_balance=Decimal("10.00"))
    Wallet.objects.create(user=other_user, name="Itau", initial_balance=Decimal("20.00"))

    response = authenticated_client.get(reverse("wallet-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Nubank"


@pytest.mark.django_db
def test_retrieve_wallet_from_another_user_returns_not_found(
    authenticated_client,
    other_user,
):
    wallet = Wallet.objects.create(
        user=other_user,
        name="Itau",
        initial_balance=Decimal("20.00"),
    )

    response = authenticated_client.get(reverse("wallet-detail", args=[wallet.id]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_wallet_rejects_duplicate_name_for_same_user(
    authenticated_client,
    user,
):
    Wallet.objects.create(user=user, name="Nubank", initial_balance=Decimal("0.00"))

    response = authenticated_client.post(
        reverse("wallet-list"),
        {"name": "Nubank", "initial_balance": "50.00"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Wallet.objects.count() == 1


@pytest.mark.django_db
def test_create_wallet_allows_same_name_for_different_users(
    authenticated_client,
    other_user,
):
    Wallet.objects.create(
        user=other_user,
        name="Nubank",
        initial_balance=Decimal("0.00"),
    )

    response = authenticated_client.post(
        reverse("wallet-list"),
        {"name": "Nubank", "initial_balance": "50.00"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Wallet.objects.count() == 2
