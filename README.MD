# Finance Data Processing & Access Control Backend

## Table of Contents

1. [What is this project?](#1-what-is-this-project)
2. [How does it work?](#2-how-does-it-work)
3. [Project Structure](#3-project-structure)
4. [Tech Stack](#4-tech-stack)
5. [Setup Guide](#5-setup-guide)
6. [Seeding Sample Data](#6-seeding-sample-data)
7. [How to Use the APIs](#7-how-to-use-the-apis)
8. [All API Endpoints Explained](#8-all-api-endpoints-explained)
9. [Role & Permission System](#9-role--permission-system)
10. [Filtering & Pagination](#10-filtering--pagination)
11. [Error Responses](#11-error-responses)
12. [Running Tests](#12-running-tests)
13. [Assumptions Made](#13-assumptions-made)
14. [Optional Features Included](#14-optional-features-included)

---

## 1. What is this project?

This is a **REST API backend** built for a **Finance Dashboard System**. It allows different types of users to manage financial records — such as income and expense transactions — based on their assigned role in the system.

Think of it like the backend of a company's internal finance tool where:

- A **Viewer** (e.g. a junior employee) can only look at the financial data.
- An **Analyst** (e.g. a finance team member) can view data and also add new transactions.
- An **Admin** (e.g. a finance manager) has full control — they can create, update, delete transactions and manage other users.

The system is secured using **JWT (JSON Web Token)** authentication, which means every user must log in to get a token and use that token to access the APIs.

---

## 2. How does it work?

The backend follows a simple flow:

```
Client (Postman / Frontend)
        |
        | sends HTTP request with JWT token
        v
  Django REST Framework
        |
        | checks: is the user logged in?      → 401 if not
        | checks: does the user have role?    → 403 if not
        v
    View / Business Logic
        |
        | reads or writes data
        v
    MySQL Database
        |
        | returns result
        v
  JSON Response back to client
```

Every request (except register and login) must include a **Bearer Token** in the header. The server validates the token, checks the user's role, and either allows or blocks the action.

---

## 3. Project Structure

```
finance_backend/                             ← Root folder
│
├── manage.py                                ← Django management script
├── requirements.txt                         ← All Python libraries needed
├── Finance_Backend.postman_collection.json  ← Import this in Postman
├── .gitignore                               ← Files ignored by Git
│
├── finance_backend/                         ← Main Django project config
│   ├── settings.py                          ← Database, JWT, installed apps
│   ├── urls.py                              ← Root URL router
│   ├── exceptions.py                        ← Custom error response format
│   ├── wsgi.py                              ← For deployment
│   └── asgi.py                              ← For async deployment
│
├── users/                                   ← App 1: Users, roles, auth
│   ├── models.py                            ← User model with role field
│   ├── serializers.py                       ← JSON conversion + validation
│   ├── views.py                             ← Register, login, manage users
│   ├── urls.py                              ← URL paths for user endpoints
│   ├── permissions.py                       ← IsAdmin, IsAnalystOrAdmin classes
│   ├── admin.py                             ← Django admin config
│   ├── tests.py                             ← Unit tests for auth & roles
│   └── management/commands/seed.py          ← "python manage.py seed" command
│
├── transactions/                            ← App 2: Financial records
│   ├── models.py                            ← Transaction model
│   ├── serializers.py                       ← Validation + JSON conversion
│   ├── views.py                             ← CRUD logic with role checks
│   ├── urls.py                              ← URL paths for transactions
│   ├── filters.py                           ← Filter by date, type, category
│   └── tests.py                             ← Unit tests for transactions
│
└── dashboard/                               ← App 3: Analytics & summaries
    ├── views.py                             ← Summary, trends, category logic
    ├── urls.py                              ← URL paths for dashboard
    └── tests.py                             ← Unit tests for dashboard
```

---

## 4. Tech Stack

| Layer          | Technology                           | Why used                                    |
|----------------|--------------------------------------|---------------------------------------------|
| Language       | Python 3.10+                         | Clean, readable, widely used for backends   |
| Framework      | Django 4.2                           | Fast development with built-in ORM & admin  |
| REST API       | Django REST Framework                | Makes building APIs clean and structured    |
| Authentication | djangorestframework-simplejwt        | Stateless, secure token-based auth          |
| Database       | MySQL                                | Reliable relational database                |
| Filtering      | django-filter                        | Query param based filtering support         |
| CORS           | django-cors-headers                  | Allows frontend apps to connect             |

---

## 5. Setup Guide

Follow these steps **in order** to get the project running on your machine.

### Prerequisites

Make sure the following are installed on your PC:

- Python 3.10 or above — check: `python --version`
- MySQL Server — check: `mysql --version`
- pip — check: `pip --version`

---

### Step 1 — Get the project

```bash
# If cloning from GitHub:
git clone https://github.com/your-username/finance_backend.git
cd finance_backend

# If you have the zip file, extract it and open that folder in terminal.
```

---

### Step 2 — Create and activate a virtual environment

A virtual environment keeps this project's libraries separate from other Python projects on your system.

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

After activation, your terminal prompt will show `(venv)` — this means the environment is active.

---

### Step 3 — Install all required libraries

```bash
pip install -r requirements.txt
```

This installs: Django, Django REST Framework, SimpleJWT, django-filter, mysqlclient, and django-cors-headers.

---

### Step 4 — Create the MySQL database

Open MySQL Workbench or your MySQL terminal and run:

```sql
CREATE DATABASE finance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 5 — Set your database credentials

Open `finance_backend/settings.py` and update this section with your MySQL username and password:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'finance_db',        # database name you just created
        'USER': 'root',              # your MySQL username
        'PASSWORD': 'yourpassword',  # your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

### Step 6 — Run migrations (create database tables)

```bash
python manage.py makemigrations users
python manage.py makemigrations transactions
python manage.py migrate
```

Expected output:
```
Applying users.0001_initial... OK
Applying transactions.0001_initial... OK
```

This creates all the necessary tables inside your `finance_db` MySQL database.

---

### Step 7 — Start the server

```bash
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL+C.
```

Your backend is now live. Keep this terminal open while testing.

---

## 6. Seeding Sample Data

Instead of creating users and transactions manually, run the seed command to instantly populate the database with test data.

```bash
python manage.py seed
```

Output:
```
Creating users...
  Created : admin@finance.com    [admin]
  Created : analyst@finance.com  [analyst]
  Created : viewer@finance.com   [viewer]

Creating 30 sample transactions...
  Created 30 transactions.

Login credentials:
  ADMIN      admin@finance.com       Admin@1234
  ANALYST    analyst@finance.com     Analyst@1234
  VIEWER     viewer@finance.com      Viewer@1234
```

To clear all data and start completely fresh:

```bash
python manage.py seed --clear
```

---

## 7. How to Use the APIs

### Option A — Using Postman (Recommended)

1. Download and open [Postman](https://www.postman.com/downloads/)
2. Click **Import** → select `Finance_Backend.postman_collection.json`
3. All 20+ requests will appear in the left sidebar
4. First run the **Login** request to get your token — Postman automatically saves it

### Option B — Using curl in terminal

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@finance.com", "password": "Admin@1234"}'

# Use token in subsequent requests
curl http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Getting and using the JWT Token

Every protected API requires a token. Here is the exact flow:

**Step 1 — Login and get token:**

```
POST http://127.0.0.1:8000/api/auth/login/

Body:
{
  "email": "admin@finance.com",
  "password": "Admin@1234"
}
```

**Step 2 — Copy the access token from response:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Step 3 — Add the token to every request header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

In Postman: open any request → click **Authorization** tab → select **Bearer Token** → paste your token.

> The access token expires in **1 hour**. After that, use the refresh token endpoint to get a new one.

---

## 8. All API Endpoints Explained

---

### AUTH ENDPOINTS

---

#### `POST /api/auth/register/`

Creates a new user account.

**Access:** Public — no token required

**Request body:**
```json
{
  "email": "john@example.com",
  "name": "John Doe",
  "password": "John@1234",
  "role": "viewer"
}
```

Role options: `viewer`, `analyst`, `admin`. Defaults to `viewer` if not provided.

**Success (201):**
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 4,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "viewer",
    "is_active": true,
    "created_at": "2024-03-15T10:00:00Z"
  }
}
```

**Failure — duplicate email (400):**
```json
{
  "error": "Invalid input. Please check the fields below.",
  "details": {
    "email": ["user with this email already exists."]
  }
}
```

---

#### `POST /api/auth/login/`

Logs in a user and returns JWT tokens.

**Access:** Public — no token required

**Request body:**
```json
{
  "email": "admin@finance.com",
  "password": "Admin@1234"
}
```

**Success (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Wrong password (401):**
```json
{
  "error": "Authentication required. Please login to continue."
}
```

---

#### `POST /api/auth/token/refresh/`

Gets a new access token when the current one expires, without logging in again.

**Request body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success (200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

#### `GET /api/auth/me/`

Returns the profile of the currently logged-in user.

**Access:** Any authenticated user

**Success (200):**
```json
{
  "id": 1,
  "email": "admin@finance.com",
  "name": "Admin User",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-03-01T09:00:00Z"
}
```

---

### USER MANAGEMENT ENDPOINTS

---

#### `GET /api/auth/users/`

Returns a paginated list of all users in the system.

**Access:** Admin only

**Success (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "email": "admin@finance.com",   "name": "Admin User",   "role": "admin",   "is_active": true },
    { "id": 2, "email": "analyst@finance.com", "name": "Analyst User", "role": "analyst", "is_active": true },
    { "id": 3, "email": "viewer@finance.com",  "name": "Viewer User",  "role": "viewer",  "is_active": true }
  ]
}
```

**Viewer or Analyst tries this (403):**
```json
{
  "error": "Only admin users can perform this action."
}
```

---

#### `PATCH /api/auth/users/<id>/role/`

Changes the role of any user. Example: promote a viewer to analyst.

**Access:** Admin only

**Example URL:** `PATCH /api/auth/users/3/role/`

**Request body:**
```json
{ "role": "analyst" }
```

**Success (200):**
```json
{
  "message": "Role updated.",
  "user": { "id": 3, "email": "viewer@finance.com", "role": "analyst" }
}
```

**User not found (404):**
```json
{ "error": "The requested resource was not found." }
```

---

#### `PATCH /api/auth/users/<id>/status/`

Activates or deactivates a user. A deactivated user is immediately blocked from all API access even if they have a valid token.

**Access:** Admin only

**Example URL:** `PATCH /api/auth/users/3/status/`

**Deactivate:**
```json
{ "is_active": false }
```

**Reactivate:**
```json
{ "is_active": true }
```

**Success (200):**
```json
{ "message": "User deactivated successfully." }
```

---

### TRANSACTION ENDPOINTS

---

#### `GET /api/transactions/`

Returns a paginated list of all financial transactions (10 per page).

**Access:** All roles

**Success (200):**
```json
{
  "count": 30,
  "next": "http://127.0.0.1:8000/api/transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "admin@finance.com",
      "amount": "50000.00",
      "type": "income",
      "category": "salary",
      "date": "2024-03-01",
      "notes": "March salary credited",
      "created_at": "2024-03-15T10:00:00Z",
      "updated_at": "2024-03-15T10:00:00Z"
    }
  ]
}
```

---

#### `POST /api/transactions/`

Creates a new financial transaction record.

**Access:** Analyst and Admin only

**Request body:**
```json
{
  "amount": 50000.00,
  "type": "income",
  "category": "salary",
  "date": "2024-03-01",
  "notes": "March salary credited"
}
```

Field rules:
- `amount` — required, must be greater than 0
- `type` — required, must be `income` or `expense`
- `category` — required, cannot be blank
- `date` — required, format `YYYY-MM-DD`
- `notes` — optional

**Success (201):**
```json
{
  "id": 31,
  "user": 1,
  "user_email": "admin@finance.com",
  "amount": "50000.00",
  "type": "income",
  "category": "salary",
  "date": "2024-03-01",
  "notes": "March salary credited",
  "created_at": "2024-03-15T11:00:00Z",
  "updated_at": "2024-03-15T11:00:00Z"
}
```

**Negative amount (400):**
```json
{
  "error": "Invalid input. Please check the fields below.",
  "details": { "amount": ["Amount must be greater than 0."] }
}
```

**Viewer tries to create (403):**
```json
{ "error": "Only analyst or admin users can perform this action." }
```

---

#### `GET /api/transactions/<id>/`

Returns one transaction by its ID.

**Access:** All roles

**Success (200):**
```json
{
  "id": 5,
  "user": 1,
  "user_email": "admin@finance.com",
  "amount": "3000.00",
  "type": "expense",
  "category": "rent",
  "date": "2024-03-05",
  "notes": "House rent payment",
  "created_at": "2024-03-15T10:10:00Z",
  "updated_at": "2024-03-15T10:10:00Z"
}
```

**Not found (404):**
```json
{ "error": "The requested resource was not found." }
```

---

#### `PUT /api/transactions/<id>/`

Fully updates an existing transaction. All fields must be included.

**Access:** Admin only

**Request body:**
```json
{
  "amount": 3500.00,
  "type": "expense",
  "category": "rent",
  "date": "2024-03-05",
  "notes": "Updated rent amount"
}
```

**Success (200):** Returns the updated transaction object.

---

#### `PATCH /api/transactions/<id>/`

Partially updates a transaction. Only send the fields you want to change.

**Access:** Admin only

**Example — update only notes:**
```json
{ "notes": "Corrected note" }
```

---

#### `DELETE /api/transactions/<id>/`

Soft deletes a transaction. The record stays in the database but is hidden from all API responses. This preserves financial audit history.

**Access:** Admin only

**Success (200):**
```json
{ "message": "Transaction deleted successfully." }
```

After deletion, `GET /api/transactions/<id>/` returns 404 for that record.

---

### DASHBOARD ENDPOINTS

---

#### `GET /api/dashboard/summary/`

Returns total income, total expense, and net balance across all transactions.

**Access:** All roles

**Success (200):**
```json
{
  "total_income": "125000.00",
  "total_expense": "87000.00",
  "net_balance": "38000.00"
}
```

`net_balance = total_income - total_expense`

---

#### `GET /api/dashboard/category-wise/`

Returns totals broken down by category and type. Shows where money is coming from and going.

**Access:** Analyst and Admin only

**Success (200):**
```json
[
  { "category": "bonus",         "type": "income",  "total": "15000.00", "count": 2 },
  { "category": "entertainment", "type": "expense", "total": "4500.00",  "count": 3 },
  { "category": "food",          "type": "expense", "total": "8200.00",  "count": 5 },
  { "category": "salary",        "type": "income",  "total": "100000.00","count": 2 }
]
```

---

#### `GET /api/dashboard/trends/`

Returns monthly totals for income and expense. Useful for trend analysis over time.

**Access:** Analyst and Admin only

**Success (200):**
```json
[
  { "month": "2024-01", "income": 50000, "expense": 30000 },
  { "month": "2024-02", "income": 75000, "expense": 45000 },
  { "month": "2024-03", "income": 60000, "expense": 40000 }
]
```

---

#### `GET /api/dashboard/trends/weekly/`

Same as monthly trends but broken down by week start date.

**Access:** Analyst and Admin only

**Success (200):**
```json
[
  { "week_start": "2024-03-04", "income": 20000, "expense": 12000 },
  { "week_start": "2024-03-11", "income": 15000, "expense": 9000 }
]
```

---

#### `GET /api/dashboard/recent/`

Returns the 10 most recent transactions sorted by date.

**Access:** All roles

**Success (200):**
```json
[
  {
    "id": 30,
    "user_email": "admin@finance.com",
    "amount": "12000.00",
    "type": "income",
    "category": "freelance",
    "date": "2024-03-14",
    "notes": "Freelance project payment"
  }
]
```

---

## 9. Role & Permission System

| Action                       | Viewer | Analyst | Admin |
|------------------------------|--------|---------|-------|
| Register / Login             | ✅     | ✅      | ✅    |
| View own profile             | ✅     | ✅      | ✅    |
| List transactions            | ✅     | ✅      | ✅    |
| View single transaction      | ✅     | ✅      | ✅    |
| View dashboard summary       | ✅     | ✅      | ✅    |
| View recent activity         | ✅     | ✅      | ✅    |
| Create transaction           | ❌     | ✅      | ✅    |
| View category-wise analytics | ❌     | ✅      | ✅    |
| View monthly/weekly trends   | ❌     | ✅      | ✅    |
| Update transaction           | ❌     | ❌      | ✅    |
| Delete transaction           | ❌     | ❌      | ✅    |
| List all users               | ❌     | ❌      | ✅    |
| Change user role             | ❌     | ❌      | ✅    |
| Activate / Deactivate user   | ❌     | ❌      | ✅    |

These rules are enforced by three custom permission classes in `users/permissions.py`:

- `IsAdmin` — allows only users with role `admin`
- `IsAnalystOrAdmin` — allows users with role `analyst` or `admin`
- `IsActiveUser` — blocks any user whose account has been deactivated

---

## 10. Filtering & Pagination

### Filter Transactions by Query Parameters

```
GET /api/transactions/?type=income
GET /api/transactions/?type=expense
GET /api/transactions/?category=salary
GET /api/transactions/?date_from=2024-01-01&date_to=2024-03-31
GET /api/transactions/?amount_min=1000&amount_max=50000
GET /api/transactions/?type=income&category=salary&date_from=2024-01-01
```

### Ordering

```
GET /api/transactions/?ordering=-date      ← newest first
GET /api/transactions/?ordering=date       ← oldest first
GET /api/transactions/?ordering=-amount    ← highest amount first
GET /api/transactions/?ordering=amount     ← lowest amount first
```

### Pagination

All list endpoints return 10 records per page.

```
GET /api/transactions/?page=1
GET /api/transactions/?page=2
```

Response format:
```json
{
  "count": 30,
  "next": "http://127.0.0.1:8000/api/transactions/?page=2",
  "previous": null,
  "results": [ ... 10 items ... ]
}
```

---

## 11. Error Responses

All errors follow a consistent JSON format:

### 400 — Validation error
```json
{
  "error": "Invalid input. Please check the fields below.",
  "details": {
    "amount": ["Amount must be greater than 0."],
    "type": ["This field is required."]
  }
}
```

### 401 — No token or invalid token
```json
{ "error": "Authentication required. Please login to continue." }
```

### 403 — Logged in but wrong role
```json
{ "error": "Only admin users can perform this action." }
```

### 404 — Record not found
```json
{ "error": "The requested resource was not found." }
```

---

## 12. Running Tests

The project includes 25+ unit tests covering authentication, permissions, CRUD, validation, filtering, and analytics.

### Run all tests

```bash
python manage.py test
```

### Run tests for a specific app

```bash
python manage.py test users
python manage.py test transactions
python manage.py test dashboard
```

### Expected output

```
Creating test database for alias 'default'...
.........................
----------------------------------------------------------------------
Ran 25 tests in 4.312s

OK
Destroying test database for alias 'default'...
```

Each `.` is one passing test. `F` means a failure with explanation. `E` means an error.

### What is tested

**users/tests.py** — register success, duplicate email, missing fields, login success, wrong password, inactive user, admin list users, viewer blocked from user list, unauthenticated blocked.

**transactions/tests.py** — viewer list allowed, analyst create allowed, admin create allowed, viewer create blocked, admin update allowed, analyst update blocked, admin soft delete, viewer delete blocked, negative amount rejected, zero amount rejected, invalid type rejected, filter by type works, filter by category works, soft deleted records hidden.

**dashboard/tests.py** — summary returns correct math, viewer can access summary, summary blocks unauthenticated, analyst accesses category-wise, viewer blocked from category-wise, analyst accesses trends, viewer blocked from trends, recent returns max 10, soft deleted excluded from summary totals.

---

## 13. Assumptions Made

1. **Soft delete** — Transactions are never permanently removed. The `is_deleted` flag hides them from all API responses while keeping the record in the database for audit purposes.

2. **Shared data** — All authenticated users can see all transactions. This models a shared company finance system where data belongs to the organization, not individual users.

3. **Role on register** — The register endpoint accepts a `role` field so admins can create accounts with specific roles. If no role is given, it defaults to `viewer`.

4. **Token expiry** — Access token expires in 1 hour. Refresh token expires in 7 days.

5. **Pagination** — List endpoints return 10 records per page to keep responses fast and manageable.

6. **Category normalization** — Category values are automatically lowercased so that `Salary` and `salary` are treated as the same category during filtering.

7. **Inactive user blocking** — If an admin deactivates a user account, that user loses all API access immediately even if their token is still valid.

---

## 14. Optional Features Included

| Feature                 | How it was implemented                                            |
|-------------------------|-------------------------------------------------------------------|
| JWT Authentication      | Access token (1hr) + Refresh token (7 days) via SimpleJWT        |
| Pagination              | 10 records per page on all list endpoints                        |
| Soft Delete             | `is_deleted` field on Transaction — admin only, preserves history|
| Advanced Filtering      | By type, category, date range, amount range via query params     |
| Ordering support        | `?ordering=-date`, `?ordering=amount`, etc.                      |
| Unit Tests              | 25+ tests across all three apps                                  |
| API Documentation       | This README + Postman collection with all requests pre-configured|
| Custom Error Handler    | Consistent JSON error format across all endpoints                |
| Management Seed Command | `python manage.py seed` and `python manage.py seed --clear`      |
| Django Admin Panel      | All models registered, accessible at `/admin/`                   |

---

## Default Test Accounts (after running seed)

| Role    | Email                  | Password     |
|---------|------------------------|--------------|
| Admin   | admin@finance.com      | Admin@1234   |
| Analyst | analyst@finance.com    | Analyst@1234 |
| Viewer  | viewer@finance.com     | Viewer@1234  |

Use the Login API with any of these to get a token and start testing all endpoints.