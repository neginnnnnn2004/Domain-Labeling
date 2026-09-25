# 🛡️ DomainAuth - Identity & Access Management (IAM) Service

`DomainAuth` is a centralized, production-ready **Identity & Access Management (IAM)** web service built with **Django** and **Django REST Framework (DRF)**.

The service provides custom authentication, JWT-based access, role-based authorization, user and group management, domain management, dynamic tag assignment, backup-code password recovery, and security audit logging.

---

## 🌟 Key Features

- **Custom User Architecture:** Customized Django `User` model supporting roles, account status, phone number, verification status, login tracking, and soft deletion.
- **JWT Authentication:** Stateless authentication using JSON Web Tokens.
- **Granular Access Control:** Dedicated permission classes for users, roles, groups, domains, and tags.
- **Secure Password Reset with Backup Codes:** One-time backup recovery codes are securely hashed and invalidated after use.
- **Automatic Backup Code Rotation:** A new backup code is generated after a successful password reset.
- **User Enumeration Protection:** Password-reset and login workflows use generic responses where appropriate to avoid revealing account existence.
- **Domain & Tag Management:** Domain import, update, deletion, tag creation, tag management, and bulk domain-tag synchronization.
- **Group Management:** Group creation, user-group assignment, primary-group support, and domain association.
- **User Management:** User listing, pending-user management, role assignment, status management, and soft deletion.
- **Security Audit Logging:** Security-sensitive events are recorded through structured logging without storing passwords, tokens, or backup codes.
- **Automated Testing:** Module-based tests covering authentication, password reset, user management, group management, and domain/tag management.

---

# 📁 Project Architecture & Structure

The project follows the **Separation of Concerns (SoC)** principle by organizing authentication, user management, group management, and domain/tag management into separate Django applications.

```text
📁 iam2/                                      # Project root
│
├── 📁 identity/                              # Core identity and data models
│   ├── 📁 migrations/                        # Database migration files
│   ├── 📁 serializers/                       # Legacy/core DRF serializers
│   ├── 📁 tests/                             # Legacy/core test suites
│   ├── 📁 views/                             # Legacy/core API views
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── formatters.py
│   ├── models.py                             # Core data models
│   ├── permissions.py
│   ├── services.py                            # Service/security audit helpers
│   ├── urls.py
│   └── utils.py
│
├── 📁 accounts/                              # Authentication and account management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── get_my_role.py
│   │   ├── login.py
│   │   ├── profile_update.py
│   │   ├── register.py
│   │   └── reset_pass.py
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_get_my_role.py
│   │   ├── test_login.py
│   │   ├── test_profile_update.py
│   │   ├── test_register.py
│   │   └── test_reset_pass.py
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── get_my_role.py
│   │   ├── login.py
│   │   ├── profile_update.py
│   │   ├── register.py
│   │   └── reset_pass.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 user_management/                       # User and role management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── assign_role.py
│   │   ├── list_roles.py
│   │   ├── list_users.py
│   │   ├── manage_status.py
│   │   └── pending_users.py
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_assign_role.py
│   │   ├── test_list_roles.py
│   │   ├── test_list_users.py
│   │   ├── test_manage_status.py
│   │   └── test_pending_users.py
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── assign_role.py
│   │   ├── list_roles.py
│   │   ├── list_users.py
│   │   ├── manage_status.py
│   │   └── pending_users.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 group_management/                      # Group management API
│   ├── 📁 serializers/
│   │   ├── group_detail.py
│   │   ├── group_domain_assign.py
│   │   ├── group_domains.py
│   │   ├── group_list.py
│   │   ├── group_members.py
│   │   ├── group_register.py
│   │   └── group_user_bulk_assign.py
│   ├── 📁 views/
│   │   ├── group_list.py
│   │   ├── group_register.py
│   │   ├── group_detail.py
│   │   ├── group_user_bulk_assign.py
│   │   ├── group_domains.py
│   │   ├── group_members.py
│   │   └── group_domain_assign.py
│   └── urls.py
│
├── 📁 domain_tag_management/                 # Domain and tag management
│   ├── 📁 serializers/
│   │   ├── __init__.py
│   │   ├── assign_tag_to_domain.py
│   │   ├── domain_list.py
│   │   ├── import_or_edit_domain.py
│   │   ├── tag_create.py
│   │   ├── tag_edit_or_delete.py
│   │   └── tag_list.py
│   ├── 📁 tests/
│   │   ├── __init__.py
│   │   ├── test_assign_tag_to_domain.py
│   │   ├── test_domain_list.py
│   │   ├── test_import_or_edit_domain.py
│   │   ├── test_tag_create.py
│   │   ├── test_tag_edit_or_delete.py
│   │   └── test_tag_list.py
│   ├── 📁 views/
│   │   ├── __init__.py
│   │   ├── assign_tag_to_domain.py
│   │   ├── domain_list.py
│   │   ├── import_or_edit_domain.py
│   │   ├── tag_create.py
│   │   ├── tag_edit_or_delete.py
│   │   └── tag_list.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── utils.py
│
├── 📁 middleware/
│   ├── __init__.py
│   └── logging_middleware.py
│
├── 📁 config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env.example
├── .gitignore
├── .gitlab-ci.yml
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
├── manage.py
├── logger.py
├── import_domains.py
└── delete_domains.py
```

