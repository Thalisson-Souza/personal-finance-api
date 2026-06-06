from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.transactions.models import Transaction
from apps.wallets.models import Wallet


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="thalisson-reports",
        password="strong-test-password",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="other-reports",
        password="strong-test-password",
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_transaction(*, user, name, transaction_type, amount, date):
    wallet = Wallet.objects.create(user=user, name=f"{name} wallet")
    category = Category.objects.create(user=user, name=name, type=transaction_type)
    return Transaction.objects.create(
        user=user,
        wallet=wallet,
        category=category,
        type=transaction_type,
        description=name,
        amount=Decimal(amount),
        date=date,
    )


@pytest.mark.django_db
def test_monthly_summary_requires_authentication():
    response = APIClient().get(reverse("monthly-summary"), {"year": 2026, "month": 6})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_monthly_summary_requires_year_and_month(authenticated_client):
    response = authenticated_client.get(reverse("monthly-summary"), {"year": 2026})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_monthly_summary_rejects_invalid_month(authenticated_client):
    response = authenticated_client.get(
        reverse("monthly-summary"),
        {"year": 2026, "month": 13},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_monthly_summary_returns_month_totals_and_recent_transactions(
    authenticated_client,
    user,
):
    create_transaction(
        user=user,
        name="Salary",
        transaction_type=Transaction.Type.INCOME,
        amount="5000.00",
        date="2026-06-05",
    )
    market = create_transaction(
        user=user,
        name="Market",
        transaction_type=Transaction.Type.EXPENSE,
        amount="120.50",
        date="2026-06-06",
    )
    rent = create_transaction(
        user=user,
        name="Rent",
        transaction_type=Transaction.Type.EXPENSE,
        amount="1000.00",
        date="2026-06-01",
    )
    create_transaction(
        user=user,
        name="Old Market",
        transaction_type=Transaction.Type.EXPENSE,
        amount="50.00",
        date="2026-05-31",
    )

    response = authenticated_client.get(
        reverse("monthly-summary"),
        {"year": 2026, "month": 6},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["year"] == 2026
    assert response.data["month"] == 6
    assert response.data["total_income"] == "5000.00"
    assert response.data["total_expense"] == "1120.50"
    assert response.data["balance"] == "3879.50"
    assert response.data["expenses_by_category"] == [
        {
            "category_id": rent.category_id,
            "category_name": "Rent",
            "total": "1000.00",
        },
        {
            "category_id": market.category_id,
            "category_name": "Market",
            "total": "120.50",
        },
    ]
    assert [item["description"] for item in response.data["recent_transactions"]] == [
        "Market",
        "Salary",
        "Rent",
    ]


@pytest.mark.django_db
def test_monthly_summary_ignores_other_user_transactions(
    authenticated_client,
    user,
    other_user,
):
    create_transaction(
        user=user,
        name="Market",
        transaction_type=Transaction.Type.EXPENSE,
        amount="120.50",
        date="2026-06-06",
    )
    create_transaction(
        user=other_user,
        name="Other Salary",
        transaction_type=Transaction.Type.INCOME,
        amount="9999.00",
        date="2026-06-06",
    )

    response = authenticated_client.get(
        reverse("monthly-summary"),
        {"year": 2026, "month": 6},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_income"] == "0.00"
    assert response.data["total_expense"] == "120.50"
    assert response.data["balance"] == "-120.50"
