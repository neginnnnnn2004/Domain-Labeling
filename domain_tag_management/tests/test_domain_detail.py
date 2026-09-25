from unittest.mock import patch

from django.urls import reverse
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


class DomainDetailViewTestCase(APITestCase):

    def setUp(self):
        # ============================================================
        # Roles
        # ============================================================

        self.admin_role = Role.objects.create(
            code='admin',
            title='Admin',
            level=3,
            is_system=True
        )

        self.super_admin_role = Role.objects.create(
            code='super_admin',
            title='Super Admin',
            level=4,
            is_system=True
        )

        self.regular_role = Role.objects.create(
            code='regular',
            title='Regular',
            level=2,
            is_system=True
        )

        self.limited_role = Role.objects.create(
            code='limited',
            title='Limited',
            level=1,
            is_system=True
        )

        # ============================================================
        # Users
        # ============================================================

        self.admin = User.objects.create_user(
            username='admin01',
            email='admin@test.com',
            password='Test12345',
            phone='09120000001',
            role=self.admin_role,
            status='active',
        )

        self.super_admin = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='Test12345',
            phone='09120000002',
            role=self.super_admin_role,
            status='active',
        )

        self.regular_user = User.objects.create_user(
            username='regular01',
            email='regular@test.com',
            password='Test12345',
            phone='09120000003',
            role=self.regular_role,
            status='active',
        )

        self.limited_user = User.objects.create_user(
            username='limited01',
            email='limited@test.com',
            password='Test12345',
            phone='09120000004',
            role=self.limited_role,
            status='active',
        )

        self.other_regular_user = User.objects.create_user(
            username='regular02',
            email='regular2@test.com',
            password='Test12345',
            phone='09120000005',
            role=self.regular_role,
            status='active',
        )

        # ============================================================
        # Groups
        # ============================================================

        self.group1 = Group.objects.create(
            title='Group One',
            description='First test group',
            assigned_by=self.admin,
        )

        self.group2 = Group.objects.create(
            title='Group Two',
            description='Second test group',
            assigned_by=self.admin,
        )

        # ============================================================
        # User Groups
        # ============================================================

        UserGroup.objects.create(
            user=self.regular_user,
            group=self.group1,
            assigned_by=self.admin,
            is_primary=True,
        )

        UserGroup.objects.create(
            user=self.limited_user,
            group=self.group1,
            assigned_by=self.admin,
            is_primary=True,
        )

        UserGroup.objects.create(
            user=self.other_regular_user,
            group=self.group2,
            assigned_by=self.admin,
            is_primary=True,
        )

        # ============================================================
        # Domains
        # ============================================================

        self.group_domain = Domain.objects.create(
            domain_name='group1.com',
            description='Group 1 domain',
            created_by=self.admin,
            group=self.group1,
        )

        self.other_group_domain = Domain.objects.create(
            domain_name='group2.com',
            description='Group 2 domain',
            created_by=self.admin,
            group=self.group2,
        )

        self.ungrouped_domain = Domain.objects.create(
            domain_name='public.com',
            description='Public domain',
            created_by=self.admin,
            group=None,
        )

        self.deleted_domain = Domain.objects.create(
            domain_name='deleted.com',
            description='Deleted domain',
            created_by=self.admin,
            group=self.group1,
            deleted_at='2026-01-01T00:00:00Z',
        )

        # ============================================================
        # Tags
        # ============================================================

        self.main_tag_1 = Tag.objects.create(
            title='Python',
            description='Python tag',
            created_by=self.admin,
        )

        self.main_tag_2 = Tag.objects.create(
            title='Django',
            description='Django tag',
            created_by=self.admin,
        )

        self.regular_tag = Tag.objects.create(
            title='Backend',
            description='Backend tag',
            created_by=self.regular_user,
        )

        self.other_tag = Tag.objects.create(
            title='Database',
            description='Database tag',
            created_by=self.admin,
        )

        self.deleted_tag = Tag.objects.create(
            title='DeletedTag',
            description='Deleted tag',
            created_by=self.admin,
        )

        # ============================================================
        # URL
        # ============================================================

        self.url = lambda domain_id: reverse(
            'domain-detail',
            kwargs={'pk': domain_id}
        )

    # =================================================================
    # 1. AUTHENTICATION
    # =================================================================

    def test_unauthenticated_user_cannot_access_domain_detail(self):
        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =================================================================
    # 2. DOMAIN EXISTENCE
    # =================================================================

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_existing_domain_returns_200(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.group_domain.id
        )

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_non_existing_domain_returns_404(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(999999)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.data['error_code'],
            50
        )

        self.assertIsNone(
            response.data['detail']
        )

        mock_log.assert_called_once()

        call_kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            call_kwargs['action'],
            'DOMAIN_DETAIL'
        )

        self.assertEqual(
            call_kwargs['status_type'],
            'failed'
        )

        self.assertEqual(
            call_kwargs['error_code'],
            50
        )

        self.assertEqual(
            call_kwargs['extra']['domain_id'],
            999999
        )

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_soft_deleted_domain_returns_404(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.deleted_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.data['error_code'],
            50
        )

        call_kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            call_kwargs['action'],
            'DOMAIN_DETAIL'
        )

        self.assertEqual(
            call_kwargs['status_type'],
            'failed'
        )

        self.assertEqual(
            call_kwargs['error_code'],
            50
        )

    # =================================================================
    # 3. ADMIN / SUPER ADMIN ACCESS
    # =================================================================

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_admin_can_access_domain_from_any_group(self, mock_log):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.url(self.other_group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.other_group_domain.id
        )

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_super_admin_can_access_domain_from_any_group(self, mock_log):
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.get(
            self.url(self.other_group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.other_group_domain.id
        )

    # =================================================================
    # 4. REGULAR USER ACCESS
    # =================================================================

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_regular_user_can_access_domain_of_own_group(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_regular_user_cannot_access_domain_of_other_group(
        self,
        mock_log
    ):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.other_group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data['error_code'],
            50
        )

        self.assertIsNone(
            response.data['detail']
        )

        call_kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            call_kwargs['action'],
            'DOMAIN_DETAIL'
        )

        self.assertEqual(
            call_kwargs['status_type'],
            'failed'
        )

        self.assertEqual(
            call_kwargs['error_code'],
            50
        )

        self.assertEqual(
            call_kwargs['extra']['domain_id'],
            self.other_group_domain.id
        )

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_regular_user_can_access_ungrouped_domain(
        self,
        mock_log
    ):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.ungrouped_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_user_without_group_cannot_access_grouped_domain(self):
        user = User.objects.create_user(
            username='nogroup',
            email='nogroup@test.com',
            password='Test12345',
            phone='09120000006',
            role=self.regular_role,
            status='active',
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data['error_code'],
            50
        )

    # =================================================================
    # 5. LIMITED USER ACCESS
    # =================================================================

    def test_limited_user_can_access_domain_of_own_group(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_limited_user_cannot_access_domain_of_other_group(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(
            self.url(self.other_group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data['error_code'],
            50
        )

    def test_limited_user_can_access_ungrouped_domain(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(
            self.url(self.ungrouped_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # =================================================================
    # 6. ADMIN TAG VISIBILITY
    # =================================================================

    def test_admin_sees_all_active_domain_tags(self):
        # Main tag 1
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
        )

        # Regular user's tag
        User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.group_domain,
            tag=self.regular_tag,
        )

        # Another admin tag
        User_Domain_Tag.objects.create(
            user=self.super_admin,
            domain=self.group_domain,
            tag=self.other_tag,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_tag_ids = {
            tag['id']
            for tag in response.data['tags']
        }

        self.assertSetEqual(
            returned_tag_ids,
            {
                self.main_tag_1.id,
                self.regular_tag.id,
                self.other_tag.id,
            }
        )

    def test_admin_can_add_tag_when_less_than_two_main_tags_exist(self):
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data['can_add_tag']
        )

        self.assertTrue(
            response.data['has_main_tag']
        )

    def test_admin_cannot_add_tag_when_two_main_tags_exist(self):
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
        )

        User_Domain_Tag.objects.create(
            user=self.super_admin,
            domain=self.group_domain,
            tag=self.main_tag_2,
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            response.data['can_add_tag']
        )

        self.assertTrue(
            response.data['has_main_tag']
        )

    # =================================================================
    # 7. LIMITED USER TAG VISIBILITY
    # =================================================================

    def test_limited_user_sees_only_main_tags(self):
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
        )

        User_Domain_Tag.objects.create(
            user=self.limited_user,
            domain=self.group_domain,
            tag=self.regular_tag,
        )

        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_tag_ids = {
            tag['id']
            for tag in response.data['tags']
        }

        self.assertSetEqual(
            returned_tag_ids,
            {self.main_tag_1.id}
        )

        self.assertFalse(
            response.data['can_add_tag']
        )

        self.assertTrue(
            response.data['has_main_tag']
        )

    def test_limited_user_sees_no_tags_when_no_main_tag_exists(self):
        User_Domain_Tag.objects.create(
            user=self.limited_user,
            domain=self.group_domain,
            tag=self.regular_tag,
        )

        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['tags'],
            []
        )

        self.assertFalse(
            response.data['can_add_tag']
        )

        self.assertFalse(
            response.data['has_main_tag']
        )

    # =================================================================
    # 8. REGULAR USER TAG VISIBILITY
    # =================================================================

    def test_regular_user_with_main_tag_sees_only_main_tags(self):
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
        )

        User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.group_domain,
            tag=self.regular_tag,
        )

        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_tag_ids = {
            tag['id']
            for tag in response.data['tags']
        }

        # Because has_main_tag=True,
        # only main tags are visible.
        self.assertSetEqual(
            returned_tag_ids,
            {self.main_tag_1.id}
        )

        self.assertFalse(
            response.data['can_add_tag']
        )

        self.assertTrue(
            response.data['has_main_tag']
        )

    def test_regular_user_without_main_tag_or_own_tag_can_add_tag(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['tags'],
            []
        )

        self.assertTrue(
            response.data['can_add_tag']
        )

        self.assertFalse(
            response.data['has_main_tag']
        )

    def test_regular_user_with_own_tag_and_without_main_tag_sees_own_tag(
        self
    ):
        User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.group_domain,
            tag=self.regular_tag,
        )

        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_tag_ids = {
            tag['id']
            for tag in response.data['tags']
        }

        self.assertSetEqual(
            returned_tag_ids,
            {self.regular_tag.id}
        )

        self.assertFalse(
            response.data['can_add_tag']
        )

        self.assertFalse(
            response.data['has_main_tag']
        )

    # =================================================================
    # 9. SOFT-DELETED USER DOMAIN TAG
    # =================================================================

    def test_soft_deleted_user_domain_tag_is_not_visible(self):
        User_Domain_Tag.objects.create(
            user=self.admin,
            domain=self.group_domain,
            tag=self.main_tag_1,
            deleted_at='2026-01-01T00:00:00Z',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['tags'],
            []
        )

        self.assertFalse(
            response.data['has_main_tag']
        )

    # =================================================================
    # 10. SUCCESS LOGGING
    # =================================================================

    @patch('domain_tag_management.views.domain_detail.log_critical_event')
    def test_success_request_logs_success_event(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        mock_log.assert_called_once()

        call_kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            call_kwargs['action'],
            'DOMAIN_DETAIL'
        )

        self.assertEqual(
            call_kwargs['status_type'],
            'success'
        )

        self.assertEqual(
            call_kwargs['user_id'],
            self.regular_user.id
        )

        self.assertEqual(
            call_kwargs['extra']['domain_id'],
            self.group_domain.id
        )

    # =================================================================
    # 11. UNEXPECTED EXCEPTION
    # =================================================================

    @patch(
        'domain_tag_management.views.domain_detail.Domain.objects.get',
        side_effect=Exception('Unexpected database error')
    )
    @patch(
        'domain_tag_management.views.domain_detail.log_critical_event'
    )
    def test_unexpected_exception_returns_500(
        self,
        mock_log,
        mock_domain_get
    ):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(
            self.url(self.group_domain.id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        self.assertEqual(
            response.data['detail'],
            'An unexpected error occurred / خطای غیرمنتظره‌ای رخ داده است.'
        )

        # The unexpected exception is caught by the outer except,
        # therefore an error log must be created.
        mock_log.assert_called_once()

        call_kwargs = mock_log.call_args.kwargs

        self.assertEqual(
            call_kwargs['action'],
            'DOMAIN_DETAIL'
        )

        self.assertEqual(
            call_kwargs['status_type'],
            'error'
        )

        self.assertEqual(
            call_kwargs['error_code'],
            'DOMAIN_DETAIL_FAILED'
        )