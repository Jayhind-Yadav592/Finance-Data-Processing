from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer, TransactionCreateSerializer
from .filters import TransactionFilter
from users.permissions import IsAdmin, IsAnalystOrAdmin, IsActiveUser


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Access Control:
      GET    (list, retrieve) → Viewer, Analyst, Admin
      POST   (create)        → Analyst, Admin
      PUT    (update)        → Admin only
      DELETE (destroy)       → Admin only (soft delete)
    """
    filterset_class = TransactionFilter
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        # Soft deleted records kabhi bhi return nahi honge
        return Transaction.objects.filter(is_deleted=False).select_related('user')

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_permissions(self):
        """Action ke hisaab se permissions decide karna."""
        if self.action in ('list', 'retrieve'):
            permission_classes = [IsAuthenticated, IsActiveUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]
        else:  # update, partial_update, destroy
            permission_classes = [IsAuthenticated, IsActiveUser, IsAdmin]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Hard delete ki jagah soft delete — record DB mein rehta hai
        lekin list mein nahi dikhta.
        """
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({'message': 'Transaction deleted successfully.'}, status=status.HTTP_200_OK)
