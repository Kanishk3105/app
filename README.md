# Healthcare Backend API

A secure healthcare backend built with **Django**, **Django REST Framework** and **PostgreSQL**, using **JWT authentication**. It manages users, patients, doctors and patient-doctor mappings through a clean REST API.

---

## 1. Project Overview

The API supports three core domains:

| Domain | Purpose |
|---|---|
| **Authentication** | Register, login and JWT-protected access |
| **Patients** | Private patient records, strictly owned by the creator |
| **Doctors** | Shared doctor directory visible to every authenticated user |
| **Mappings** | Assign doctors to patients, query assignments, remove them |

Security is a first-class concern: passwords are hashed with PBKDF2, all `/api/*` routes require a Bearer JWT, patient records are ownership-scoped (403/404 for foreign records), and every secret is read from environment variables.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Framework | Django 5.2 |
| API | Django REST Framework 3.18 |
| Auth | djangorestframework-simplejwt (JWT / Bearer tokens) |
| Database | PostgreSQL 18 (Django ORM only - no SQLite) |
| DB driver | psycopg2-binary |
| Config | python-dotenv (`.env`) |
| Tests | Django test runner + DRF `APITestCase` |

---

## 3. Setup Instructions

### 3.1 Prerequisites

* Python 3.10+
* PostgreSQL 11+ running locally (or a remote instance)

### 3.2 Clone & virtual environment

```bash
git clone <repo-url> healthcare_backend
cd healthcare_backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3.3 Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
Django==5.2.17
djangorestframework==3.18.1
djangorestframework-simplejwt==5.5.1
psycopg2-binary==2.9.10
python-dotenv==1.1.1
django-cors-headers==4.9.0
```

---

## 4. PostgreSQL Setup

```bash
# 1. Connect to your PostgreSQL server
psql -U postgres

# 2. Create a dedicated database
CREATE DATABASE healthcare_db;

# 3. (Recommended) create a least-privilege role
CREATE ROLE healthcare_user WITH LOGIN PASSWORD 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
\q
```

> The database is created automatically only if your `.env` user has the right
> to create databases; otherwise create it manually as shown above.

---

## 5. Environment Variables

Copy the template and fill in real values. **Never commit `.env`.**

```bash
cp .env.example .env
```

`.env.example`:

```ini
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=healthcare_db
DATABASE_USER=postgres
DATABASE_PASSWORD=change-me
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=7

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production-only (read only when DEBUG=False)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
```

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django/JWT signing key - startup fails without it |
| `DEBUG` | ✅ | `True` in development, `False` in production |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hostnames |
| `DATABASE_NAME` | ✅ | PostgreSQL database name |
| `DATABASE_USER` | ✅ | PostgreSQL role |
| `DATABASE_PASSWORD` | ✅ | PostgreSQL password (never committed) |
| `DATABASE_HOST` | ✅ | Host, default `127.0.0.1` |
| `DATABASE_PORT` | ✅ | Port, default `5432` |
| `ACCESS_TOKEN_LIFETIME` | optional | JWT access token lifetime (minutes) |
| `REFRESH_TOKEN_LIFETIME` | optional | JWT refresh token lifetime (days) |
| `CORS_ALLOWED_ORIGINS` | optional | Allowed front-end origins |

`.gitignore` excludes `.env` so no credential can be committed.

---

## 6. Migrations, Server, Tests

```bash
# Create migrations (already generated in this repo)
python manage.py makemigrations

# Apply migrations to PostgreSQL
python manage.py migrate

# (Optional) create an admin user for /admin/
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# Run the full test suite
python manage.py test

# Run tests for a single app
python manage.py test apps.accounts
python manage.py test apps.patients
python manage.py test apps.doctors
python manage.py test apps.mappings

# Django system checks
python manage.py check
python manage.py check --deploy   # run with DEBUG=False for production advice
```

