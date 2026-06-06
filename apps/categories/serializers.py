from rest_framework import serializers

from apps.categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        name = attrs.get("name", getattr(self.instance, "name", None))
        category_type = attrs.get("type", getattr(self.instance, "type", None))

        queryset = Category.objects.filter(
            user=request.user,
            name=name,
            type=category_type,
        )

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {"name": "Category with this name and type already exists."}
            )

        return attrs
