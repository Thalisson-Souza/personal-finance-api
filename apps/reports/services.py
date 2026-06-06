from decimal import Decimal

from django.db.models import Sum

from apps.transactions.models import Transaction


def format_money(value):
    return f"{value.quantize(Decimal('0.01'))}"


def get_monthly_summary(*, user, year, month):
    transactions = Transaction.objects.filter(
        user=user,
        date__year=year,
        date__month=month,
    )

    total_income = transactions.filter(type=Transaction.Type.INCOME).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")
    total_expense = transactions.filter(type=Transaction.Type.EXPENSE).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")
    balance = total_income - total_expense

    expenses_by_category = [
        {
            "category_id": item["category_id"],
            "category_name": item["category__name"],
            "total": format_money(item["total"]),
        }
        for item in transactions.filter(type=Transaction.Type.EXPENSE)
        .values("category_id", "category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    ]

    recent_transactions = [
        {
            "id": transaction.id,
            "description": transaction.description,
            "amount": format_money(transaction.amount),
            "type": transaction.type,
            "date": transaction.date.isoformat(),
            "category": transaction.category.name,
            "wallet": transaction.wallet.name,
        }
        for transaction in transactions.select_related("category", "wallet")[:5]
    ]

    return {
        "year": year,
        "month": month,
        "total_income": format_money(total_income),
        "total_expense": format_money(total_expense),
        "balance": format_money(balance),
        "expenses_by_category": expenses_by_category,
        "recent_transactions": recent_transactions,
    }
