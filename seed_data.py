"""
Sample data seed script.

Usage:
    python manage.py shell < seed_data.py

Ye script 3 users (admin, analyst, viewer) aur 20 sample
transactions create karega testing ke liye.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_backend.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
import random
from decimal import Decimal

from users.models import User, Role
from transactions.models import Transaction, TransactionType

print("Seeding database...")

# ── 1. Users ──────────────────────────────────────────────────────────────────
users_data = [
    {'email': 'admin@finance.com',   'name': 'Admin User',   'password': 'Admin@1234',   'role': Role.ADMIN},
    {'email': 'analyst@finance.com', 'name': 'Analyst User', 'password': 'Analyst@1234', 'role': Role.ANALYST},
    {'email': 'viewer@finance.com',  'name': 'Viewer User',  'password': 'Viewer@1234',  'role': Role.VIEWER},
]

created_users = []
for u in users_data:
    if not User.objects.filter(email=u['email']).exists():
        user = User.objects.create_user(
            email=u['email'],
            name=u['name'],
            password=u['password'],
            role=u['role'],
        )
        created_users.append(user)
        print(f"  Created user: {u['email']}  role={u['role']}")
    else:
        existing = User.objects.get(email=u['email'])
        created_users.append(existing)
        print(f"  User already exists: {u['email']}")

admin_user = User.objects.get(email='admin@finance.com')

# ── 2. Transactions ────────────────────────────────────────────────────────────
INCOME_CATEGORIES  = ['salary', 'freelance', 'investment', 'bonus', 'rental']
EXPENSE_CATEGORIES = ['rent', 'food', 'transport', 'utilities', 'entertainment', 'medical']

NOTES = {
    'salary':        'Monthly salary credited',
    'freelance':     'Freelance project payment',
    'investment':    'Dividend / returns received',
    'bonus':         'Performance bonus',
    'rental':        'Rental income from property',
    'rent':          'House rent payment',
    'food':          'Groceries and dining',
    'transport':     'Fuel and commute',
    'utilities':     'Electricity and internet bill',
    'entertainment': 'Movies and subscriptions',
    'medical':       'Doctor consultation / medicine',
}

today = date.today()
Transaction.objects.filter(is_deleted=False).delete()  # clear old test data

transactions = []
for i in range(20):
    t_type = random.choice([TransactionType.INCOME, TransactionType.EXPENSE])
    category = random.choice(
        INCOME_CATEGORIES if t_type == TransactionType.INCOME else EXPENSE_CATEGORIES
    )
    amount = Decimal(str(round(random.uniform(500, 50000), 2)))
    t_date = today - timedelta(days=random.randint(0, 90))

    transactions.append(Transaction(
        user=admin_user,
        amount=amount,
        type=t_type,
        category=category,
        date=t_date,
        notes=NOTES.get(category, ''),
    ))

Transaction.objects.bulk_create(transactions)
print(f"  Created {len(transactions)} sample transactions")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n✅ Seed complete!")
print("\n--- Login credentials ---")
for u in users_data:
    print(f"  {u['role'].upper():<10} email: {u['email']:<30} password: {u['password']}")
print("\nRun: python manage.py runserver")