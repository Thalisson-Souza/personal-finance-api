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
        username="thalisson-transactions",
        password="strong-test-password",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="other-transactions",
        password="strong-test-password",
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def wallet(user):
    return Wallet.objects.create(
        user=user,
        name="Nubank",
        initial_balance=Decimal("0.00"),
    )


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        user=user,
        name="Market",
        type=Category.Type.EXPENSE,
    )


@pytest.mark.django_db
def test_transactions_require_authentication():
    response = APIClient().get(reverse("transaction-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_transaction_sets_authenticated_user(
    authenticated_client,
    user,
    wallet,
    expense_category,
):
    response = authenticated_client.post(
        reverse("transaction-list"),
        {
            "wallet": wallet.id,
            "category": expense_category.id,
            "type": Transaction.Type.EXPENSE,
            "description": "Groceries",
            "amount": "120.50",
            "date": "2026-06-06",
            "notes": "Weekly market",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    transaction = Transaction.objects.get()
    assert transaction.user == user
    assert transaction.amount == Decimal("120.50")
    assert response.data["amount"] == "120.50"
    assert "user" not in response.data


@pytest.mark.django_db
def test_list_transactions_returns_only_authenticated_user_transactions(
    authenticated_client,
    user,
    other_user,
    wallet,
    expense_category,
):
    other_wallet = Wallet.objects.create(user=other_user, name="Itau")
    other_category = Category.objects.create(
        user=other_user,
        name="Rent",
        type=Category.Type.EXPENSE,
    )
    Transaction.objects.create(
        user=user,
        wallet=wallet,
        category=expense_category,
        type=Transaction.Type.EXPENSE,
        description="Groceries",
        amount=Decimal("120.50"),
        date="2026-06-06",
    )
    Transaction.objects.create(
        user=other_user,
        wallet=other_wallet,
        category=other_category,
        type=Transaction.Type.EXPENSE,
        description="Rent",
        amount=Decimal("1000.00"),
        date="2026-06-06",
    )

    response = authenticated_client.get(reverse("transaction-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["description"] == "Groceries"


@pytest.mark.django_db
def test_retrieve_transaction_from_another_user_returns_not_found(
    authenticated_client,
    other_user,
):
    other_wallet = Wallet.objects.create(user=other_user, name="Itau")
    other_category = Category.objects.create(
        user=other_user,
        name="Rent",
        type=Category.Type.EXPENSE,
    )
    transaction = Transaction.objects.create(
        user=other_user,
        wallet=other_wallet,
        category=other_category,
        type=Transaction.Type.EXPENSE,
        description="Rent",
        amount=Decimal("1000.00"),
        date="2026-06-06",
    )

    response = authenticated_client.get(
        reverse("transaction-detail", args=[transaction.id])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_transaction_rejects_wallet_from_another_user(
    authenticated_client,
    other_user,
    expense_category,
):
    other_wallet = Wallet.objects.create(user=other_user, name="Itau")

    response = authenticated_client.post(
        reverse("transaction-list"),
        {
            "wallet": other_wallet.id,
            "category": expense_category.id,
            "type": Transaction.Type.EXPENSE,
            "description": "Groceries",
            "amount": "120.50",
            "date": "2026-06-06",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_rejects_category_from_another_user(
    authenticated_client,
    other_user,
    wallet,
):
    other_category = Category.objects.create(
        user=other_user,
        name="Rent",
        type=Category.Type.EXPENSE,
    )

    response = authenticated_client.post(
        reverse("transaction-list"),
        {
            "wallet": wallet.id,
            "category": other_category.id,
            "type": Transaction.Type.EXPENSE,
            "description": "Groceries",
            "amount": "120.50",
            "date": "2026-06-06",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_rejects_category_type_mismatch(
    authenticated_client,
    user,
    wallet,
):
    income_category = Category.objects.create(
        user=user,
        name="Salary",
        type=Category.Type.INCOME,
    )

    response = authenticated_client.post(
        reverse("transaction-list"),
        {
            "wallet": wallet.id,
            "category": income_category.id,
            "type": Transaction.Type.EXPENSE,
            "description": "Groceries",
            "amount": "120.50",
            "date": "2026-06-06",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_rejects_zero_amount(
    authenticated_client,
    wallet,
    expense_category,
):
    response = authenticated_client.post(
        reverse("transaction-list"),
        {
            "wallet": wallet.id,
            "category": expense_category.id,
            "type": Transaction.Type.EXPENSE,
            "description": "Groceries",
            "amount": "0.00",
            "date": "2026-06-06",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_filter_transactions_by_month_type_category_and_wallet(
    authenticated_client,
    user,
    wallet,
    expense_category,
):
    income_category = Category.objects.create(
        user=user,
        name="Salary",
        type=Category.Type.INCOME,
    )
    Transaction.objects.create(
        user=user,
        wallet=wallet,
        category=expense_category,
        type=Transaction.Type.EXPENSE,
        description="June groceries",
        amount=Decimal("120.50"),
        date="2026-06-06",
    )
    Transaction.objects.create(
        user=user,
        wallet=wallet,
        category=income_category,
        type=Transaction.Type.INCOME,
        description="June salary",
        amount=Decimal("5000.00"),
        date="2026-06-05",
    )

    response = authenticated_client.get(
        reverse("transaction-list"),
        {
            "year": "2026",
            "month": "6",
            "type": Transaction.Type.EXPENSE,
            "category": expense_category.id,
            "wallet": wallet.id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["description"] == "June groceries"
