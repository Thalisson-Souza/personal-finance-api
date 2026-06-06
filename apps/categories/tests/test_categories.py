import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.categories.models import Category


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="thalisson",
        password="strong-test-password",
    )


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(
        username="other",
        password="strong-test-password",
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_categories_require_authentication():
    response = APIClient().get(reverse("category-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_category_sets_authenticated_user(authenticated_client, user):
    response = authenticated_client.post(
        reverse("category-list"),
        {"name": "Market", "type": Category.Type.EXPENSE},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    category = Category.objects.get()
    assert category.user == user
    assert category.name == "Market"
    assert category.type == Category.Type.EXPENSE
    assert "user" not in response.data


@pytest.mark.django_db
def test_list_categories_returns_only_authenticated_user_categories(
    authenticated_client,
    user,
    other_user,
):
    Category.objects.create(user=user, name="Salary", type=Category.Type.INCOME)
    Category.objects.create(user=other_user, name="Rent", type=Category.Type.EXPENSE)

    response = authenticated_client.get(reverse("category-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Salary"


@pytest.mark.django_db
def test_retrieve_category_from_another_user_returns_not_found(
    authenticated_client,
    other_user,
):
    category = Category.objects.create(
        user=other_user,
        name="Rent",
        type=Category.Type.EXPENSE,
    )

    response = authenticated_client.get(reverse("category-detail", args=[category.id]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_category_rejects_duplicate_name_and_type_for_same_user(
    authenticated_client,
    user,
):
    Category.objects.create(user=user, name="Market", type=Category.Type.EXPENSE)

    response = authenticated_client.post(
        reverse("category-list"),
        {"name": "Market", "type": Category.Type.EXPENSE},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Category.objects.count() == 1


@pytest.mark.django_db
def test_create_category_allows_same_name_with_different_type(
    authenticated_client,
    user,
):
    Category.objects.create(user=user, name="Bonus", type=Category.Type.INCOME)

    response = authenticated_client.post(
        reverse("category-list"),
        {"name": "Bonus", "type": Category.Type.EXPENSE},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.count() == 2
