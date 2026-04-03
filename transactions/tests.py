from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Role
from transactions.models import Transaction, TransactionType
from datetime import date


def create_user(email, role=Role.VIEWER):
    return User.objects.create_user(email=email, name='Test', password='Pass@1234', role=role)


def get_token(client, email):
    res = client.post(reverse('login'), {'email': email, 'password': 'Pass@1234'}, format='json')
    return res.data.get('access', '')


def make_transaction(user, t_type=TransactionType.INCOME, category='salary', amount=5000):
    return Transaction.objects.create(
        user=user,
        amount=amount,
        type=t_type,
        category=category,
        date=date.today(),
        notes='Test transaction',
    )


class TransactionCRUDTests(TestCase):
    def setUp(self):
        self.client  = APIClient()
        self.admin   = create_user('admin@t.com',   Role.ADMIN)
        self.analyst = create_user('analyst@t.com', Role.ANALYST)
        self.viewer  = create_user('viewer@t.com',  Role.VIEWER)

    def auth(self, email):
        token = get_token(self.client, email)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ── List (all roles can view) ──────────────────────────────────────────
    def test_viewer_can_list_transactions(self):
        self.auth('viewer@t.com')
        res = self.client.get(reverse('transaction-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_analyst_can_list_transactions(self):
        self.auth('analyst@t.com')
        res = self.client.get(reverse('transaction-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ── Create ────────────────────────────────────────────────────────────
    def test_analyst_can_create_transaction(self):
        self.auth('analyst@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': 10000, 'type': 'income',
            'category': 'salary', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_transaction(self):
        self.auth('admin@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': 5000, 'type': 'expense',
            'category': 'rent', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create_transaction(self):
        self.auth('viewer@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': 100, 'type': 'income',
            'category': 'salary', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Update (admin only) ───────────────────────────────────────────────
    def test_admin_can_update_transaction(self):
        t = make_transaction(self.admin)
        self.auth('admin@t.com')
        res = self.client.patch(
            reverse('transaction-detail', args=[t.id]),
            {'amount': 99999}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_analyst_cannot_update_transaction(self):
        t = make_transaction(self.admin)
        self.auth('analyst@t.com')
        res = self.client.patch(
            reverse('transaction-detail', args=[t.id]),
            {'amount': 99999}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Delete (admin only, soft delete) ─────────────────────────────────
    def test_admin_can_soft_delete_transaction(self):
        t = make_transaction(self.admin)
        self.auth('admin@t.com')
        res = self.client.delete(reverse('transaction-detail', args=[t.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify it's soft deleted (not in list)
        t.refresh_from_db()
        self.assertTrue(t.is_deleted)

    def test_viewer_cannot_delete_transaction(self):
        t = make_transaction(self.admin)
        self.auth('viewer@t.com')
        res = self.client.delete(reverse('transaction-detail', args=[t.id]))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Validation ────────────────────────────────────────────────────────
    def test_negative_amount_rejected(self):
        self.auth('admin@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': -500, 'type': 'income',
            'category': 'salary', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_rejected(self):
        self.auth('admin@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': 0, 'type': 'income',
            'category': 'salary', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_rejected(self):
        self.auth('admin@t.com')
        res = self.client.post(reverse('transaction-list'), {
            'amount': 1000, 'type': 'invalid_type',
            'category': 'salary', 'date': '2024-03-01',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Filters ───────────────────────────────────────────────────────────
    def test_filter_by_type(self):
        make_transaction(self.admin, TransactionType.INCOME)
        make_transaction(self.admin, TransactionType.EXPENSE)
        self.auth('admin@t.com')
        res = self.client.get(reverse('transaction-list') + '?type=income')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data['results']:
            self.assertEqual(item['type'], 'income')

    def test_filter_by_category(self):
        make_transaction(self.admin, category='salary')
        make_transaction(self.admin, category='rent')
        self.auth('admin@t.com')
        res = self.client.get(reverse('transaction-list') + '?category=salary')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for item in res.data['results']:
            self.assertEqual(item['category'], 'salary')

    def test_soft_deleted_not_in_list(self):
        t = make_transaction(self.admin)
        t.is_deleted = True
        t.save()
        self.auth('admin@t.com')
        res = self.client.get(reverse('transaction-list'))
        ids = [item['id'] for item in res.data['results']]
        self.assertNotIn(t.id, ids)