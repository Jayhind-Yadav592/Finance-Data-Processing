"""
Custom management command for seeding sample data.

Usage:
    python manage.py seed           # create sample data
    python manage.py seed --clear   # clear existing + create fresh
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from users.models import User, Role
from transactions.models import Transaction, TransactionType


USERS = [
    {'email': 'admin@finance.com',   'name': 'Admin User',   'password': 'Admin@1234',   'role': Role.ADMIN},
    {'email': 'analyst@finance.com', 'name': 'Analyst User', 'password': 'Analyst@1234', 'role': Role.ANALYST},
    {'email': 'viewer@finance.com',  'name': 'Viewer User',  'password': 'Viewer@1234',  'role': Role.VIEWER},
]

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


class Command(BaseCommand):
    help = 'Seed the database with sample users and transactions for testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Transaction.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('  All non-superuser data cleared.'))

        # ── Create Users ──────────────────────────────────────────────────
        self.stdout.write('\nCreating users...')
        admin_user = None

        for u in USERS:
            user, created = User.objects.get_or_create(
                email=u['email'],
                defaults={
                    'name': u['name'],
                    'role': u['role'],
                }
            )
            if created:
                user.set_password(u['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  Created : {u["email"]}  [{u["role"]}]'))
            else:
                self.stdout.write(f'  Exists  : {u["email"]}  [{u["role"]}]')

            if u['role'] == Role.ADMIN:
                admin_user = user

        # ── Create Transactions ──────────────────────────────────────────
        self.stdout.write('\nCreating 30 sample transactions...')
        today = date.today()
        batch = []

        for _ in range(30):
            t_type   = random.choice([TransactionType.INCOME, TransactionType.EXPENSE])
            category = random.choice(
                INCOME_CATEGORIES if t_type == TransactionType.INCOME else EXPENSE_CATEGORIES
            )
            amount = Decimal(str(round(random.uniform(500, 50000), 2)))
            t_date = today - timedelta(days=random.randint(0, 120))

            batch.append(Transaction(
                user=admin_user,
                amount=amount,
                type=t_type,
                category=category,
                date=t_date,
                notes=NOTES.get(category, ''),
            ))

        Transaction.objects.bulk_create(batch)
        self.stdout.write(self.style.SUCCESS(f'  Created 30 transactions.'))

        # ── Summary ──────────────────────────────────────────────────────
        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(self.style.SUCCESS('Seed complete!'))
        self.stdout.write('\nLogin credentials:')
        for u in USERS:
            self.stdout.write(f'  {u["role"].upper():<10} {u["email"]:<30} {u["password"]}')
        self.stdout.write('\nStart server: python manage.py runserver\n')