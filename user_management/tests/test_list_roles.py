from unittest import mock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role


class ListOfRolesViewTest(APITestCase):

    def setUp(self):
        self.admin_role = Role.objects.create(
            code='admin', title='ادمین', level=100, is_system=True,
        )
        self.super_admin_role = Role.objects.create(
            code='super_admin', title='سوپر ادمین', level=999, is_system=True,
        )
        self.regular_role = Role.objects.create(
            code='regular', title='کاربر معمولی', level=20, is_system=True,
        )
        self.limited_role = Role.objects.create(
            code='limited', title='کاربر محدود شده', level=20, is_system=True,
        )

        self.admin_user = User.objects.create_user(
            username="admin_dara",
            password="admin_password123",
            email="admin@test.com",
            phone="09111111111",
            status="active",
            role=self.admin_role,
        )
        self.regular_user = User.objects.create_user(
            username="normal_user",
            password="password123",
            email="normal@test.com",
            phone="09333333333",
            status="active",
            role=self.regular_role,
        )
        self.no_role_user = User.objects.create_user(
            username="no_role_user",
            password="password123",
            email="norole@test.com",
            phone="09444444444",
            status="active",
        )

        self.list_roles_url = reverse('list-of-roles')  # اسم url واقعی رو بذار

    # ---------------------------------------------------------
    # Permission
    # ---------------------------------------------------------

    def test_admin_can_list_roles(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_roles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_can_not_list_roles(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_roles_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_without_role_can_not_list_roles(self):
        self.client.force_authenticate(user=self.no_role_user)
        response = self.client.get(self.list_roles_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_list_roles(self):
        response = self.client.get(self.list_roles_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_with_pending_status_can_not_list_roles(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_roles_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # Content correctness
    # ---------------------------------------------------------

    def test_all_roles_are_returned(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_roles_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ۴ تا role توی setUp ساختیم
        self.assertEqual(len(response.data), 4)

        returned_codes = {item['code'] for item in response.data}
        self.assertEqual(
            returned_codes,
            {'admin', 'super_admin', 'regular', 'limited'}
        )

    # ---------------------------------------------------------
    # Exception path
    # ---------------------------------------------------------

    @mock.patch('user_management.views.list_roles.log_critical_event')
    @mock.patch('user_management.views.list_roles.ListOfRolesSerializer')
    def test_returns_500_on_unexpected_exception(
        self, mock_serializer, mock_log_critical_event
    ):
        mock_serializer.side_effect = ValueError("boom")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_roles_url)

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertIn('detail', response.data)

        mock_log_critical_event.assert_called_once()
        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'ROLE_LIST')
        self.assertEqual(kwargs['status_type'], 'error')
        self.assertEqual(kwargs['error_code'], 500)  # عدده، نه رشته
        self.assertEqual(kwargs['extra']['error_type'], 'ValueError')
        self.assertEqual(kwargs['extra']['error_message'], 'boom')

    # ---------------------------------------------------------
    # Logging on success
    # ---------------------------------------------------------

    @mock.patch('user_management.views.list_roles.log_critical_event')
    def test_success_logs_critical_event_with_correct_params(
        self, mock_log_critical_event
    ):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_roles_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_log_critical_event.assert_called_once()

        _, kwargs = mock_log_critical_event.call_args
        self.assertEqual(kwargs['action'], 'ROLE_LIST')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['user_id'], self.admin_user.id)
        self.assertEqual(kwargs['extra']['role_count'], 4)

    # ---------------------------------------------------------
    # Method not allowed
    # ---------------------------------------------------------

    def test_post_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_roles_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)