> **Note:** The two `.xlsx` files previously listed in the project tree are intentionally not included in the canonical tree above because their current repository status has not yet been confirmed.

---

# 🔐 Ignored Files

The following files/directories are intentionally excluded from version control:

- `.env` — local environment variables and sensitive configuration.
- `logs/` — runtime and security logs.
- `.venv/` — local Python virtual environment.

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://gitlab.lioradco.ir/domain-labeling/backend.git
cd backend
```

## 2. Configure Environment Variables

Create the local environment file:

```bash
cp .env.example .env
```

> **Windows:** If `cp` is unavailable, copy `.env.example` manually and rename it to `.env`.

Update `.env` according to the local database and environment configuration.

The `.env` file must not be committed to Git.

## 3. Create the Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

The project currently includes:

```text
drf-spectacular==0.30.0
```

for OpenAPI schema/documentation.

## 5. Apply Database Migrations

```bash
python manage.py migrate
```

## 6. Run Tests

```bash
python manage.py test
```

## 7. Run the Development Server

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

---

# 🔑 Authentication & Authorization

Most protected endpoints require JWT authentication.

The main application roles are:

- `limited`
- `regular`
- `admin`
- `super_admin`

## Permission Classes

### `IsAdminRole`

Allows active users whose role is:

```text
admin
super_admin
```

### `IsSuperAdmin`

Allows active users whose role is:

```text
super_admin
```

### `IsAllowedUser`

Allows active users whose role is:

```text
regular
admin
super_admin
```

A `limited` user does not pass `IsAllowedUser`.

> Permission checks are based on the user's active status and assigned role. The domain/tag assignment logic does not use a separate `is_superuser` bypass.

---

# 🗺️ API Endpoints Reference — Authentication & Profile Management

**Base path:** `/accounts/`

---

## POST `/accounts/register/`

Registers a new user account and issues one-time backup recovery codes.

**Authentication:** Not required

### Request Body

| Field | Type | Required | Notes |
|---|---|---:|---|
| `username` | string | Yes | 5–20 chars; letters, digits, `_`, `-`; normalized to lowercase |
| `password` | string | Yes | Minimum 8 chars; validated by password rules |
| `confirm_password` | string | Yes | Must match `password` |
| `email` | string | Yes | Unique; normalized to lowercase |
| `phone` | string | Yes | Iranian mobile format: `09xxxxxxxxx`; unique |
| `first_name` | string | No | — |
| `last_name` | string | No | — |

### Response — 201 Created

```json
{
  "message": {
    "fa": "...",
    "en": "Registration successful. Please store your backup codes in a safe place."
  },
  "user": {
    "username": "...",
    "email": "...",
    "phone": "...",
    "first_name": "...",
    "last_name": "..."
  },
  "backup_codes": ["XXXXXXXX", "..."]
}
```

### Response — 400 Bad Request

| `error_code` | Meaning |
|---:|---|
| `10` | Invalid input data |
| `11` | Username already exists |
| `12` | Required field missing/empty |
| `13` | Invalid/weak password |
| `14` | Phone number already registered |
| `15` | Email already registered |
| `16` | Invalid email or phone format |
| `17` | Password confirmation does not match |

---

## POST `/accounts/login/`

Authenticates user credentials and issues a JWT access/refresh token pair.

**Authentication:** Not required

### Request Body

| Field | Type | Required | Notes |
|---|---|---:|---|
| `username` | string | Yes | Normalized to lowercase |
| `password` | string | Yes | Plain-text password |

### Response — 200 OK

```json
{
  "access_token": "...",
  "refresh": "..."
}
```

### Response — 400 Bad Request

| `error_code` | Meaning |
|---:|---|
| `10` | Missing or invalid request data |

### Response — 401 Unauthorized

| `error_code` | Meaning |
|---:|---|
| `20` | Username/password mismatch or deleted account |
| `21` | Account is inactive |

### Account Status Behavior

Only:

```text
status == active
```

can log in successfully.

| Status | Meaning |
|---|---|
| `unverified` | Account is not yet verified |
| `pending` | Account is awaiting approval |
| `suspended` | Account has been suspended |
| `active` | Account can authenticate |

---

## POST `/accounts/reset-password/`

Resets the password using a one-time backup recovery code.

**Authentication:** Not required

### Security Notes

- Invalid account information and invalid backup codes use a generic error.
- Backup codes are single-use.
- The used backup code is invalidated.
- A new backup code is issued after a successful reset.
- Passwords and backup codes are not written to security logs.

### Request Body

| Field | Type | Required |
|---|---|---:|
| `username` | string | Yes |
| `backup_code` | string | Yes |
| `new_password` | string | Yes |
| `confirm_password` | string | Yes |

### Response — 200 OK

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

### Response — 400 Bad Request

| `error_code` | Meaning |
|---:|---|
| `10` | Invalid input or password format |
| `75` | Invalid account information or backup code |

---

## GET `/accounts/myRole/`

Returns the authenticated user's profile and role information.

**Authentication:** Required (JWT)

### Response — 200 OK

Response shape is defined by `ReturnRoleUsersSerializer`.

### Response — 401 Unauthorized

Standard authentication failure.

### Response — 500 Internal Server Error

```json
{
  "detail": "An error occurred while fetching user role / خطایی در دریافت نقش کاربر رخ داده است."
}
```

---

## PATCH `/accounts/profile/update/`

Partially updates the authenticated user's profile.

**Authentication:** Required (JWT)

Only `PATCH` is supported.

Sensitive changes such as phone/password changes are logged.

### Response — 200 OK

```json
{
  "message": {
    "fa": "پروفایل با موفقیت بروزرسانی شد",
    "en": "Profile updated successfully"
  },
  "data": {
    "...": "shape defined by ProfileUpdateResponseSerializer"
  }
}
```

### Response — 400 Bad Request

| `error_code` | Meaning |
|---:|---|
| `10` | Invalid input |
| `30` | Invalid password |
| `31` | Invalid phone number |
| `32` | Password confirmation mismatch |
| `33` | Phone number already registered |

### Response — 401 Unauthorized

Standard authentication failure.

---

# 🗺️ API Endpoints Reference — User Management

**Base path:** `/user_management/`

> The base path is confirmed by the project's root URL configuration:
>
> ```python
> path("user_management/", include("user_management.urls"))
> ```

## Permission Levels

| Permission | Roles |
|---|---|
| `IsSuperAdmin` | active `super_admin` |
| `IsAdminRole` | active `admin` or `super_admin` |

---

## GET `/user_management/admin/list-of-users/`

Lists registered users.

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsAdminRole`

