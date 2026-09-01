from unittest import mock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role


class AdminUserManagementTest(APITestCase):

    def setUp(self):
        # create roles
        self.admin_role = Role.objects.create(
            code='admin',
            title='ادمین',
            level=100,
            is_system=True,
        )

        self.super_admin_role = Role.objects.create(
            code='super_admin',
            title='سوپر ادمین',
            level=999,
            is_system=True,
        )

        self.limited_role = Role.objects.create(
            code='limited',
            title='کاربر محدود شده',
            level=20,
            is_system=True,
        )

        self.regular_role = Role.objects.create(
            code='regular',
            title='کاربر معمولی',
            level=20,
            is_system=True,
        )

        # create_user
        self.admin_user = User.objects.create_user(
            username="admin_dara",
            password="admin_password123",
            email="admin@test.com",
            phone="09111111111",
            status="active",
            role=self.admin_role
        )
        self.super_admin_user = User.objects.create_user(
            username="super_admin_nima",
            password="super_admin_password123",
            email="superadmin@test.com",
            phone="09222222222",
            status="active",
            role=self.super_admin_role
        )
        self.regular_user = User.objects.create_user(
            username="normal_user",
            password="password123",
            email="normal@test.com",
            phone="09333333333",
            status="unverified",
            role=self.regular_role
        )
        self.target_user = User.objects.create_user(
            username="pending_user",
            password="password123",
            email="target@test.com",
            phone="09444444444",
            status="pending"
        )
        self.limited_user = User.objects.create_user(
            username="limited_user",
            password="password123",
            email="limited@test.com",
            phone="09555555555",
            status="active",
            role=self.limited_role
        )

        # define urls
        self.list_users_url = reverse('list-of-users')

    # ---------------------------------------------------------
    # Basic tests
    # ---------------------------------------------------------

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_super_admin_can_list_users(self):
        self.client.force_authenticate(user=self.super_admin_user)
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_regular_user_can_not_list_users(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_list_users(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_list_users(self):
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------------------------------------
    # Wrong Pass / Exception
    # ---------------------------------------------------------

    @mock.patch('user_management.views.list_users.log_critical_event')
    @mock.patch('user_management.views.list_users.ListOfUsersSerializer')
    def test_list_users_returns_500_on_unexpected_exception(
        self, mock_serializer, mock_log_critical_event
    ):
        mock_serializer.side_effect = Exception("boom")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_users_url)

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertIn('detail', response.data)

        mock_log_critical_event.assert_called_once()
        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'list_users')
        self.assertEqual(kwargs['status_type'], 'error')
        self.assertEqual(kwargs['error_code'], 'LIST_USERS_FAILED')
        self.assertEqual(kwargs['user_id'], self.admin_user.id)

    # ---------------------------------------------------------
    # User without role
    # ---------------------------------------------------------

    def test_user_without_role_can_not_list_users(self):
        self.client.force_authenticate(user=self.target_user)
        response = self.client.get(self.list_users_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Create log after success event with true parameters
    # ---------------------------------------------------------

    @mock.patch('user_management.views.list_users.log_critical_event')
    def test_successful_list_users_logs_critical_event_with_correct_params(
        self, mock_log_critical_event
    ):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_log_critical_event.assert_called_once()

        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'list_users')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['user_id'], self.admin_user.id)
        self.assertEqual(kwargs['extra']['username'], self.admin_user.username)
        self.assertEqual(kwargs['extra']['count'], 5)

    # ---------------------------------------------------------
    # Status states for admin-role users
    # ---------------------------------------------------------

    def test_admin_with_pending_status_can_not_list_users(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_with_unverified_status_can_not_list_users(self):
        self.admin_user.status = 'unverified'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_with_blocked_status_can_not_list_users(self):
        # If your model's actual choice isn't 'blocked' (e.g. 'suspended',
        # 'inactive', or 'banned'), replace this value with the real one.
        self.admin_user.status = 'blocked'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Status state for a regular-role user (separated from the role test)
    #
    # Here we deliberately keep the role as admin, to make sure the
    # rejection is due to status specifically, not role.
    # ---------------------------------------------------------

    def test_regular_role_active_status_still_forbidden_by_role(self):
        self.regular_user.status = 'active'
        self.regular_user.save()
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Difference between "no role" and "invalid/non-system role"
    # ---------------------------------------------------------

    def test_user_with_non_system_role_can_not_list_users(self):
        fake_role = Role.objects.create(
            code='temp_custom',
            title='نقش موقت',
            level=50,
            is_system=False,
        )
        self.target_user.role = fake_role
        self.target_user.save()
        self.client.force_authenticate(user=self.target_user)

        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Other HTTP methods on this endpoint
    # ---------------------------------------------------------

    def test_post_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_users_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)