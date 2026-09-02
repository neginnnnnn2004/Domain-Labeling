from unittest import mock

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role
from django.urls import reverse

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

        self.none_role_user = User.objects.create_user(
            username="none_role_user",
            password="password123",
            email="none_role@test.com",
            phone="09666666666",
            status="active",
            role=None
        )

#########################
# Manage User Status
#########################

    def test_super_admin_can_change_user_status(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()

        self.assertEqual(self.target_user.status,'active')


    def test_admin_can_not_change_user_status(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_regular_user_can_not_change_user_status(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}


        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_none_role_user_can_not_change_user_status(self):
        self.client.force_authenticate(user=self.none_role_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}


        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_change_user_status(self):

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unverified_admin_can_not_change_user_status(self):
        self.admin_user.status = 'unverified'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_pending_admin_can_not_change_user_status(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'pending'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_suspended_admin_can_not_change_user_status(self):
        self.admin_user.status = 'suspended'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleted_admin_can_not_change_user_status(self):
        self.admin_user.status = 'deleted'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


###############################
    def test_super_admin_can_not_change_status_with_invalid_value(self):
        self.client.force_authenticate(user=self.super_admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'invalid_status'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_change_status_for_non_existing_user(self):
        self.client.force_authenticate(user=self.super_admin_user)

        url = reverse('manage-user-status', kwargs={'pk': 9999})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    #########################
    # Soft Delete User
    #########################

    def test_super_admin_can_soft_delete_user(self):
        self.client.force_authenticate(user=self.super_admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


        self.target_user.refresh_from_db()

        self.assertIsNotNone(self.target_user.deleted_at)

        self.assertEqual(self.target_user.status,'deleted')


    def test_admin_can_not_soft_delete_user(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)


    def test_regular_user_can_not_soft_delete_user(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)


    def test_unauthenticated_user_can_not_soft_delete_user(self):
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)


    def test_soft_delete_non_existing_user(self):
        self.client.force_authenticate(user=self.super_admin_user)

        url = reverse('manage-user-status', kwargs={'pk': 9999})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    # ---------------------------------------------------------
    # Manage Status
    # When soft_deleted user not found
    # ---------------------------------------------------------

    def test_change_status_for_already_soft_deleted_user(self):
        self.target_user.deleted_at = timezone.now()
        self.target_user.status = 'deleted'
        self.target_user.save()

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 40)

    # ---------------------------------------------------------
    # Manage Status
    # Check error code
    # ---------------------------------------------------------

    def test_invalid_status_returns_error_code_10(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'invalid_status'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['error_code'], 10)

    def test_not_found_returns_error_code_40(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': 9999})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['error_code'], 40)

    # ---------------------------------------------------------
    # Manage Status — logging
    # ---------------------------------------------------------

    @mock.patch('user_management.views.manage_status.log_critical_event')
    def test_change_status_success_logs_old_and_new_status(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        self.client.patch(url, data, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'change_user_status')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['old_status'], 'pending')
        self.assertEqual(kwargs['extra']['new_status'], 'active')

    @mock.patch('user_management.views.manage_status.log_critical_event')
    def test_change_status_not_found_logs_error(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': 9999})
        data = {'status': 'active'}

        self.client.patch(url, data, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 'USER_NOT_FOUND')
        self.assertEqual(kwargs['extra']['target_user_id'], 9999)

    @mock.patch('user_management.views.manage_status.log_critical_event')
    def test_change_status_invalid_logs_error(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'garbage'}

        self.client.patch(url, data, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 'INVALID_STATUS')
        self.assertEqual(kwargs['extra']['requested_status'], 'garbage')

    # ---------------------------------------------------------
    # Manage Status — Exception
    # ---------------------------------------------------------

    @mock.patch('user_management.views.manage_status.log_critical_event')
    @mock.patch('user_management.views.manage_status.UserStatusUpdateSerializer')
    def test_change_status_returns_500_on_unexpected_exception(
        self, mock_serializer, mock_log
    ):
        mock_serializer.side_effect = Exception("boom")

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})
        data = {'status': 'active'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 'STATUS_CHANGE_FAILED')

    # ---------------------------------------------------------
    # Soft Delete — permission tests
    # ---------------------------------------------------------

    def test_none_role_user_can_not_soft_delete_user(self):
        self.client.force_authenticate(user=self.none_role_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_admin_can_not_soft_delete_user(self):
        self.admin_user.status = 'unverified'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_admin_can_not_soft_delete_user(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Soft Delete — idempotency
    # ---------------------------------------------------------

    def test_soft_delete_already_deleted_user_returns_404(self):
        self.target_user.deleted_at = timezone.now()
        self.target_user.status = 'deleted'
        self.target_user.save()

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 40)

    # ---------------------------------------------------------
    # Soft Delete — logging
    # ---------------------------------------------------------

    @mock.patch('user_management.views.manage_status.log_critical_event')
    def test_soft_delete_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        self.client.delete(url, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'soft_delete_user')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['target_user_id'], self.target_user.id)

    @mock.patch('user_management.views.manage_status.log_critical_event')
    def test_soft_delete_not_found_logs_error(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': 9999})

        self.client.delete(url, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 'USER_NOT_FOUND')
        self.assertEqual(kwargs['extra']['target_user_id'], 9999)

    # ---------------------------------------------------------
    # Soft Delete — Exception
    # ---------------------------------------------------------

    @mock.patch('user_management.views.manage_status.log_critical_event')
    @mock.patch('user_management.views.manage_status.timezone')
    def test_soft_delete_returns_500_on_unexpected_exception(
        self, mock_timezone, mock_log
    ):
        mock_timezone.now.side_effect = Exception("boom")

        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.delete(url, format='json')

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 'SOFT_DELETE_FAILED')

    # ---------------------------------------------------------
    # Invalid method
    # ---------------------------------------------------------

    def test_get_method_not_allowed(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('manage-user-status', kwargs={'pk': self.target_user.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)