### Response — 200 OK

```json
[
  {
    "...": "shape defined by ListOfUsersSerializer"
  }
]
```

### Response — 403 Forbidden

Authenticated user does not have an admin role.

### Response — 500 Internal Server Error

```json
{
  "detail": "An unexpected error occurred / خطای غیرمنتظره‌ای رخ داده است."
}
```

---

## GET `/user_management/admin/list-of-pending-users/`

Lists users whose status is:

```text
pending
```

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsAdminRole`

No additional pagination/filtering is applied by this endpoint.

---

## GET `/user_management/admin/list-of-roles/`

Lists available system roles.

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsAdminRole`

### Response — 200 OK

```json
[
  {
    "...": "shape defined by ListOfRolesSerializer"
  }
]
```

---

## PATCH `/user_management/super-admin/users/{pk}/assign/role/`

Assigns or changes a user's role.

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsSuperAdmin`

### Path Parameter

| Field | Type |
|---|---|
| `pk` | int |

### Request Body

```json
{
  "role": 1
}
```

`role` is the ID of the target `Role`.

The serializer is used with `partial=True`.

### Response — 200 OK

```json
{
  "message": "User role updated successfully / نقش کاربر با موفقیت بروزرسانی شد.",
  "data": {
    "...": "shape defined by UserRoleUpdateSerializer"
  }
}
```

### Response — 400 Bad Request

| `error_code` | Meaning |
|---:|---|
| `10` | Invalid payload or attempt to change own role |

### Response — 404 Not Found

| `error_code` | Meaning |
|---:|---|
| `40` | Target user not found or soft-deleted |

### Business Rules

- A user cannot change their own role.
- Successful and failed attempts are recorded through `log_critical_event`.
- The target user must not be soft-deleted.

---

## PATCH `/user_management/super-admin/users/{pk}/change/status/`

Changes a user's status.

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsSuperAdmin`

### Valid Status Values

```text
pending
active
suspended
unverified
```

### Request Body

```json
{
  "status": "active"
}
```

### Response — 200 OK

```json
{
  "message": "User status updated successfully to '{new_status}' / وضعیت کاربر با موفقیت به {new_status} تغییر یافت.",
  "data": {
    "...": "shape defined by UserStatusUpdateSerializer"
  }
}
```

### Response — 400 Bad Request

```text
error_code: 10
```

Invalid status value.

### Response — 404 Not Found

```text
error_code: 40
```

Target user does not exist or is soft-deleted.

