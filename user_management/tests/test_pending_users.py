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
            level = 100 ,
            is_system = True,
        )

        self.super_admin_role = Role.objects.create(
            code='super_admin',
            title='سوپر ادمین',
            level = 999 ,
            is_system = True,
        )

        self.limited_role= Role.objects.create(
            code='limited',
            title='کاربر محدود شده ',
            level = 20 ,
            is_system = True,
        )

        self.regular_role = Role.objects.create(
            code='regular',
            title='کاربر معمولی',
            level = 20 ,
            is_system = True,
        )
        # create_user
        self.admin_user = User.objects.create(
            username="admin_dara",
            password="admin_password123",
            email="admin@test.com",
            phone="09111111111",
            status="active",
            role=self.admin_role
        )
        self.super_admin_user = User.objects.create(
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
        self.target2_user = User.objects.create_user(
            username="pending2_user",
            password="password123",
            email="target2@test.com",
            phone="09444444443",
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

        self.none_role_user = User.objects.create_user(
            username="none_role_user",
            password="password123",
            email="none_role@test.com",
            phone="09666666666",
            status="active",
            role=None
        )

        # define urls
        self.list_pending_users_url = reverse('pending-users')


    def test_admin_can_list_pending_users(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_super_admin_can_list_pending_users(self):
        self.client.force_authenticate(user=self.super_admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_regular_user_can_not_list_pending_users(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_limited_user_can_not_list_pending_users(self):
        self.client.force_authenticate(user=self.limited_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_none_role_user_can_not_list_pending_users(self):
        self.client.force_authenticate(user=self.none_role_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_Unauthenticated_user_can_not_list_pending_users(self):
        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unverified_admin_can_not_list_pending_users(self):
        self.admin_user.status = 'unverified'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_pending_admin_can_not_list_pending_users(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_suspended_admin_can_not_list_pending_users(self):
        self.admin_user.status = 'suspended'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_deleted_admin_can_not_list_pending_users(self):
        self.admin_user.status = 'deleted'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_list_pending_users_check_users(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(response.status_code,status.HTTP_200_OK)

        # for calculate the length of response use --> len()
        self.assertEqual(len(response.data),2)

        returned_username = {item['username'] for item in response.data}
        self.assertEqual(
            returned_username,
            {self.target_user.username, self.target2_user.username}
        )


    def test_non_pending_users_are_excluded(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_pending_users_url)

        returned_usernames = {item['username'] for item in response.data}
        self.assertNotIn('active_user', returned_usernames)
        self.assertNotIn('unverified_user', returned_usernames)
        self.assertNotIn('admin_dara', returned_usernames)

    def test_returns_empty_list_when_no_pending_users(self):
        # همه‌ی pendingها رو تغییر می‌دیم که هیچی pending نمونه
        self.target_user.status = 'active'
        self.target_user.save()
        self.target2_user.status = 'active'
        self.target2_user.save()

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ---------------------------------------------------------
    # Exception path
    # ---------------------------------------------------------

    @mock.patch('user_management.views.pending_users.log_critical_event')
    @mock.patch('user_management.views.pending_users.ListOfUsersSerializer')
    def test_returns_500_on_unexpected_exception(
        self, mock_serializer, mock_log_critical_event
    ):
        mock_serializer.side_effect = Exception("boom")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertIn('detail', response.data)

        mock_log_critical_event.assert_called_once()
        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'list_pending_users')
        self.assertEqual(kwargs['status_type'], 'error')
        self.assertEqual(kwargs['error_code'], 'LIST_PENDING_USERS_FAILED')

    # ---------------------------------------------------------
    # Logging on success
    # ---------------------------------------------------------

    @mock.patch('user_management.views.pending_users.log_critical_event')
    def test_success_logs_critical_event_with_correct_params(
        self, mock_log_critical_event
    ):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_pending_users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'list_pending_users')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['count'], 2)

    # ---------------------------------------------------------
    # Method not allowed
    # ---------------------------------------------------------

    def test_post_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_pending_users_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)