**Test results: 69 tests, all passing** (registration, login, JWT, permissions, ownership, CRUD, mappings, validation and error cases).

---

## 7. API Endpoints

Base URL: `http://127.0.0.1:8000`

### 7.0 Root

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Public | JSON index listing every endpoint, auth method and description |

### 7.1 Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Create a new user |
| POST | `/api/auth/login/` | Public | Get JWT `access` + `refresh` tokens |
| POST | `/api/auth/token/refresh/` | Public | Rotate the access token |
| POST | `/api/auth/logout/` | Bearer | Confirm logout (client discards tokens) |
| GET | `/api/auth/me/` | Bearer | Current user profile |

### 7.2 Patients (owner-scoped)

| Method | Endpoint | Auth | Success |
|---|---|---|---|
| POST | `/api/patients/` | Bearer | `201` |
| GET | `/api/patients/` | Bearer | `200` |
| GET | `/api/patients/<id>/` | Bearer | `200` |
| PUT | `/api/patients/<id>/` | Bearer | `200` |
| PATCH | `/api/patients/<id>/` | Bearer | `200` |
| DELETE | `/api/patients/<id>/` | Bearer | `204` |

### 7.3 Doctors (shared directory)

| Method | Endpoint | Auth | Success |
|---|---|---|---|
| POST | `/api/doctors/` | Bearer | `201` |
| GET | `/api/doctors/` | Bearer | `200` |
| GET | `/api/doctors/<id>/` | Bearer | `200` |
| PUT | `/api/doctors/<id>/` | Bearer | `200` |
| PATCH | `/api/doctors/<id>/` | Bearer | `200` |
| DELETE | `/api/doctors/<id>/` | Bearer | `204` |

### 7.4 Patient-Doctor Mappings

| Method | Endpoint | Auth | Success | Description |
|---|---|---|---|---|
| POST | `/api/mappings/` | Bearer | `201` | Assign a doctor to a patient |
| GET | `/api/mappings/` | Bearer | `200` | List *your* mappings |
| GET | `/api/mappings/<patient_id>/` | Bearer | `200` | All doctors assigned to that patient |
| DELETE | `/api/mappings/<id>/` | Bearer | `204` | Remove a mapping |

> **Assumption (documented):** the assignment uses the same path shape for
> `GET /api/mappings/<patient_id>/` and `DELETE /api/mappings/<id>/`.
> The path parameter is interpreted by HTTP method:
> * `GET` → the parameter is a **patient id** (returns that patient's doctors)
> * `DELETE` → the parameter is a **mapping id** (deletes that mapping)
>
> `GET /api/mappings/` always returns the mapping `id`s, so clients can always
> discover which id to `DELETE`.

### 7.5 Status codes

| Code | When |
|---|---|
| `200` | Successful read/update |
| `201` | Resource created |
| `204` | Deleted successfully |
| `400` | Validation error (missing/invalid/duplicate fields) |
| `401` | Missing, invalid or expired JWT |
| `403` | Authenticated but not allowed (someone else's patient/mapping) |
| `404` | Resource does not exist |
| `405` | Method not allowed on the resource |

---

## 8. Authentication & JWT Usage

### Register

```http
POST /api/auth/register/
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "SecurePass123!"
}
```

**Response `201`**

```json
{
  "message": "User registered successfully.",
  "user": { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "created_at": "2026-09-28T01:00:00Z" }
}
```

**Error `400` (duplicate email / weak password / missing fields)**

```json
{ "email": ["A user with this email already exists."] }
```

### Login

```http
POST /api/auth/login/
Content-Type: application/json

{ "email": "jane@example.com", "password": "SecurePass123!" }
```

**Response `200`**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "created_at": "..." },
  "message": "Login successful."
}
```

**Error `401`**

```json
{ "detail": "No active account found with the given credentials" }
```

### Using the token

Send the access token on every protected request:

```http
GET /api/patients/
Authorization: Bearer <access_token>
```

Refresh when the access token expires:

```http
POST /api/auth/token/refresh/
Content-Type: application/json