### Business Rules

- Successful and failed status changes are logged.
- The log contains the old and new status.
- The current implementation does not apply a self-status-change restriction.

---

## DELETE `/user_management/super-admin/users/{pk}/change/status/`

Soft-deletes a user.

The same URL as the PATCH endpoint is used; the HTTP method determines the operation.

**Authentication:** Required (JWT)

**Permissions:** `IsAuthenticated`, `IsSuperAdmin`

### Response — 204 No Content

Empty response body.

### Soft Delete Behavior

The user is not physically removed.

Instead:

```text
deleted_at = current time
status = deleted
```

---

# 🌐 Domain & Tag Management

The current domain/tag functionality is implemented in:

```text
domain_tag_management/
```

The application is mounted at `/domain_tag_management/` in `config/urls.py`. The routes below are the exact paths defined by the application URL configuration.

---

## Domain API

### GET `/domain_tag_management/domain/detail/list/`

Lists active domains visible to the authenticated user.

**Permission:** `IsAuthenticated`

### Visibility Rules

For `admin` and `super_admin`:

- active domains are available according to the admin scope.

For other authenticated users:

- domains belonging to the user's groups are visible.
- ungrouped domains are visible.
- deleted domains are excluded.

### Query Parameters

```text
search
page
page_size
```

Default:

```text
page_size = 20
```

Maximum:

```text
page_size = 100
```

Example:

```http
GET domain/detail/list/?search=example&page=1&page_size=20
```

---

## POST `/domain_tag_management/import-or-edit/domain/`

Creates/imports domains.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

Both a single object and a list are supported.

### Example

```json
{
  "domain_name": "example.com",
  "description": "Example domain",
  "group": 1
}
```

### Bulk Example

```json
[
  {
    "domain_name": "example.com",
    "description": "Example domain",
    "group": 1
  },
  {
    "domain_name": "example.org",
    "description": "Example organization",
    "group": null
  }
]
```

### Domain Normalization

The import workflow normalizes domain input, including:

- lowercasing
- accepting domains with or without an HTTP/HTTPS prefix
- parsing the hostname
- removing a parsed port

Existing active domains are skipped.

Soft-deleted domains can be reactivated.

---

## PATCH `/domain_tag_management/import-or-edit/domain/`

Bulk-updates existing domains.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

The update workflow is transactional.

---

## DELETE `/domain_tag_management/import-or-edit/domain/`

Bulk soft-deletes domains.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

Domains receive a `deleted_at` timestamp instead of being physically deleted.

The operation is transactional.

---

## GET `/domain_tag_management/domain/<int:pk>/detail/`

Returns details for a specific domain.

**Permission:** `IsAuthenticated`

The returned information depends on the user's access and the current domain/tag rules.

---

# 🏷️ Tag API

## POST `/domain_tag_management/tag/create/`

Creates a tag.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

### Example

```json
{
  "title": "Technology",
  "description": "Technology related domains"
}
```

### Tag Normalization

The normalized title is generated from:

```text
title.strip().lower()
```

A deterministic tag code is generated from the normalized title.

Duplicate tag titles are rejected.

Known validation codes include:

| `error_code` | Meaning |
|---:|---|
| `10` | General validation error |
| `11` | Duplicate tag title |

---

## GET `/domain_tag_management/tag/detail/list`

Lists active, non-deleted tags.

**Permission:** `IsAuthenticated`

Tags are ordered by title.

> The current URL configuration defines this route **without a trailing slash**.

---

## PATCH `/domain_tag_management/tag/<int:pk>/edit/`

Updates an active tag.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

If the tag does not exist or has been soft-deleted, the endpoint returns:

```text
error_code: 55
```

---

## DELETE `/domain_tag_management/tag/<int:pk>/edit/`

Soft-deletes a tag.

**Permissions:**

```text
IsAuthenticated
IsAdminRole
```

The tag is marked:

```text
deleted_at != null
is_active = false
```

The response is:

```text
204 No Content
```

---

# 🔗 Domain-Tag Assignment API

## POST `/domain_tag_management/tag-assign-to-domain/`

Synchronizes domain-tag assignments.

**Permissions:**

```text
IsAuthenticated
IsAllowedUser
```

The endpoint supports:

- add
- update
- delete

in a single bulk request.

---

## Request Structure

```json
{
  "add": [],
  "update": [],
  "delete": []
}
```

All three arrays are optional.

---

## Add Tags

```json
{
  "add": [
    {
      "domain_name": "example.com",
      "title": "Technology"
    }
  ]
}
```

---

## Update Tags

```json
{
  "update": [
    {
      "domain_name": "example.com",
      "old_title": "Technology",
      "title": "Software",
      "confirm": true
    }
  ]
}
```

The `confirm` field is used by the update workflow where explicit confirmation is required.

---

