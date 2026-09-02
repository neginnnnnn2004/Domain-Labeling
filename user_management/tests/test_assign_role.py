from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
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
            title='کاربر محدود شده ',
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
        self.limited_user = User.objects.create_user(
            username="limited_user",
            password="password123",
            email="limited@test.com",
            phone="09555555555",
            status="active",
            role=self.limited_role
        )
        # soft-deleted user, used for the "not found" scenario
        self.deleted_user = User.objects.create_user(
            username="deleted_user",
            password="password123",
            email="deleted@test.com",
            phone="09666666666",
            status="active",
            role=self.regular_role,
        )
        self.deleted_user.deleted_at = timezone.now()
        self.deleted_user.save()

    # ---------------------------------------------------------------
    # Permission / authentication
    # ---------------------------------------------------------------

    def test_unauthenticated_user_can_not_assign_role_to_user(self):
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_can_not_assign_role_to_user(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_not_assign_role_to_user(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_assign_role_to_user(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------------
    # Happy path
    # ---------------------------------------------------------------

    def test_super_admin_user_can_assign_role_to_user1(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check JSON response
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(
            response.data['message'],
            "User role updated successfully / نقش کاربر با موفقیت بروزرسانی شد."
        )

        # verifying that the change was actually applied to the database
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role.id, self.regular_role.id)
        self.assertEqual(self.target_user.role, self.regular_role)

    def test_super_admin_user_can_assign_role_to_user2(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.limited_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')

        # check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check JSON response
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(
            response.data['message'],
            "User role updated successfully / نقش کاربر با موفقیت بروزرسانی شد."
        )

        # verifying that the change was actually applied to the database
        self.limited_user.refresh_from_db()
        self.assertEqual(self.limited_user.role.id, self.regular_role.id)
        self.assertEqual(self.limited_user.role, self.regular_role)

    def test_super_admin_can_change_role_from_none_to_a_role(self):
        # target_user is created without a role in setUp -> covers the
        # "old_role is None" branch inside the view/log_critical_event call
        self.assertIsNone(self.target_user.role)

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.limited_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, self.limited_role)

    # ---------------------------------------------------------------
    # 404 - user not found / soft deleted (error_code 40)
    # ---------------------------------------------------------------

    def test_user_not_found(self):
        self.client.force_authenticate(user=self.super_admin_user)
        # build a pk that is guaranteed not to exist, instead of a hardcoded number
        non_existent_pk = User.objects.order_by('-pk').first().pk + 1
        url = reverse('assign-users-role', kwargs={'pk': non_existent_pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 40)

    def test_soft_deleted_user_is_treated_as_not_found(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.deleted_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 40)

        # make sure the soft-deleted user's role was NOT changed
        self.deleted_user.refresh_from_db()
        self.assertEqual(self.deleted_user.role, self.regular_role)

    # ---------------------------------------------------------------
    # 400 - self role change (error_code 10)
    # ---------------------------------------------------------------

    def test_user_can_not_change_their_role(self):
        # Must be authenticated as a super admin, otherwise the permission
        # check (403) fires before the self-role-change check ever runs.
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.super_admin_user.pk})
        data = {'role': self.limited_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

        # role must remain unchanged
        self.super_admin_user.refresh_from_db()
        self.assertEqual(self.super_admin_user.role, self.super_admin_role)

    # ---------------------------------------------------------------
    # 400 - invalid payload (error_code 10)
    # ---------------------------------------------------------------

    def test_invalid_payload_role_with_wrong_type(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})

        data = {'role': 'this-is-not-a-valid-role-id'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)
        self.assertIn('detail', response.data)

        self.target_user.refresh_from_db()
        self.assertIsNone(self.target_user.role)

    def test_invalid_payload_role_does_not_exist(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        non_existent_role_id = Role.objects.order_by('-pk').first().pk + 1
        data = {'role': non_existent_role_id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

        # role must remain unchanged
        self.target_user.refresh_from_db()
        self.assertIsNone(self.target_user.role)

    # ---------------------------------------------------------------
    # 500 - unexpected exception
    # ---------------------------------------------------------------

    @patch('user_management.serializers.assign_role.UserRoleUpdateSerializer.save')
    def test_unexpected_exception_returns_500(self, mock_save):
        mock_save.side_effect = Exception('boom')

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.target_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.data)

        # role must remain unchanged since save() blew up
        self.target_user.refresh_from_db()
        self.assertIsNone(self.target_user.role)

    # ---------------------------------------------------------------
    # log_critical_event calls (behavioural check, not just status codes)
    # ---------------------------------------------------------------

    @patch('user_management.views.assign_role.log_critical_event')
    def test_success_logs_old_and_new_role(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('assign-users-role', kwargs={'pk': self.limited_user.pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_log.assert_called_once()
        call_kwargs = mock_log.call_args.kwargs
        self.assertEqual(call_kwargs['action'], 'change_user_role')
        self.assertEqual(call_kwargs['status_type'], 'success')
        self.assertEqual(call_kwargs['extra']['old_role']['id'], self.limited_role.id)
        self.assertEqual(call_kwargs['extra']['new_role']['id'], self.regular_role.id)

    @patch('user_management.views.assign_role.log_critical_event')
    def test_user_not_found_logs_error_code(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        non_existent_pk = User.objects.order_by('-pk').first().pk + 1
        url = reverse('assign-users-role', kwargs={'pk': non_existent_pk})
        data = {'role': self.regular_role.id}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        mock_log.assert_called_once()
        call_kwargs = mock_log.call_args.kwargs
        self.assertEqual(call_kwargs['error_code'], 'USER_NOT_FOUND')
