from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Role
from transactions.models import Transaction, TransactionType
from datetime import date


def create_user(email, role):
    return User.objects.create_user(email=email, name='Test', password='Pass@1234', role=role)


def get_token(client, email):
    res = client.post(reverse('login'), {'email': email, 'password': 'Pass@1234'}, format='json')
    return res.data.get('access', '')


def make_transaction(user, t_type, amount, category='salary'):
    return Transaction.objects.create(
        user=user, amount=amount, type=t_type,
        category=category, date=date.today(),
    )


class DashboardSummaryTests(TestCase):
    def setUp(self):
        self.client  = APIClient()
        self.admin   = create_user('admin@d.com',   Role.ADMIN)
        self.analyst = create_user('analyst@d.com', Role.ANALYST)
        self.viewer  = create_user('viewer@d.com',  Role.VIEWER)

        # Known test data
        make_transaction(self.admin, TransactionType.INCOME,  10000, 'salary')
        make_transaction(self.admin, TransactionType.INCOME,  5000,  'bonus')
        make_transaction(self.admin, TransactionType.EXPENSE, 3000,  'rent')
        make_transaction(self.admin, TransactionType.EXPENSE, 2000,  'food')

    def auth(self, email):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ── Summary ───────────────────────────────────────────────────────────
    def test_summary_returns_correct_totals(self):
        self.auth('admin@d.com')
        res = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(float(res.data['total_income']),  15000)
        self.assertEqual(float(res.data['total_expense']),  5000)
        self.assertEqual(float(res.data['net_balance']),   10000)

    def test_viewer_can_access_summary(self):
        self.auth('viewer@d.com')
        res = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_summary_requires_auth(self):
        self.client.credentials()
        res = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Category-wise ─────────────────────────────────────────────────────
    def test_analyst_can_access_category_wise(self):
        self.auth('analyst@d.com')
        res = self.client.get(reverse('dashboard-category'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_viewer_cannot_access_category_wise(self):
        self.auth('viewer@d.com')
        res = self.client.get(reverse('dashboard-category'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Trends ────────────────────────────────────────────────────────────
    def test_analyst_can_access_monthly_trends(self):
        self.auth('analyst@d.com')
        res = self.client.get(reverse('dashboard-monthly'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_viewer_cannot_access_monthly_trends(self):
        self.auth('viewer@d.com')
        res = self.client.get(reverse('dashboard-monthly'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Recent ────────────────────────────────────────────────────────────
    def test_recent_returns_max_10(self):
        # Create 15 more transactions
        for i in range(15):
            make_transaction(self.admin, TransactionType.INCOME, 100 * (i + 1))
        self.auth('viewer@d.com')
        res = self.client.get(reverse('dashboard-recent'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(res.data), 10)

    def test_soft_deleted_not_in_summary(self):
        # Soft-delete the income transactions
        Transaction.objects.filter(type=TransactionType.INCOME).update(is_deleted=True)
        self.auth('admin@d.com')
        res = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(float(res.data['total_income']), 0)
        self.assertEqual(float(res.data['net_balance']),  -5000)