## Delete Tags

```json
{
  "delete": [
    {
      "domain_name": "example.com",
      "title": "Software"
    }
  ]
}
```

The delete `title` field may be optional according to the current serializer definition.

---

# 👁️ Domain/Tag Visibility Rules

The domain-list and assignment logic applies role-based tag visibility.

## Admin / Super Admin

For an admin or super-admin user:

- relevant tags can be returned according to the endpoint's visibility rules.
- the user can add tags subject to the main-tag limit.
- main tags are determined from assignments associated with admin/super-admin users.

## Regular User

A regular user can access domains permitted by group/ungrouped-domain visibility.

Tag visibility and tag creation are restricted according to the current domain/tag assignment rules.

## Limited User

A limited user does not pass `IsAllowedUser` and therefore cannot use the domain-tag assignment endpoint.

---

# ⭐ Main Tag Rule

The domain/tag logic contains a maximum main-tag rule.

For eligible administrators:

```text
Maximum main tags per domain = 2
```

When two main tags are already assigned by eligible admin/super-admin users, another normal main-tag assignment is not permitted by the main-tag rule.

The domain list may expose:

```text
can_add_tag
```

to indicate whether the current user can add a tag under the applicable rules.

---

# 👥 Group Management

The `group_management` application provides group CRUD operations, group membership management, domain assignment, and role-aware group-domain/tag visibility.

The application is mounted at:

```text
/group_management/
```

## Group Management Structure

```text
group_management/
├── serializers/
│   ├── group_detail.py
│   ├── group_domain_assign.py
│   ├── group_domains.py
│   ├── group_list.py
│   ├── group_members.py
│   ├── group_register.py
│   └── group_user_bulk_assign.py
├── views/
│   ├── group_list.py
│   ├── group_register.py
│   ├── group_detail.py
│   ├── group_user_bulk_assign.py
│   ├── group_domains.py
│   ├── group_members.py
│   └── group_domain_assign.py
└── urls.py
```

## Group API

### GET `/group_management/list/`

Returns the list of active groups.

**Authentication:** Required

### Admin / Superadmin response

Admin users receive:

```json
[
  {
    "id": 1,
    "code": 123456789,
    "title": "Example Group",
    "description": "Example description",
    "is_active": true,
    "user_count": 5
  }
]
```

`user_count` counts active `UserGroup` memberships.

### Other authenticated users

Non-admin users receive only groups they are active members of, with:

```json
[
  {
    "id": 1,
    "title": "Example Group",
    "description": "Example description"
  }
]
```

Deleted groups and deleted memberships are excluded.

---

## POST `/group_management/create/`

Creates a new group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

### Request Body

```json
{
  "title": "Example Group",
  "description": "Example description"
}
```

### Response — 201 Created

```json
{
  "id": 1,
  "title": "Example Group",
  "code": 123456789,
  "description": "Example description"
}
```

### Validation

Group titles are normalized using `strip().lower()` for duplicate detection. A title that matches an existing normalized title is rejected.

`error_code: 10` is returned for invalid group creation data.

---

## GET `/group_management/<id>/detail/`

Returns the details of an active group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

If the group does not exist or has been soft-deleted:

```text
HTTP 404
error_code: 65
```

---

## PATCH `/group_management/<id>/detail/`

Partially updates an active group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

The update uses `GroupSerializer` with `partial=True`. Model fields marked read-only by the serializer include:

```text
assigned_by
deleted_at
created_at
updated_at
code
```

### Error responses

| Status | Error | Meaning |
|---|---:|---|
| `400` | `10` | Submitted group data is invalid |
| `404` | `65` | Group does not exist or has been deleted |

---

## DELETE `/group_management/<id>/detail/`

Soft-deletes an active group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

The group is not physically deleted. Instead, `deleted_at` is populated.

### Response

```text
204 No Content
```

If the group does not exist or has already been deleted:

```text
404 Not Found
error_code: 65
```

---

# 👤 Group Members

## GET `/group_management/group/<group_id>/members/`

Returns active members of a group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

Deleted users and soft-deleted memberships are excluded.

### Member fields

The response includes:

- membership `id`
- `user_id`
- `username`
- `email`
- `first_name`
- `last_name`
- `is_primary`
- `assigned_by`
- `created_at`

If the group does not exist or has been deleted, the endpoint returns `404` with `error_code: 65`.

---

## DELETE `/group_management/group/<group_id>/members/<user_id>/`

Soft-removes a user from a group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

The membership record is retained and its `deleted_at` value is set.

### Error responses

| Status | Error | Meaning |
|---|---:|---|
| `404` | `65` | Group does not exist or has been deleted |
| `404` | `67` | User is not an active member of the group |

Successful removal returns `204 No Content`.

---

# 👥 Bulk User Assignment

## POST `/group_management/group/<group_id>/users/assign/`

