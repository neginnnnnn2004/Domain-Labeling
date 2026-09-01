# 🛡️ DomainAuth - Identity & Access Management (IAM) Service

`DomainAuth` is a centralized, production-ready **Identity & Access Management (IAM)** web service built with **Django** and **Django REST Framework (DRF)**.

Designed with a highly clean, decoupled architecture, this service manages custom user authentication, granular group permissions, and enterprise domain tracking with dynamic tagging. It features a completely stateless, time-sensitive password reset mechanism that ensures top-tier security without database overhead.

---

## 🌟 Key Features

* **Custom User Architecture:** Built using a customized Django User Model (`User`), allowing the system to support additional user attributes such as roles, account status, phone number, verification status, and login tracking.

* **JWT Authentication:** Implements stateless authentication using JSON Web Tokens with short-lived access tokens and longer-lived refresh tokens.

* **Granular Access Control:** Provides role-based access control and dedicated permission classes for managing users, roles, groups, domains, and tags.

* **Secure Password Reset with Backup Codes:** Allows users to reset their password using a one-time backup code. Backup codes are securely hashed before being stored in the database and are marked as used after successful verification.

* **Automatic Backup Code Rotation:** After a backup code is successfully used for password recovery, it is invalidated and a new backup code is generated.

* **User Enumeration Protection:** Password reset failures use a generic error response for invalid account information and invalid backup codes, reducing the risk of revealing whether a username exists.

* **Domain & Tag Management:** Provides APIs for managing domains and dynamically assigning tags to domains, supporting classification, filtering, and organizational domain management.

* **Group Management:** Supports group creation, user-group assignment, primary group management, and domain association.

* **User Management:** Provides administrative functionality for managing users, roles, account status, and pending users.

* **Security Audit Logging:** Records security-sensitive events such as password reset attempts using structured logs while excluding sensitive information such as passwords, tokens, and backup codes.

* **Automated Testing:** Includes module-based unit and integration tests covering authentication, password reset, user management, group management, and domain/tag management.
---

## 📁 Project Architecture & Structure

The project follows the **Separation of Concerns (SoC)** principle by organizing authentication, user management, group management, and domain/tag management into separate Django applications.

Each application is responsible for its own domain-specific views, serializers, permissions, utilities, and test suites, while the `identity` application provides the core data models and shared identity-related functionality.

This modular architecture improves **maintainability, scalability, testability, and separation of responsibilities**.

