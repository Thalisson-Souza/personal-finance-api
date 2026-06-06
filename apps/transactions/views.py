from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user).select_related(
            "category",
            "wallet",
        )
        params = self.request.query_params

        if year := params.get("year"):
            queryset = queryset.filter(date__year=year)

        if month := params.get("month"):
            queryset = queryset.filter(date__month=month)

        if transaction_type := params.get("type"):
            queryset = queryset.filter(type=transaction_type)

        if category := params.get("category"):
            queryset = queryset.filter(category_id=category)

        if wallet := params.get("wallet"):
            queryset = queryset.filter(wallet_id=wallet)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