Adds and/or removes multiple users from a group in one request.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

### Request Body

```json
{
  "add": [
    {
      "user_id": 1,
      "is_primary": true
    },
    {
      "user_id": 2
    }
  ],
  "remove": [
    {
      "user_id": 5
    }
  ]
}
```

Both arrays are optional and default to empty lists.

### Validation rules

Before any database changes are made, the endpoint validates:

- the target group exists and is not deleted;
- each added user exists and is not deleted;
- a user is not already an active member;
- the same user ID is not repeated in the request;
- a user marked as `is_primary=true` does not already have another active primary group;
- every removed user is an active member of the target group.

If validation fails, no assignment changes are applied.

### Primary Group Rule

A user can have at most one active primary group. This rule is enforced in the view before `bulk_create`, because bulk creation bypasses serializer-level validation.

### Successful response

```json
{
  "message": {
    "fa": "تغییرات با موفقیت اعمال شد.",
    "en": "Changes were applied successfully."
  },
  "result": {
    "added": 2,
    "removed": 1
  }
}
```

HTTP status: `200 OK`.

### Error codes

| Status | Error | Meaning |
|---|---:|---|
| `400` | `60` | One or more requested changes are invalid |
| `404` | `65` | Target group does not exist or has been deleted |

The database changes are applied inside `transaction.atomic()`.

---

# 🌐 Group Domain Assignment

## POST `/group_management/group/<group_id>/domains/assign/`

Adds and/or removes domains from a group.

**Permissions:** `IsAuthenticated`, `IsAdminRole`

### Request Body

```json
{
  "add": [
    {
      "domain_name": "example.com"
    }
  ],
  "remove": [
    {
      "domain_name": "old-example.com"
    }
  ]
}
```

Both arrays are optional and default to empty lists. An empty object is therefore valid input and results in zero additions/removals when no validation errors exist.

### Add behavior

- The domain must exist and not be soft-deleted.
- Assigning a domain already assigned to the same group is an error.
- A domain assigned to another group is moved to the requested group.

### Remove behavior

- The domain must exist and not be soft-deleted.
- The domain must currently belong to the requested group.
- Removal sets the domain's `group` to `NULL`.

Duplicate domain names within the request are rejected. All validation is completed before database changes are applied.

### Successful response

```json
{
  "message": {
    "fa": "تغییرات با موفقیت اعمال شد.",
    "en": "Changes were applied successfully."
  },
  "result": {
    "added": 1,
    "removed": 1
  }
}
```

HTTP status: `200 OK`.

### Error codes

| Status | Error | Meaning |
|---|---:|---|
| `400` | `60` | One or more requested changes are invalid |
| `404` | `65` | Target group does not exist or has been deleted |

Changes are applied using `transaction.atomic()` and `bulk_update()`.

---

# 🌍 Group Domains & Tag Visibility

## GET `/group_management/group/<group_id>/domains/`

Returns active domains associated with a specific group and applies role-aware tag visibility.

**Authentication:** Required

### Group access

- `admin` and `super_admin` users can access domains of groups regardless of membership.
- Other users must be an active member of the requested group.
- If the group does not exist or is deleted, the endpoint returns `404` with `error_code: 65`.
- A non-admin user without group membership receives `403` with `error_code: 66`.

### Domain response

Each returned domain is based on `DomainRegisterSerializer` and is extended with:

```text
tags
can_add_tag
has_main_tag
```

### Tag visibility

#### Admin / Superadmin

- All active domain-tag assignments are visible.
- `can_add_tag` is `true`.
- `tags_overview` is included.
- `tags_overview` contains each tag, its assignment count, and the users associated with that tag.

#### Limited

- Only main tags are visible.
- `can_add_tag` is `false`.

#### Regular user with a main tag present

- Only main tags are visible.
- `can_add_tag` is `false`.

#### Regular user without a main tag present

- Main tags and the current user's tags are visible.
- Duplicate tags are de-duplicated by tag ID.
- `can_add_tag` is `true` only when the current user has not already assigned a tag to the domain.

A main tag is determined by an assignment whose user has the `admin` or `super_admin` role.

> **Implementation note:** `GroupDomainView` also treats `request.user.is_superuser` as admin for its access and tag-visibility logic.

---

# 📋 Group Management API Summary