{ "refresh": "<refresh_token>" }
```

**Response `200`** → `{ "message": "Token refreshed.", "access": "..." }`

Missing/invalid token → `401 { "detail": "Given token not valid for any token type" }`.

---

## 9. Example Requests & Responses

### Create a patient

```http
POST /api/patients/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "John Doe",
  "age": 34,
  "gender": "male",
  "phone": "+1-555-0100",
  "address": "12 Main St, Springfield",
  "blood_group": "O+",
  "allergies": "Penicillin",
  "medical_history": "Hypertension"
}
```

**Response `201`**

```json
{
  "id": 1,
  "name": "John Doe",
  "date_of_birth": null,
  "age": 34,
  "gender": "male",
  "phone": "+1-555-0100",
  "email": "",
  "address": "12 Main St, Springfield",
  "blood_group": "O+",
  "allergies": "Penicillin",
  "medical_history": "Hypertension",
  "created_by": "jane@example.com",
  "created_at": "2026-09-28T01:05:00Z",
  "updated_at": "2026-09-28T01:05:00Z"
}
```

### List patients

```http
GET /api/patients/
Authorization: Bearer <access_token>
```

**Response `200`** - only records created by the requesting user:

```json
[ { "id": 1, "name": "John Doe", "age": 34, "created_by": "jane@example.com", "...": "..." } ]
```

### Access another user's patient

```http
GET /api/patients/<someone-elses-patient-id>/
```

**Response `403`**

```json
{ "detail": "You do not have permission to access this patient record." }
```

### Create a doctor

```http
POST /api/doctors/
Authorization: Bearer <access_token>

{ "name": "Priya Sharma", "specialization": "Cardiology", "email": "priya@clinic.com", "phone": "+1-555-0199", "qualification": "MD" }
```

**Response `201`** - returns the doctor with `created_by` audit info.

### Assign a doctor to a patient

```http
POST /api/mappings/
Authorization: Bearer <access_token>