```text
📁 iam2/                                      # Project root
│
├── 📁 identity/                              # Core identity and data models
│   ├── 📁 migrations/                        # Database migration files
│   ├── 📁 serializers/                       # Legacy/core DRF serializers
│   ├── 📁 tests/                             # Legacy/core test suites
│   ├── 📁 views/                             # Legacy/core API views
│   ├── __init__.py
│   ├── admin.py                              # Django admin configuration
│   ├── apps.py                               # Django application configuration
│   ├── formatters.py                         # Response/log formatting utilities
│   ├── models.py                             # Core data models
│   ├── permissions.py                        # Custom permission classes
│   ├── services.py                           # Service-layer and security audit helpers
│   ├── urls.py                               # Identity application routing
│   └── utils.py                              # Backup code generation and verification
│
├── 📁 accounts/                              # Authentication and account management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── get_my_role.py
│   │   ├── login.py
│   │   ├── profile_update.py
│   │   ├── register.py
│   │   └── reset_pass.py
│   │
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_get_my_role.py
│   │   ├── test_login.py
│   │   ├── test_profile_update.py
│   │   ├── test_register.py
│   │   └── test_reset_pass.py
│   │
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── get_my_role.py
│   │   ├── login.py
│   │   ├── profile_update.py
│   │   ├── register.py
│   │   └── reset_pass.py
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 user_management/                      # User and role management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── assign_role.py
│   │   ├── list_roles.py
│   │   ├── list_users.py
│   │   ├── manage_status.py
│   │   └── pending_users.py
│   │
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_assign_role.py
│   │   ├── test_list_roles.py
│   │   ├── test_list_users.py
│   │   ├── test_manage_status.py
│   │   └── test_pending_users.py
│   │
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── assign_role.py
│   │   ├── list_roles.py
│   │   ├── list_users.py
│   │   ├── manage_status.py
│   │   └── pending_users.py
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 group_management/                     # Group management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── group_assign_users.py
│   │   ├── group_detail.py
│   │   ├── group_domains.py
│   │   ├── group_list.py
│   │   └── group_register.py
│   │
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_group_assign_users.py
│   │   ├── test_group_detail.py
│   │   ├── test_group_domains.py
│   │   ├── test_group_list.py
│   │   └── test_group_register.py
│   │
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── group_assign_users.py
│   │   ├── group_detail.py
│   │   ├── group_domains.py
│   │   ├── group_list.py
│   │   └── group_register.py
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 domain_tag_management/                # Domain and tag management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── assign_tag_to_domain.py
│   │   ├── domain_list.py
│   │   ├── import_or_edit_domain.py
│   │   ├── tag_create.py
│   │   ├── tag_edit_or_delete.py
│   │   └── tag_list.py
│   │
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_assign_tag_to_domain.py
│   │   ├── test_domain_list.py
│   │   ├── test_import_or_edit_domain.py
│   │   ├── test_tag_create.py
│   │   ├── test_tag_edit_or_delete.py
│   │   └── test_tag_list.py
│   │
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── assign_tag_to_domain.py
│   │   ├── domain_list.py
│   │   ├── import_or_edit_domain.py
│   │   ├── tag_create.py
│   │   ├── tag_edit_or_delete.py
│   │   └── tag_list.py
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 middleware/                           # Custom Django middleware
│   ├── __init__.py
│   └── logging_middleware.py                # Request/response logging middleware
│
├── 📁 config/                               # Core Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                           # Project settings
│   ├── urls.py                               # Global URL routing
│   └── wsgi.py
│
├── .env.example                              # Environment variable template
├── .gitignore                                # Git ignore rules
├── .gitlab-ci.yml                            # GitLab CI/CD configuration
├── Dockerfile                                # Docker image configuration
├── LICENSE                                   # Project license
├── README.md                                 # Project documentation
├── requirements.txt                          # Python dependencies
├── manage.py                                 # Django management utility
├── logger.py                                 # Project-level logging configuration
├── import_domains.py                         # Domain data import script
├── delete_domains.py                         # Domain deletion/cleanup script
│
#not sure about xlsx file in tree... i should check it
├── 📄 Fa_domain (1).xlsx                     # Domain data source
└── 📄 لیست سایت های فارسی.xlsx                # Persian website/domain list```

### 🔐 Ignored Files

The following files and directories are intentionally excluded from version control
for security and environment-specific reasons:

- `.env` — Contains local environment variables and sensitive configuration.
- `logs/` — Contains runtime application and security logs.
- `.venv/` — Local Python virtual environment.