| Method | Endpoint | Purpose | Permission |
|---|---|---|---|
| GET | `/group_management/list/` | List active groups | Authenticated |
| POST | `/group_management/create/` | Create group | Admin / Superadmin |
| GET | `/group_management/<id>/detail/` | Group detail | Admin / Superadmin |
| PATCH | `/group_management/<id>/detail/` | Update group | Admin / Superadmin |
| DELETE | `/group_management/<id>/detail/` | Soft-delete group | Admin / Superadmin |
| GET | `/group_management/group/<group_id>/domains/` | List group domains + visible tags | Authenticated |
| POST | `/group_management/group/<group_id>/domains/assign/` | Add/remove group domains | Admin / Superadmin |
| GET | `/group_management/group/<group_id>/members/` | List active members | Admin / Superadmin |
| DELETE | `/group_management/group/<group_id>/members/<user_id>/` | Soft-remove member | Admin / Superadmin |
| POST | `/group_management/group/<group_id>/users/assign/` | Bulk add/remove users | Admin / Superadmin |

# 🗃️ Core Data Model

The identity layer contains the core entities used throughout the service.

## User

Important fields include:

- `username`
- `email`
- `phone`
- `status`
- `email_verified`
- `failed_login_attempts`
- `last_login_at`
- `role`
- `created_at`
- `updated_at`
- `deleted_at`

Username rules include:

```text
5–20 characters
letters / digits / _ / -
lowercased on save
```

Phone format:

```text
^09\d{9}$
```

---

## Role

Supported role codes:

```text
limited
regular
admin
super_admin
```

Roles also contain:

- title
- level
- system-role flag
- timestamps

---

## Group

Groups contain:

- code
- title
- normalized title
- description
- active state
- assigned-by user
- timestamps
- soft-delete timestamp

---

## UserGroup

Connects users to groups and supports:

- group membership
- primary group
- assigning user
- soft deletion

The database enforces uniqueness for active relationships and active primary-group assignment.

---

## Domain

Domains contain:

- domain name
- description
- creator
- group
- timestamps
- soft-delete timestamp

A domain can be associated with a group or remain ungrouped.

---

## Tag

Tags contain:

- title
- normalized title
- deterministic code
- description
- creator
- active state
- timestamps
- soft-delete timestamp

---

## User_Domain_Tag

Connects:

```text
User
Domain
Tag
```

and prevents duplicate active user/domain/tag assignments.

---

## Backup_Code

Backup codes are stored securely using hashed values.

They include:

- user
- hashed code
- used state
- creation timestamp

---

# 🗑️ Soft Delete

The project uses soft deletion for several entities.

Instead of physically removing a record:

```text
deleted_at
```

is populated.

For tags, deletion also sets:

```text
is_active = false
```

For users, soft deletion sets:

```text
deleted_at = current time
status = deleted
```

Soft-deleted records are excluded from active workflows.

---

# 🔄 Transactions

Bulk workflows use `transaction.atomic()` where atomic behavior is required.

Examples include:

- bulk domain updates
- bulk domain deletion
- domain-tag synchronization
- other security-sensitive bulk operations

The goal is to prevent partial database state when a transactional operation fails.

---

# 📝 Security Audit Logging

Security-sensitive operations are logged through the project's logging/service layer.

Examples include:

- password reset attempts
- role changes
- status changes
- sensitive profile changes
- domain/tag security-sensitive operations

Sensitive values such as:

- passwords
- JWT tokens
- backup codes

must not be written to security logs.

---

# ⚠️ Error Handling

The project uses both:

1. Standard Django REST Framework HTTP status responses.
2. Application-specific `error_code` values for domain-specific validation and business rules.

Examples documented by the current APIs include:

| Error Code | Usage |
|---:|---|
| `10` | General validation error in several workflows |
| `11` | Duplicate tag title / username-related workflow depending on endpoint |
| `20` | Invalid login credentials/deleted account |
| `21` | Inactive account |
| `30` | Invalid password during profile update |
| `31` | Invalid phone during profile update |
| `32` | Password confirmation mismatch |
| `33` | Duplicate phone during profile update |
| `40` | Target user not found/soft-deleted |
| `55` | Tag not found/unavailable |
| `75` | Invalid password-reset account/backup-code information |
| `403` | Access denied in applicable domain/tag authorization checks |

> Error codes are endpoint-specific. The same numeric code should not be assumed to have identical semantics across every application.

---

# 📚 API Documentation

The project uses OpenAPI tooling for API documentation.

The current dependency set includes:

```text
drf-spectacular==0.30.0
```

`drf-yasg` is also retained in the project's dependency set where required by the existing codebase.

The configured OpenAPI/schema routes should be checked in `config/urls.py`.

---

# 🧪 Testing

Run all tests:

```bash
python manage.py test
```

Run a specific application:

```bash
python manage.py test user_management
```

Run a specific test module:

```bash
python manage.py test user_management.tests.test_manage_status
```

For domain/tag workflows, tests should cover:

- domain creation
- duplicate domains
- domain normalization
- domain reactivation
- bulk domain update
- bulk domain delete
- tag creation
- duplicate tag handling
- tag update
- tag soft deletion
- tag visibility
- domain-tag add
- domain-tag update
- domain-tag delete
- permission restrictions
- main-tag limit
- transactional rollback

---

