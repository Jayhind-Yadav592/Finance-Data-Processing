from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone

from transactions.models import Transaction, TransactionType
from users.permissions import IsAnalystOrAdmin, IsActiveUser


class SummaryView(APIView):
    """
    GET /api/dashboard/summary/
    Returns: total income, total expense, net balance
    Access: Viewer, Analyst, Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        totals = qs.aggregate(
            total_income  = Sum('amount', filter=Q(type=TransactionType.INCOME)),
            total_expense = Sum('amount', filter=Q(type=TransactionType.EXPENSE)),
        )

        total_income  = totals['total_income']  or 0
        total_expense = totals['total_expense'] or 0
        net_balance   = total_income - total_expense

        return Response({
            'total_income':  total_income,
            'total_expense': total_expense,
            'net_balance':   net_balance,
        })


class CategoryWiseView(APIView):
    """
    GET /api/dashboard/category-wise/
    Returns: har category ka total amount (income + expense alag)
    Access: Analyst, Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        data = (
            qs.values('category', 'type')
              .annotate(total=Sum('amount'), count=Count('id'))
              .order_by('category', 'type')
        )

        return Response(list(data))


class MonthlyTrendView(APIView):
    """
    GET /api/dashboard/trends/
    Returns: har month ka income aur expense total
    Access: Analyst, Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        monthly = (
            qs.annotate(month=TruncMonth('date'))
              .values('month', 'type')
              .annotate(total=Sum('amount'))
              .order_by('month', 'type')
        )

        # Group by month for clean response
        result = {}
        for row in monthly:
            month_str = row['month'].strftime('%Y-%m')
            if month_str not in result:
                result[month_str] = {'month': month_str, 'income': 0, 'expense': 0}
            result[month_str][row['type']] = float(row['total'])

        return Response(sorted(result.values(), key=lambda x: x['month']))


class WeeklyTrendView(APIView):
    """
    GET /api/dashboard/trends/weekly/
    Returns: last 8 weeks ka income + expense
    Access: Analyst, Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        weekly = (
            qs.annotate(week=TruncWeek('date'))
              .values('week', 'type')
              .annotate(total=Sum('amount'))
              .order_by('week', 'type')
        )

        result = {}
        for row in weekly:
            week_str = row['week'].strftime('%Y-%m-%d')
            if week_str not in result:
                result[week_str] = {'week_start': week_str, 'income': 0, 'expense': 0}
            result[week_str][row['type']] = float(row['total'])

        return Response(sorted(result.values(), key=lambda x: x['week_start']))


class RecentActivityView(APIView):
    """
    GET /api/dashboard/recent/
    Returns: last 10 transactions
    Access: Viewer, Analyst, Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        from transactions.serializers import TransactionSerializer

        recent = Transaction.objects.filter(is_deleted=False).order_by('-date', '-created_at')[:10]
        serializer = TransactionSerializer(recent, many=True)
        return Response(serializer.data)