{ "patient": 1, "doctor": 1, "notes": "Quarterly review" }
```

**Response `201`**

```json
{
  "id": 1,
  "patient": 1,
  "patient_name": "John Doe",
  "doctor": 1,
  "doctor_name": "Priya Sharma",
  "doctor_specialization": "Cardiology",
  "notes": "Quarterly review",
  "assigned_by": "jane@example.com",
  "created_at": "2026-09-28T01:10:00Z"
}
```

**Errors**

```json
{ "doctor": ["This doctor is already assigned to this patient."] }   // 400 duplicate
{ "patient": ["Invalid pk \"999999\" - object does not exist."] }     // 400 unknown patient
{ "patient": ["You do not have access to this patient."] }            // 400 foreign patient
```

### Doctors assigned to a patient

```http
GET /api/mappings/1/
Authorization: Bearer <access_token>
```

**Response `200`**

```json
[
  {
    "mapping_id": 1,
    "id": 1,
    "name": "Priya Sharma",
    "specialization": "Cardiology",
    "qualification": "MD",
    "email": "priya@clinic.com",
    "phone": "+1-555-0199",
    "clinic_address": "",
    "years_of_experience": null,
    "is_available": true,
    "created_by": "jane@example.com",
    "created_at": "2026-09-28T01:02:00Z",
    "updated_at": "2026-09-28T01:02:00Z"
  }
]
```

### Remove a mapping

```http
DELETE /api/mappings/1/
Authorization: Bearer <access_token>
```

**Response `204`** - empty body.

### Error examples

```json
GET /api/patients/999999/     -> 404 { "detail": "Patient not found." }
GET /api/patients/abc/        -> 404 { "detail": "Not found." }
GET /api/unknown-route/       -> 404 { "detail": "Not found." }
GET /api/patients/  (no JWT)  -> 401 { "detail": "Given token not valid for any token type" }
```

Every error is JSON - Django never returns an HTML error page for `/api/*` routes.

---

## 10. Project Structure

```
healthcare_backend/
├── manage.py
├── requirements.txt
├── .env.example              # documented environment template
├── .env                      # real secrets (git-ignored)
├── .gitignore
├── postman_collection.json   # ready-to-import Postman collection
├── README.md
├── config/                   # project-level configuration
│   ├── settings.py           # env-driven settings (DB, JWT, DRF, security)
│   ├── urls.py               # root URL routing + JSON 404 fallback
│   ├── views.py              # GET / - JSON index of every endpoint
│   ├── exceptions.py         # custom DRF exception handler (JSON errors)
│   ├── errors.py             # JSON fallbacks for unmatched API routes
│   ├── wsgi.py
│   └── asgi.py
└── apps/                     # domain modules
    ├── accounts/             # custom user + auth endpoints
    │   ├── models.py         # User (email login, hashed password)
    │   ├── serializers.py    # Register/Login serializers
    │   ├── views.py          # register, login, me, refresh, logout
    │   ├── urls.py
    │   ├── admin.py
    │   └── tests.py          # 20 auth tests
    ├── patients/
    │   ├── models.py         # Patient (owned by creator)
    │   ├── serializers.py
    │   ├── views.py          # ownership-scoped ModelViewSet
    │   ├── urls.py           # router -> /api/patients/
    │   ├── admin.py
    │   └── tests.py          # 22 patient tests
    ├── doctors/
    │   ├── models.py         # Doctor (shared directory)
    │   ├── serializers.py
    │   ├── views.py          # ModelViewSet -> /api/doctors/
    │   ├── urls.py
    │   ├── admin.py
    │   └── tests.py          # 15 doctor tests
    └── mappings/
        ├── models.py         # PatientDoctorMapping + constraints
        ├── serializers.py
        ├── views.py          # list/create + get-doctors/delete-mapping
        ├── urls.py           # /api/mappings/ and /api/mappings/<pk>/
        ├── admin.py
        └── tests.py          # 18 mapping tests
```

Responsibilities are strictly separated: **models → serializers → permissions/views → URLs → tests**, which makes the codebase easy for a reviewer to navigate.

---

## 11. Database / Model Explanation

### `accounts.User` (custom user model)

| Field | Type | Notes |
|---|---|---|
| `id` | BigAuto PK | auto |
| `name` | Char(150) | full name |
| `email` | Email, unique, indexed | **login identifier** (`USERNAME_FIELD`) |
| `password` | Char | PBKDF2 hash - never returned by the API |
| `is_active`, `is_staff` | Boolean | standard Django flags |
| `created_at`, `updated_at` | DateTime | audit timestamps |

`UserManager.create_user()` normalises the email and calls `set_password()` so the
password is **never stored in clear text**.

### `patients.Patient`

| Field | Type | Notes |
|---|---|---|
| `name` | Char(150) | required |
| `date_of_birth` | Date, nullable | optional |
| `age` | PositiveInt, nullable | check constraint `age >= 0` |
| `gender` | Choice | male / female / other / prefer_not_to_say |
| `phone`, `email`, `address`, `blood_group` | text | optional contact info |
| `allergies`, `medical_history` | text | clinical notes |
| `created_by` | **FK → User** (`CASCADE`) | ownership - drives all row filtering |
| `created_at`, `updated_at` | DateTime | `auto_now_add` / `auto_now` |

Indexes: `(created_by, -created_at)` for fast per-user listings, `(name)` for search.

### `doctors.Doctor`

| Field | Type | Notes |
|---|---|---|
| `name` | Char(150) | required |
| `specialization` | Char(120) | required, indexed |
| `qualification`, `phone`, `clinic_address` | text | optional |
| `email` | Email | unique **when provided** (partial unique constraint) |
| `years_of_experience` | PositiveInt, nullable | |
| `is_available` | Boolean | default `True` |
| `created_by` | **FK → User** | audit trail (who registered the doctor) |
| `created_at`, `updated_at` | DateTime | |

### `mappings.PatientDoctorMapping`

| Field | Type | Notes |
|---|---|---|
| `patient` | **FK → Patient** (`CASCADE`) | deleting a patient removes its mappings |
| `doctor` | **FK → Doctor** (`CASCADE`) | deleting a doctor removes its mappings |
| `assigned_by` | **FK → User** | who created the assignment |
| `notes` | text | optional |
| `created_at`, `updated_at` | DateTime | |

Constraints:

* `UniqueConstraint(patient, doctor)` - **no duplicate assignments**
* Index on `(patient, doctor)` - fast "doctors for this patient" lookups
* `clean()` verifies the assigning user actually owns the patient

Relationships:

```
User 1 ──── * Patient
User 1 ──── * Doctor          (creator / audit)
User 1 ──── * Mapping         (assigner / audit)
Patient 1 ── * Mapping * ── 1 Doctor
```

An explicit mapping model (instead of a bare `ManyToManyField`) is used so the
assignment keeps its own `id`, `assigned_by` audit field, `notes` and timestamps -
which is what the API's `DELETE /api/mappings/<id>/` endpoint requires.

---

## 12. Security Checklist

* [x] Passwords hashed with Django's PBKDF2 hasher (`set_password`), never stored or returned
* [x] JWT (HS256) access/refresh tokens signed with the env-provided `SECRET_KEY`
* [x] All non-auth endpoints require `IsAuthenticated` (default DRF permission)
* [x] Patient queries filtered by `created_by` - no cross-tenant reads
* [x] Explicit `403` when a record exists but belongs to another user, `404` when it does not
* [x] Serializer-level validation (required fields, email format, uniqueness, age bounds)
* [x] Duplicate patient-doctor assignments rejected by a DB unique constraint **and** the serializer
* [x] Secrets read from environment variables; `.env` is git-ignored; `.env.example` holds placeholders only
* [x] `HttpOnly` cookies, `X-Frame-Options: DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`
* [x] Production hardening flags (`SSL redirect`, `HSTS`, `secure cookies`) gated behind `DEBUG=False`
* [x] Custom JSON error handling for `/api/*` - no HTML error pages, no stack traces leaked
* [x] `SECRET_KEY` missing → application refuses to start (`ImproperlyConfigured`)

---

## 13. Running with Postman

Import **`postman_collection.json`** (root of this repo):

1. Postman → **Import** → select the file
2. The collection auto-acquires tokens: run **Auth → Register** then **Auth → Login**
3. The `{{base_url}}` (default `http://127.0.0.1:8000`) and `{{access_token}}`
   variables are set automatically by the login request
4. Every remaining request carries `Authorization: Bearer {{access_token}}`

---

## 14. Assumptions

Documented decisions where the assignment left the design open:

1. **Field schemas** - minimal healthcare fields chosen (age, gender, blood group,
   allergies, history for patients; specialization, qualification for doctors) as
   the assignment does not prescribe them.
2. **Doctors are a shared directory** - the assignment requires
   `GET /api/doctors/` to "retrieve all doctors", so any authenticated user can
   read and manage them; `created_by` is retained as an audit field.
3. **Patients are private** - filtered by `created_by`; foreign access returns `403`.
4. **`/api/mappings/<pk>/` dual meaning** - `GET` uses the parameter as a
   `patient_id`, `DELETE` uses it as a mapping `id` (see §7.4).
5. **No pagination** - list endpoints return plain JSON arrays, exactly as the
   assignment describes, to keep responses simple and predictable.
6. **`PATCH`** is supported in addition to the required `PUT` (standard DRF behaviour).
7. **Password policy** - minimum 8 characters plus Django's standard validators.
