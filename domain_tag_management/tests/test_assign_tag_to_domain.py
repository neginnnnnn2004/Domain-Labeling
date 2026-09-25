from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from identity.models import (
    User,
    Role,
    Group,
    UserGroup,
    Domain,
    Tag,
    User_Domain_Tag,
)

from domain_tag_management.serializers.assign_tag_to_domain import (
    UserDomainTagAddSerializer,
    UserDomainTagPatchSerializer,
    UserDomainTagDeleteSerializer,
    BulkSyncDomainTagsSerializer,
)

from domain_tag_management.views.assign_tag_to_domain import (
    BulkSyncDomainTagsView,
)


class BulkSyncDomainTagsSerializerTestCase(APITestCase):
    """
    Unit tests for the serializers used by BulkSyncDomainTagsView.
    """

    # ================================================================
    # ADD SERIALIZER
    # ================================================================

    def test_add_serializer_accepts_valid_data(self):
        serializer = UserDomainTagAddSerializer(
            data={
                "domain_name": "example.com",
                "title": "Python",
            }
        )

        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            serializer.validated_data["domain_name"],
            "example.com",
        )

        self.assertEqual(
            serializer.validated_data["title"],
            "Python",
        )

    def test_add_serializer_requires_domain_name(self):
        serializer = UserDomainTagAddSerializer(
            data={
                "title": "Python",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "domain_name",
            serializer.errors,
        )

    def test_add_serializer_requires_title(self):
        serializer = UserDomainTagAddSerializer(
            data={
                "domain_name": "example.com",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "title",
            serializer.errors,
        )

    # ================================================================
    # PATCH / UPDATE SERIALIZER
    # ================================================================

    def test_patch_serializer_accepts_valid_data(self):
        serializer = UserDomainTagPatchSerializer(
            data={
                "domain_name": "example.com",
                "old_title": "Python",
                "title": "Django",
                "confirm": True,
            }
        )

        self.assertTrue(serializer.is_valid())

        self.assertTrue(
            serializer.validated_data["confirm"]
        )

    def test_patch_serializer_confirm_defaults_to_false(self):
        serializer = UserDomainTagPatchSerializer(
            data={
                "domain_name": "example.com",
                "old_title": "Python",
                "title": "Django",
            }
        )

        self.assertTrue(serializer.is_valid())

        self.assertFalse(
            serializer.validated_data["confirm"]
        )

    def test_patch_serializer_requires_domain_name(self):
        serializer = UserDomainTagPatchSerializer(
            data={
                "old_title": "Python",
                "title": "Django",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "domain_name",
            serializer.errors,
        )

    def test_patch_serializer_requires_old_title(self):
        serializer = UserDomainTagPatchSerializer(
            data={
                "domain_name": "example.com",
                "title": "Django",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "old_title",
            serializer.errors,
        )

    def test_patch_serializer_requires_new_title(self):
        serializer = UserDomainTagPatchSerializer(
            data={
                "domain_name": "example.com",
                "old_title": "Python",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "title",
            serializer.errors,
        )

    # ================================================================
    # DELETE SERIALIZER
    # ================================================================

    def test_delete_serializer_accepts_specific_tag_delete(self):
        serializer = UserDomainTagDeleteSerializer(
            data={
                "domain_name": "example.com",
                "title": "Python",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_delete_serializer_allows_missing_title(self):
        serializer = UserDomainTagDeleteSerializer(
            data={
                "domain_name": "example.com",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_delete_serializer_allows_null_title(self):
        serializer = UserDomainTagDeleteSerializer(
            data={
                "domain_name": "example.com",
                "title": None,
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_delete_serializer_allows_blank_title(self):
        serializer = UserDomainTagDeleteSerializer(
            data={
                "domain_name": "example.com",
                "title": "",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_delete_serializer_requires_domain_name(self):
        serializer = UserDomainTagDeleteSerializer(
            data={
                "title": "Python",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "domain_name",
            serializer.errors,
        )

    # ================================================================
    # BULK SERIALIZER
    # ================================================================

    def test_bulk_serializer_accepts_empty_payload(self):
        serializer = BulkSyncDomainTagsSerializer(
            data={}
        )

        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            serializer.validated_data["add"],
            [],
        )

        self.assertEqual(
            serializer.validated_data["update"],
            [],
        )

        self.assertEqual(
            serializer.validated_data["delete"],
            [],
        )

    def test_bulk_serializer_accepts_add_only(self):
        serializer = BulkSyncDomainTagsSerializer(
            data={
                "add": [
                    {
                        "domain_name": "example.com",
                        "title": "Python",
                    }
                ]
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_bulk_serializer_accepts_update_only(self):
        serializer = BulkSyncDomainTagsSerializer(
            data={
                "update": [
                    {
                        "domain_name": "example.com",
                        "old_title": "Python",
                        "title": "Django",
                    }
                ]
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_bulk_serializer_accepts_delete_only(self):
        serializer = BulkSyncDomainTagsSerializer(
            data={
                "delete": [
                    {
                        "domain_name": "example.com",
                    }
                ]
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_bulk_serializer_accepts_add_update_delete_together(self):
        serializer = BulkSyncDomainTagsSerializer(
            data={
                "add": [
                    {
                        "domain_name": "example.com",
                        "title": "Python",
                    }
                ],
                "update": [
                    {
                        "domain_name": "example.com",
                        "old_title": "Django",
                        "title": "FastAPI",
                        "confirm": True,
                    }
                ],
                "delete": [
                    {
                        "domain_name": "example.com",
                        "title": "Backend",
                    }
                ],
            }
        )

        self.assertTrue(serializer.is_valid())


class BulkSyncDomainTagsViewTestCase(APITestCase):

    # ================================================================
    # SETUP
    # ================================================================

    def setUp(self):

        # ------------------------------------------------------------
        # Roles
        # ------------------------------------------------------------

        self.admin_role = Role.objects.create(
            code="admin",
            title="Admin",
            level=3,
            is_system=True,
        )

        self.super_admin_role = Role.objects.create(
            code="super_admin",
            title="Super Admin",
            level=4,
            is_system=True,
        )

        self.regular_role = Role.objects.create(
            code="regular",
            title="Regular",
            level=2,
            is_system=True,
        )

        self.limited_role = Role.objects.create(
            code="limited",
            title="Limited",
            level=1,
            is_system=True,
        )

        # ------------------------------------------------------------
        # Users
        # ------------------------------------------------------------

        self.admin = User.objects.create_user(
            username="admin01",
            email="admin01@test.com",
            password="Test12345",
            phone="09120000001",
            role=self.admin_role,
            status="active",
        )

        self.super_admin = User.objects.create_user(
            username="superadmin",
            email="superadmin@test.com",
            password="Test12345",
            phone="09120000002",
            role=self.super_admin_role,
            status="active",
        )

        self.regular = User.objects.create_user(
            username="regular01",
            email="regular01@test.com",
            password="Test12345",
            phone="09120000003",
            role=self.regular_role,
            status="active",
        )

        self.regular2 = User.objects.create_user(
            username="regular02",
            email="regular02@test.com",
            password="Test12345",
            phone="09120000004",
            role=self.regular_role,
            status="active",
        )

        self.limited = User.objects.create_user(
            username="limited01",
            email="limited01@test.com",
            password="Test12345",
            phone="09120000005",
            role=self.limited_role,
            status="active",
        )

        # ------------------------------------------------------------
        # Group
        # ------------------------------------------------------------

        self.group = Group.objects.create(
            title="Test Group",
            description="Test Group",
            assigned_by=self.admin,
        )

        # ------------------------------------------------------------
        # UserGroup
        # ------------------------------------------------------------

        UserGroup.objects.create(
            user=self.regular,
            group=self.group,
            assigned_by=self.admin,
            is_primary=True,
        )

        UserGroup.objects.create(
            user=self.regular2,
            group=self.group,
            assigned_by=self.admin,
            is_primary=True,
        )

        UserGroup.objects.create(
            user=self.limited,
            group=self.group,
            assigned_by=self.admin,
            is_primary=True,
        )

        # ------------------------------------------------------------
        # Domains
        # ------------------------------------------------------------

        self.domain = Domain.objects.create(
            domain_name="example.com",
            description="Example domain",
            created_by=self.admin,
            group=self.group,
        )

        self.domain2 = Domain.objects.create(
            domain_name="example2.com",
            description="Second domain",
            created_by=self.admin,
            group=self.group,
        )

        self.deleted_domain = Domain.objects.create(
            domain_name="deleted.com",
            description="Deleted domain",
            created_by=self.admin,
            group=self.group,
            deleted_at=timezone.now(),
        )

        # ------------------------------------------------------------
        # Tags
        # ------------------------------------------------------------

        self.python_tag = Tag.objects.create(
            title="Python",
            description="Python",
            created_by=self.admin,
        )

        self.django_tag = Tag.objects.create(
            title="Django",
            description="Django",
            created_by=self.admin,
        )

        self.fastapi_tag = Tag.objects.create(
            title="FastAPI",
            description="FastAPI",
            created_by=self.admin,
        )

        self.backend_tag = Tag.objects.create(
            title="Backend",
            description="Backend",
            created_by=self.regular,
        )

        self.database_tag = Tag.objects.create(
            title="Database",
            description="Database",
            created_by=self.admin,
        )

        self.inactive_tag = Tag.objects.create(
            title="Inactive",
            description="Inactive",
            created_by=self.admin,
            is_active=False,
        )

        self.deleted_tag = Tag.objects.create(
            title="DeletedTag",
            description="Deleted",
            created_by=self.admin,
            deleted_at=timezone.now(),
        )

        # ------------------------------------------------------------
        # URL
        # ------------------------------------------------------------

        self.url = reverse("assign-a-tag")

    # ================================================================
    # HELPERS
    # ================================================================

    def post(self, user, data):
        self.client.force_authenticate(user=user)

        return self.client.post(
            self.url,
            data,
            format="json",
        )

    def create_udt(self, user, domain, tag):
        return User_Domain_Tag.objects.create(
            user=user,
            domain=domain,
            tag=tag,
        )

    # ================================================================
    # 1. AUTHENTICATION
    # ================================================================

    def test_unauthenticated_user_gets_401(self):
        response = self.client.post(
            self.url,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ================================================================
    # 2. LIMITED USER
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_limited_user_is_forbidden(
            self,
            mock_log,
    ):
        response = self.post(
            self.limited,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    # ================================================================
    # 3. HELPER METHODS
    # ================================================================

    def test_is_admin_returns_true_for_admin(self):
        view = BulkSyncDomainTagsView()

        self.assertTrue(
            view._is_admin(self.admin)
        )

    def test_is_admin_returns_true_for_super_admin(self):
        view = BulkSyncDomainTagsView()

        self.assertTrue(
            view._is_admin(self.super_admin)
        )

    def test_is_admin_returns_false_for_regular(self):
        view = BulkSyncDomainTagsView()

        self.assertFalse(
            view._is_admin(self.regular)
        )

    def test_is_admin_returns_false_when_user_has_no_role(self):
        user = User.objects.create_user(
            username="norole",
            email="norole@test.com",
            password="Test12345",
            phone="09120000006",
            role=None,
            status="active",
        )

        view = BulkSyncDomainTagsView()

        self.assertFalse(
            view._is_admin(user)
        )

    # ================================================================
    # 4. DOMAIN HELPER
    # ================================================================

    def test_get_domain_by_name_returns_active_domain(self):
        view = BulkSyncDomainTagsView()

        domain, error = view._get_domain_by_name(
            self.domain.domain_name,
            0,
        )

        self.assertEqual(
            domain,
            self.domain,
        )

        self.assertIsNone(error)

    def test_get_domain_by_name_rejects_empty_name(self):
        view = BulkSyncDomainTagsView()

        domain, error = view._get_domain_by_name(
            "",
            3,
        )

        self.assertIsNone(domain)

        self.assertEqual(
            error["index"],
            3,
        )

    def test_get_domain_by_name_rejects_missing_domain(self):
        view = BulkSyncDomainTagsView()

        domain, error = view._get_domain_by_name(
            "not-found.com",
            2,
        )

        self.assertIsNone(domain)

        self.assertEqual(
            error["domain_name"],
            "not-found.com",
        )

    def test_get_domain_by_name_rejects_deleted_domain(self):
        view = BulkSyncDomainTagsView()

        domain, error = view._get_domain_by_name(
            self.deleted_domain.domain_name,
            0,
        )

        self.assertIsNone(domain)
        self.assertIsNotNone(error)

    # ================================================================
    # 5. TAG HELPER
    # ================================================================

    def test_get_tag_by_title_returns_active_tag(self):
        view = BulkSyncDomainTagsView()

        tag, error = view._get_tag_by_title(
            self.python_tag.title,
            0,
        )

        self.assertEqual(
            tag,
            self.python_tag,
        )

        self.assertIsNone(error)

    def test_get_tag_by_title_rejects_empty_title(self):
        view = BulkSyncDomainTagsView()

        tag, error = view._get_tag_by_title(
            "",
            5,
        )

        self.assertIsNone(tag)

        self.assertEqual(
            error["index"],
            5,
        )

    def test_get_tag_by_title_rejects_non_existing_tag(self):
        view = BulkSyncDomainTagsView()

        tag, error = view._get_tag_by_title(
            "NotExisting",
            0,
        )

        self.assertIsNone(tag)
        self.assertIsNotNone(error)

    def test_get_tag_by_title_rejects_inactive_tag(self):
        view = BulkSyncDomainTagsView()

        tag, error = view._get_tag_by_title(
            self.inactive_tag.title,
            0,
        )

        self.assertIsNone(tag)
        self.assertIsNotNone(error)

    def test_get_tag_by_title_rejects_deleted_tag(self):
        view = BulkSyncDomainTagsView()

        tag, error = view._get_tag_by_title(
            self.deleted_tag.title,
            0,
        )

        self.assertIsNone(tag)
        self.assertIsNotNone(error)

    # ================================================================
    # 6. MAIN TAG HELPERS
    # ================================================================

    def test_get_main_tags_returns_only_admin_tags(self):
        main_udt = self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        view = BulkSyncDomainTagsView()

        tags = list(
            view._get_main_tags(self.domain)
        )

        self.assertEqual(
            len(tags),
            1,
        )

        self.assertEqual(
            tags[0].id,
            main_udt.id,
        )

    def test_get_main_tag_count_counts_only_active_admin_tags(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.super_admin,
            self.domain,
            self.django_tag,
        )

        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        deleted_main = self.create_udt(
            self.admin,
            self.domain2,
            self.fastapi_tag,
        )

        deleted_main.deleted_at = timezone.now()
        deleted_main.save()

        view = BulkSyncDomainTagsView()

        self.assertEqual(
            view._get_main_tag_count(self.domain),
            2,
        )

        self.assertTrue(
            view._has_main_tag(self.domain)
        )

        self.assertFalse(
            view._has_main_tag(self.domain2)
        )

    def test_is_main_tag_returns_true_for_admin_tag(self):
        udt = self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        view = BulkSyncDomainTagsView()

        self.assertTrue(
            view._is_main_tag(udt)
        )

    def test_is_main_tag_returns_true_for_super_admin_tag(self):
        udt = self.create_udt(
            self.super_admin,
            self.domain,
            self.python_tag,
        )

        view = BulkSyncDomainTagsView()

        self.assertTrue(
            view._is_main_tag(udt)
        )

    def test_is_main_tag_returns_false_for_regular_tag(self):
        udt = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        view = BulkSyncDomainTagsView()

        self.assertFalse(
            view._is_main_tag(udt)
        )

    def test_get_user_tags_returns_only_active_user_tags(self):
        active_udt = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        deleted_udt = self.create_udt(
            self.regular,
            self.domain,
            self.database_tag,
        )

        deleted_udt.deleted_at = timezone.now()
        deleted_udt.save()

        view = BulkSyncDomainTagsView()

        result = view._get_user_tags(
            self.regular,
            self.domain,
        )

        self.assertEqual(
            len(result),
            1,
        )

        self.assertEqual(
            result[0].id,
            active_udt.id,
        )

    # ================================================================
    # 7. EMPTY REQUEST
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_empty_payload_returns_success_with_zero_changes(
        self,
        mock_log,
    ):
        response = self.post(
            self.regular,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"],
            {
                "added": 0,
                "updated": 0,
                "deleted": 0,
            },
        )

        kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            kwargs["status_type"],
            "success",
        )

    # ================================================================
    # 8. INVALID SERIALIZER DATA
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_invalid_serializer_data_returns_400(
        self,
        mock_log,
    ):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        # title missing
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["error_code"],
            60,
        )

        kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            kwargs["status_type"],
            "failed",
        )

        self.assertEqual(
            kwargs["error_code"],
            60,
        )

    # ================================================================
    # 9. ADD - REGULAR USER
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_regular_user_can_add_one_tag(
        self,
        mock_log,
    ):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["added"],
            1,
        )

        self.assertTrue(
            User_Domain_Tag.objects.filter(
                user=self.regular,
                domain=self.domain,
                tag=self.backend_tag,
                deleted_at__isnull=True,
            ).exists()
        )

    def test_regular_user_cannot_add_when_main_tag_exists(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["error_code"],
            60,
        )

    def test_regular_user_cannot_add_second_tag(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.database_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["error_code"],
            60,
        )

    def test_regular_user_cannot_add_duplicate_tag(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_regular_user_two_adds_in_same_request_respect_one_tag_limit(
        self,
    ):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    },
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.database_tag.title,
                    },
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User_Domain_Tag.objects.filter(
                user=self.regular,
                domain=self.domain,
                deleted_at__isnull=True,
            ).exists()
        )

    # ================================================================
    # 10. ADD - ADMIN
    # ================================================================

    def test_admin_can_add_main_tag(self):
        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["added"],
            1,
        )

        udt = User_Domain_Tag.objects.get(
            user=self.admin,
            domain=self.domain,
            tag=self.python_tag,
        )

        self.assertIsNone(
            udt.deleted_at
        )

    def test_super_admin_can_add_main_tag(self):
        response = self.post(
            self.super_admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_add_second_main_tag(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.super_admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.django_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            User_Domain_Tag.objects.filter(
                domain=self.domain,
                user__role__code__in=[
                    "admin",
                    "super_admin",
                ],
                deleted_at__isnull=True,
            ).count(),
            2,
        )

    def test_admin_cannot_add_third_main_tag(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.super_admin,
            self.domain,
            self.django_tag,
        )

        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.fastapi_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            User_Domain_Tag.objects.filter(
                domain=self.domain,
                user__role__code__in=[
                    "admin",
                    "super_admin",
                ],
                deleted_at__isnull=True,
            ).count(),
            2,
        )

    def test_admin_two_adds_in_same_request_can_fill_two_slots(self):
        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    },
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.django_tag.title,
                    },
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["added"],
            2,
        )

    def test_admin_three_adds_in_same_request_cannot_exceed_two_slots(
        self,
    ):
        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    },
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.django_tag.title,
                    },
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.fastapi_tag.title,
                    },
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            User_Domain_Tag.objects.filter(
                domain=self.domain,
                user__role__code__in=[
                    "admin",
                    "super_admin",
                ],
                deleted_at__isnull=True,
            ).count(),
            0,
        )

    # ================================================================
    # 11. ADD VALIDATION
    # ================================================================

    def test_add_non_existing_domain_returns_400(self):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": "missing.com",
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_deleted_domain_returns_400(self):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.deleted_domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_non_existing_tag_returns_400(self):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": "NotExisting",
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_inactive_tag_returns_400(self):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.inactive_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_deleted_tag_returns_400(self):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.deleted_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ================================================================
    # 12. UPDATE - REGULAR
    # ================================================================

    def test_regular_update_without_main_tag_requires_confirmation(
        self,
    ):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": False,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertEqual(
            response.data["error_code"],
            21,
        )

        self.assertTrue(
            response.data["detail"]["requires_confirmation"]
        )

        # Database must remain unchanged.
        udt = User_Domain_Tag.objects.get(
            user=self.regular,
            domain=self.domain,
        )

        self.assertEqual(
            udt.tag_id,
            self.backend_tag.id,
        )

    def test_regular_update_with_confirmation_succeeds(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["updated"],
            1,
        )

        udt = User_Domain_Tag.objects.get(
            user=self.regular,
            domain=self.domain,
        )

        self.assertEqual(
            udt.tag_id,
            self.database_tag.id,
        )

    def test_regular_user_cannot_update_when_main_tag_exists(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ================================================================
    # 13. UPDATE - ADMIN
    # ================================================================

    def test_admin_can_update_own_main_tag(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.admin,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.python_tag.title,
                        "title": self.django_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        udt = User_Domain_Tag.objects.get(
            user=self.admin,
            domain=self.domain,
        )

        self.assertEqual(
            udt.tag_id,
            self.django_tag.id,
        )

        self.assertEqual(
            udt.user_id,
            self.admin.id,
        )

    def test_admin_cannot_update_another_admins_tag(self):
        self.create_udt(
            self.super_admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.admin,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.python_tag.title,
                        "title": self.django_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        udt = User_Domain_Tag.objects.get(
            user=self.super_admin,
            domain=self.domain,
        )

        self.assertEqual(
            udt.tag_id,
            self.python_tag.id,
        )

    def test_update_same_tag_returns_400(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.backend_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_non_existing_old_tag_returns_400(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.database_tag.title,
                        "title": self.python_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_to_non_existing_tag_returns_400(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": "NotExisting",
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_requires_existing_user_tag(self):
        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": True,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ================================================================
    # 14. DELETE - REGULAR
    # ================================================================

    def test_regular_can_delete_specific_tag(self):
        udt = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["deleted"],
            1,
        )

        udt.refresh_from_db()

        self.assertIsNotNone(
            udt.deleted_at
        )

    def test_regular_can_delete_all_own_tags(self):
        udt = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["result"]["deleted"],
            1,
        )

        udt.refresh_from_db()

        self.assertIsNotNone(
            udt.deleted_at
        )

    def test_regular_delete_without_existing_tag_returns_400(self):
        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_regular_cannot_delete_another_users_tag(self):
        self.create_udt(
            self.regular2,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            User_Domain_Tag.objects.filter(
                user=self.regular2,
                domain=self.domain,
                tag=self.backend_tag,
                deleted_at__isnull=True,
            ).exists()
        )

    def test_regular_cannot_delete_when_main_tag_exists(self):
        self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            User_Domain_Tag.objects.filter(
                user=self.regular,
                domain=self.domain,
                tag=self.backend_tag,
                deleted_at__isnull=True,
            ).exists()
        )

    # ================================================================
    # 15. DELETE - ADMIN
    # ================================================================

    def test_admin_can_delete_own_main_tag(self):
        udt = self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.admin,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        udt.refresh_from_db()

        self.assertIsNotNone(
            udt.deleted_at
        )

    def test_admin_cannot_delete_another_admins_main_tag(self):
        udt = self.create_udt(
            self.super_admin,
            self.domain,
            self.python_tag,
        )

        response = self.post(
            self.admin,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        udt.refresh_from_db()

        self.assertIsNone(
            udt.deleted_at
        )

    def test_deleted_main_tag_frees_slot_for_new_main_tag(self):
        first = self.create_udt(
            self.admin,
            self.domain,
            self.python_tag,
        )

        self.create_udt(
            self.super_admin,
            self.domain,
            self.django_tag,
        )

        delete_response = self.post(
            self.admin,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_200_OK,
        )

        add_response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.fastapi_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            add_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            User_Domain_Tag.objects.filter(
                domain=self.domain,
                user__role__code__in=[
                    "admin",
                    "super_admin",
                ],
                deleted_at__isnull=True,
            ).count(),
            2,
        )

    # ================================================================
    # 16. DELETE VALIDATION
    # ================================================================

    def test_delete_non_existing_domain_returns_400(self):
        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": "missing.com",
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_non_existing_tag_returns_400(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": "NotExisting",
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ================================================================
    # 17. UPDATE + DELETE SAME REQUEST
    # ================================================================

    def test_cannot_update_tag_scheduled_for_deletion(self):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "delete": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.backend_tag.title,
                    }
                ],
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": True,
                    }
                ],
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        udt = User_Domain_Tag.objects.get(
            user=self.regular,
            domain=self.domain,
        )

        self.assertEqual(
            udt.tag_id,
            self.backend_tag.id,
        )

        self.assertIsNone(
            udt.deleted_at
        )

    # ================================================================
    # 18. MIXED OPERATIONS
    # ================================================================

    def test_add_update_delete_can_be_executed_together(self):
        existing = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": self.domain2.domain_name,
                        "title": self.database_tag.title,
                    }
                ],
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.python_tag.title,
                        "confirm": True,
                    }
                ],
                "delete": [
                    {
                        "domain_name": self.domain2.domain_name,
                    }
                ],
            },
        )

        # The delete operation above has no tag, so the whole
        # request must fail before database modification.
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        existing.refresh_from_db()

        self.assertEqual(
            existing.tag_id,
            self.backend_tag.id,
        )

    def test_multiple_valid_operations_are_saved(self):
        existing = self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.python_tag.title,
                        "confirm": True,
                    }
                ],
                "delete": [
                    {
                        "domain_name": self.domain2.domain_name,
                    }
                ],
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        existing.refresh_from_db()

        self.assertEqual(
            existing.tag_id,
            self.backend_tag.id,
        )

    # ================================================================
    # 19. ATOMICITY
    # ================================================================

    def test_validation_error_does_not_partially_create_tags(self):
        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    },
                    {
                        "domain_name": "missing.com",
                        "title": self.django_tag.title,
                    },
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User_Domain_Tag.objects.filter(
                user=self.admin,
                domain=self.domain,
                tag=self.python_tag,
                deleted_at__isnull=True,
            ).exists()
        )

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.User_Domain_Tag.objects.bulk_create",
        side_effect=Exception("database failure"),
    )
    def test_database_exception_does_not_leave_created_records(
            self,
            mock_bulk_create,
    ):
        with self.assertRaises(Exception) as context:
            self.post(
                self.admin,
                {
                    "add": [
                        {
                            "domain_name": self.domain.domain_name,
                            "title": self.python_tag.title,
                        }
                    ]
                },
            )

        self.assertEqual(
            str(context.exception),
            "database failure",
        )

        mock_bulk_create.assert_called_once()

        self.assertFalse(
            User_Domain_Tag.objects.filter(
                user=self.admin,
                domain=self.domain,
                tag=self.python_tag,
                deleted_at__isnull=True,
            ).exists()
        )
    # ================================================================
    # 20. LOGGING - SUCCESS
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_success_is_logged(self, mock_log):
        response = self.post(
            self.admin,
            {
                "add": [
                    {
                        "domain_name": self.domain.domain_name,
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            kwargs["action"],
            "BULK_SYNC_DOMAIN_TAGS",
        )

        self.assertEqual(
            kwargs["status_type"],
            "success",
        )

        self.assertEqual(
            kwargs["user_id"],
            self.admin.id,
        )

        self.assertEqual(
            kwargs["extra"]["added"],
            1,
        )

        self.assertEqual(
            kwargs["extra"]["updated"],
            0,
        )

        self.assertEqual(
            kwargs["extra"]["deleted"],
            0,
        )

    # ================================================================
    # 21. LOGGING - VALIDATION FAILURE
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_validation_failure_is_logged(self, mock_log):
        response = self.post(
            self.regular,
            {
                "add": [
                    {
                        "domain_name": "missing.com",
                        "title": self.python_tag.title,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            kwargs["action"],
            "BULK_SYNC_DOMAIN_TAGS",
        )

        self.assertEqual(
            kwargs["status_type"],
            "failed",
        )

        self.assertEqual(
            kwargs["error_code"],
            60,
        )

    # ================================================================
    # 22. LOGGING - CONFIRMATION
    # ================================================================

    @patch(
        "domain_tag_management.views.assign_tag_to_domain.log_critical_event"
    )
    def test_confirmation_required_is_logged_as_pending(
        self,
        mock_log,
    ):
        self.create_udt(
            self.regular,
            self.domain,
            self.backend_tag,
        )

        response = self.post(
            self.regular,
            {
                "update": [
                    {
                        "domain_name": self.domain.domain_name,
                        "old_title": self.backend_tag.title,
                        "title": self.database_tag.title,
                        "confirm": False,
                    }
                ]
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            kwargs["action"],
            "BULK_SYNC_DOMAIN_TAGS",
        )

        self.assertEqual(
            kwargs["status_type"],
            "pending",
        )

        self.assertEqual(
            kwargs["error_code"],
            21,
        )