## 🚀 Installation & Setup

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://gitlab.lioradco.ir/domain-labeling/backend.git
cd backend
```

### 2. Configure Environment Variables

Create your local environment file from the provided template:

```bash
cp .env.example .env
```

> **Note:** Update the values in `.env` according to your local database and environment configuration. The `.env` file is not included in version control because it may contain sensitive information.

### 3. Configure the Virtual Environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

Run the Django database migrations:

```bash
python manage.py migrate
```

### 6. Run the Test Suite

Run all project tests to verify the application:

```bash
python manage.py test
```

### 7. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will then be available at:

```text
http://127.0.0.1:8000/
```

#it should be edit
# 🗺️ API Endpoints Reference — Authentication & Profile Management

Base path: `/accounts/`

---

## POST /accounts/register/

Registers a new user account and issues one-time backup recovery codes for
account recovery. Backup codes are shown only once at registration time and
must be stored securely by the client.

**Authentication:** Not required

**Request Body**

| Field              | Type   | Required | Notes                                                              |
|--------------------|--------|----------|-----------------------------------------------------------------------|
| `username`         | string | Yes      | 5–20 chars; letters, digits, `_`, `-` only. Normalized to lowercase.   |
| `password`         | string | Yes      | Min 8 chars; validated against Django's password strength rules.      |
| `confirm_password` | string | Yes      | Must match `password`.                                                |
| `email`            | string | Yes      | Must be unique. Normalized to lowercase.                              |
| `phone`            | string | Yes      | Iranian mobile format: `09xxxxxxxxx`. Must be unique.                  |
| `first_name`       | string | No       | —                                                                      |
| `last_name`        | string | No       | —                                                                      |

**Response — 201 Created**

```json
{
  "message": {
    "fa": "...",
    "en": "Registration successful. Please store your backup codes in a safe place."
  },
  "user": { "username": "...", "email": "...", "phone": "...", "first_name": "...", "last_name": "..." },
  "backup_codes": ["XXXXXXXX", "..."]
}
```

**Response — 400 Bad Request**

| `error_code` | Meaning                                                     |
|---------------|-----------------------------------------------------------------|
| 10            | Invalid input data (e.g. username format)                        |
| 11            | Username already exists                                          |
| 12            | One or more required fields missing or empty                     |
| 13            | Password is invalid (too weak, wrong format, too short)          |
| 14            | Phone number already registered                                  |
| 15            | Email address already registered                                 |
| 16            | Invalid email or phone number format                             |
| 17            | `password` and `confirm_password` do not match                  |

---

## POST /accounts/login/

Authenticates a user's credentials and issues a JWT access/refresh token
pair. To prevent brute-force and user-enumeration attacks, invalid
credentials and a deleted account return the same generic error.

**Authentication:** Not required

**Request Body**

| Field      | Type   | Required | Notes                                    |
|------------|--------|----------|--------------------------------------------|
| `username` | string | Yes      | Normalized to lowercase before lookup.      |
| `password` | string | Yes      | Plain-text password.                        |

**Response — 200 OK**

```json
{
  "access_token": "...",
  "refresh": "..."
}
```

**Response — 400 Bad Request**

| `error_code` | Meaning                                                        |
|---------------|-----------------------------------------------------------------|
| 10            | Provided data (username or password format) is missing or invalid |

**Response — 401 Unauthorized**

| `error_code` | Meaning                                                                   |
|---------------|-------------------------------------------------------------------------------|
| 20            | Username or password does not match records, or the account has been deleted   |
| 21            | Account status is inactive — `unverified`, `pending`, or `suspended`          |

**Account status behavior**

Only users with `status == 'active'` can log in successfully. Other statuses
map to distinct `en`/`fa` messages under the same `error_code: 21`:

| `status`     | Message summary                          |
|--------------|--------------------------------------------|
| `unverified` | Account not yet verified by an admin        |
| `pending`    | Account is pending approval                 |
| `suspended`  | Account has been suspended                  |

---

## POST /accounts/reset-password/

Resets a user's password using a one-time backup recovery code. Backup codes
are single-use and are invalidated immediately after a successful reset. A
new backup code is issued in the response to replace the used one.

**Authentication:** Not required

**Security notes**
- Invalid account information and invalid backup codes return the same
  generic error response, to prevent user enumeration.
- Passwords and backup codes are never written to security logs.

**Request Body**

| Field              | Type   | Required | Notes                                    |
|--------------------|--------|----------|----------------------------------------------|
| `username`         | string | Yes      | Normalized to lowercase before lookup.         |
| `backup_code`      | string | Yes      | One of the codes issued at registration.       |
| `new_password`     | string | Yes      | —                                               |
| `confirm_password` | string | Yes      | Must match `new_password`.                     |

**Response — 200 OK**

```json
{
  "message": {
    "fa": "...",
    "en": "Your password has been changed successfully. You can now log in."
  },
  "show_popup": true,
  "new_backup_code": "XXXXXXXX"
}
```

**Response — 400 Bad Request**

| `error_code` | Meaning                                                                         |
|---------------|-------------------------------------------------------------------------------------|
| 10            | Invalid input data or password format                                                |
| 75            | Invalid account information or backup code (covers nonexistent user, inactive account, and invalid/used backup code) |

---

## GET /accounts/myRole/

Returns the authenticated user's profile and role details.

**Authentication:** Required (JWT)

**Response — 200 OK**

Response body shape depends on `ReturnRoleUsersSerializer` (fields not
confirmed here — includes at minimum the user's role).

**Response — 401 Unauthorized**

Standard authentication failure (missing/invalid token).

**Response — 500 Internal Server Error**

```json
{
  "detail": "An error occurred while fetching user role / خطایی در دریافت نقش کاربر رخ داده است."
}
```

Returned when an unexpected exception occurs while serializing the user's
role data.

---

## PATCH /accounts/profile/update/

Partially updates the authenticated user's profile information. Only `PATCH`
is supported — there is no `PUT` (full replace) on this endpoint.

**Authentication:** Required (JWT)

**Request Body**

Fields are defined by `ProfileUpdateSerializer` (not fully enumerated here);
confirmed sensitive fields include `phone`, `password`, and
`confirm_password`. Successful changes to `phone` or `password` are logged
as sensitive-field changes.

**Response — 200 OK**

```json
{
  "message": {
    "fa": "پروفایل با موفقیت بروزرسانی شد",
    "en": "Profile updated successfully"
  },
  "data": { "...": "shape defined by ProfileUpdateResponseSerializer" }
}
```

**Response — 400 Bad Request**

| `error_code` | Meaning                                              |
|---------------|-----------------------------------------------------------|
| 10            | Invalid input data                                          |
| 30            | Password is invalid (weak or bad format)                    |
| 31            | Invalid phone number format                                 |
| 32            | `password` and `confirm_password` do not match              |
| 33            | Phone number already registered by another user              |

**Response — 401 Unauthorized**

Standard authentication failure (missing/invalid token).

2. User Lifecycle & Role Administration (user_views.py)
GET /api/accounts/users/ - Fetches a list of all registered users across the platform.

GET /api/accounts/users/pending/ - Filters and lists all accounts awaiting activation (status="pending"). Requires Admin privileges.

GET /api/accounts/roles/ - Lists all available system assignment roles.

PATCH /api/accounts/users/<int:pk>/role/ - Assigns a specialized access role to a chosen user (Validation codes: 10, 40).

PATCH /api/accounts/users/<int:pk>/status/ - Modifies a profile's operational state matrix (Validation codes: 10, 40).

DELETE /api/accounts/users/<int:pk>/ - Gracefully updates a target profile to the deleted state and stamps execution time.

PATCH /api/accounts/users/<int:pk>/activation/ - Directly alters the primitive is_active boolean value flags.

3. Stateless Password Reset Flow (reset_pass_views.py)
POST /api/accounts/reset-password/ - Initiates the reset. Sends a secure 10-minute token to the user's registered email (Protected against user enumeration).

POST /api/accounts/reset-password/confirm/ - Validates the cryptographic token and securely hashes/saves the new password.

4. Enterprise Domain & Tag Management (domain_views.py)
POST /api/accounts/domains/import/ - Admin-only operation to import or create structured domains.

GET /api/accounts/domains/ - Retrieves a tailored list of active domains depending on group visibility or admin scopes.

POST /api/accounts/tags/ - Creates a tracking metadata tag in the system (Admin-only).

GET /api/accounts/tags/ - Returns a dictionary list of all valid registered tracking metadata tags.

POST /api/accounts/domains/assign-tag/ - Bulk records assignment of metadata tags to specified domains (Handles conflict monitoring).

PATCH /api/accounts/domains/assign-tag/ - Multi-record transaction patch updating domain tags with explicit verification confirm flags.

5. Group & Access Control Management (group_views.py)
GET /api/accounts/groups/ - Lists all available operational organizational groups (Admin-only).

POST /api/accounts/groups/ - Instantiates a new system access or organizational group profile.

GET /api/accounts/groups/<int:pk>/ - Fetches detailed single-group structural metadata (Includes soft-delete filtration).

PUT /api/accounts/groups/<int:pk>/ - Completely updates group properties and operational identifiers.

PATCH /api/accounts/groups/<int:pk>/ - Selectively alters single properties on an active group profile.

DELETE /api/accounts/groups/<int:pk>/ - Handles graceful soft-deletion of organizational groups using timestamp tracking.

POST /api/accounts/groups/assign-user/ - Bridges active users to organizational access groups.

🛠️ Tech Stack & Security Implementations
Core Framework: Django

API Delivery & Documentation: Django REST Framework (DRF) & drf-yasg (Swagger/OpenAPI UI integration)

Token Operations: djangorestframework-simplejwt (JSON Web Tokens)

Cryptographic Signing: Django Core Signers (TimestampSigner)

Security Practices: Password hashing (PBKDF2), atomic transaction blocks for bulk tasks (transaction.atomic), custom protection filters against user enumeration attacks, and timing-attack resilient user lookups.