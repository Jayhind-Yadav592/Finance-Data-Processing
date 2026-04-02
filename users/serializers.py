from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model  = User
        fields = ['id', 'email', 'name', 'password', 'role']
        extra_kwargs = {
            'role': {'default': Role.VIEWER},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'email', 'name', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']


class UpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['role']

    def validate_role(self, value):
        if value not in Role.values:
            raise serializers.ValidationError(f'Role must be one of: {Role.values}')
        return value


class UpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['is_active']