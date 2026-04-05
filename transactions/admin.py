
from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display   = ['id', 'user', 'type', 'category', 'amount', 'date', 'is_deleted']
    list_filter    = ['type', 'category', 'is_deleted']
    search_fields  = ['category', 'notes', 'user__email']
    ordering       = ['-date']
    date_hierarchy = 'date'


    def get_queryset(self, request):
        return Transaction.objects.all()