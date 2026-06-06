from rest_framework import serializers

from apps.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "wallet",
            "category",
            "type",
            "description",
            "amount",
            "date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        wallet = attrs.get("wallet", getattr(self.instance, "wallet", None))
        category = attrs.get("category", getattr(self.instance, "category", None))
        transaction_type = attrs.get("type", getattr(self.instance, "type", None))

        errors = {}

        if wallet is not None and wallet.user_id != request.user.id:
            errors["wallet"] = "Wallet does not belong to the authenticated user."

        if category is not None and category.user_id != request.user.id:
            errors["category"] = "Category does not belong to the authenticated user."

        if category is not None and transaction_type and category.type != transaction_type:
            errors["category"] = "Category type must match transaction type."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
