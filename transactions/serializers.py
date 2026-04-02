from rest_framework import serializers
from .models import Transaction, TransactionType
import decimal


class TransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Transaction
        fields = [
            'id', 'user', 'user_email', 'amount', 'type',
            'category', 'date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_user_email(self, obj):
        return obj.user.email

    def validate_amount(self, value):
        if value <= decimal.Decimal('0'):
            raise serializers.ValidationError('Amount must be greater than 0.')
        return value

    def validate_type(self, value):
        if value not in TransactionType.values:
            raise serializers.ValidationError(f'Type must be one of: {TransactionType.values}')
        return value

    def validate_category(self, value):
        if not value.strip():
            raise serializers.ValidationError('Category cannot be empty.')
        return value.strip().lower()


class TransactionCreateSerializer(TransactionSerializer):
    """Create ke liye — user automatically set hoga logged-in user se."""

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)