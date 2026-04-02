from django.db import models
from django.conf import settings


class TransactionType(models.TextChoices):
    INCOME  = 'income',  'Income'
    EXPENSE = 'expense', 'Expense'


class Transaction(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    type        = models.CharField(max_length=10, choices=TransactionType.choices)
    category    = models.CharField(max_length=100)
    date        = models.DateField()
    notes       = models.TextField(blank=True, default='')
    is_deleted  = models.BooleanField(default=False)   # soft delete support
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.type} | {self.category} | {self.amount}'