# 🐳 Docker

The project contains a `Dockerfile`.

Dependencies are installed from:

```text
requirements.txt
```

Whenever a Python dependency is added or changed, the Docker image used by the deployment environment must be rebuilt.

For example, after adding:

```text
drf-spectacular==0.30.0
```

the deployment must build a new image containing that package.

An already-running container does not automatically receive changes made to `requirements.txt`.

---

# 🚀 GitLab CI/CD

The repository contains:

```text
.gitlab-ci.yml
```

The CI/CD configuration defines the project's automated build/deployment workflow.

The exact jobs, runners, variables, and deployment commands are environment-specific and should be taken directly from the current `.gitlab-ci.yml`.

---

# 🔒 Security Considerations

- Use JWT authentication for protected APIs.
- Enforce role-based authorization through DRF permissions.
- Keep secrets in environment variables.
- Never commit `.env`.
- Never log passwords, backup codes, or tokens.
- Use soft deletion for entities where historical records must be preserved.
- Use transactions for atomic bulk operations.
- Use `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` appropriately.
- Rebuild deployment images after dependency changes.

---

# 🛠️ Development Workflow

When changing an API:

1. Update the corresponding view.
2. Update serializers.
3. Update URL configuration if the route changes.
4. Add or update tests.
5. Run the relevant tests.
6. Run the full test suite when appropriate.
7. Update OpenAPI documentation/schema.
8. Update this README.
9. If dependencies changed, update `requirements.txt`.
10. Rebuild the Docker image for deployment.

---

# 📋 Current Domain & Tag API Summary

| Method | Endpoint | Purpose | Permission |
|---|---|---|---|
| GET | `/domain_tag_management/domain/detail/list/` | List visible active domains | Authenticated |
| POST | `/domain_tag_management/import-or-edit/domain/` | Create/import domains | Admin / Super Admin |
| PATCH | `/domain_tag_management/import-or-edit/domain/` | Bulk update domains | Admin / Super Admin |
| DELETE | `/domain_tag_management/import-or-edit/domain/` | Bulk soft-delete domains | Admin / Super Admin |
| GET | `/domain_tag_management/domain/<pk>/detail/` | Domain detail | Authenticated |
| POST | `/domain_tag_management/tag/create/` | Create tag | Admin / Super Admin |
| GET | `/domain_tag_management/tag/detail/list` | List active tags | Authenticated |
| PATCH | `/domain_tag_management/tag/<pk>/edit/` | Update tag | Admin / Super Admin |
| DELETE | `/domain_tag_management/tag/<pk>/edit/` | Soft-delete tag | Admin / Super Admin |
| POST | `/domain_tag_management/tag-assign-to-domain/` | Add/update/delete domain tags | Allowed User |

---

# 📋 Current Authentication & User Management API Summary

| Method | Endpoint | Purpose | Permission |
|---|---|---|---|
| POST | `/accounts/register/` | Register user | Public |
| POST | `/accounts/login/` | Login | Public |
| POST | `/accounts/reset-password/` | Password reset | Public |
| GET | `/accounts/myRole/` | Get current role/profile | Authenticated |
| PATCH | `/accounts/profile/update/` | Update profile | Authenticated |
| GET | `/user_management/admin/list-of-users/` | List users | Admin / Super Admin |
| GET | `/user_management/admin/list-of-pending-users/` | List pending users | Admin / Super Admin |
| GET | `/user_management/admin/list-of-roles/` | List roles | Admin / Super Admin |
| PATCH | `/user_management/super-admin/users/{pk}/assign/role/` | Assign role | Super Admin |
| PATCH | `/user_management/super-admin/users/{pk}/change/status/` | Change status | Super Admin |
| DELETE | `/user_management/super-admin/users/{pk}/change/status/` | Soft-delete user | Super Admin |

---

# 📌 Documentation Status

The README documents the currently reviewed application structure and API behavior for:

- Authentication and account management
- User and role management
- Group management
- Group membership management
- Group-domain assignment
- Domain management
- Tag management
- Domain-tag assignment
- Role-based access control
- Soft deletion
- Security audit logging
- Docker/dependency considerations
- Testing and development workflow

---

# 🧰 Tech Stack & Security

### Core Framework

```text
Django
Django REST Framework
```

### Authentication

```text
djangorestframework-simplejwt
```

### API Documentation

```text
drf-spectacular
drf-yasg
```

### Database

```text
PostgreSQL
```

### Deployment

```text
Docker
GitLab CI/CD
```

### Security

- Django password hashing
- JWT authentication
- One-time hashed backup codes
- Timestamp-based/security-sensitive recovery workflow
- Role-based permissions
- User enumeration protection
- Atomic transactions
- Security audit logging
- Soft deletion

---

# 📄 License

See the `LICENSE` file for the project's license and usage terms.
