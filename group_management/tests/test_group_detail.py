from tokenize import group

from django.contrib.messages.api import success
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Group, UserGroup
from unittest.mock import patch


class GroupDetailTest(APITestCase):
    def setUp(self):
        # ===== Roles =====
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

        # ===== Users =====
        self.admin_user = User.objects.create(
            username="admin_dara",
            password="admin_password123",
            email="admin@test.com",
            phone="09111111111",
            status="active",
            role=self.admin_role,
        )
        self.super_admin_user = User.objects.create(
            username="super_admin_nima",
            password="super_admin_password123",
            email="superadmin@test.com",
            phone="09222222222",
            status="active",
            role=self.super_admin_role,
        )
        self.regular_user = User.objects.create_user(
            username="normal_user",
            password="password123",
            email="normal@test.com",
            phone="09333333333",
            status="unverified",
            role=self.regular_role,
        )
        self.target_user = User.objects.create_user(
            username="pending_user",
            password="password123",
            email="target@test.com",
            phone="09444444444",
            status="pending",
        )
        self.limited_user = User.objects.create_user(
            username="limited_user",
            password="password123",
            email="limited@test.com",
            phone="09555555555",
            status="active",
            role=self.limited_role,
        )

        # ===== Groups =====
        self.group_one = Group.objects.create(
            title="backend",
            description="this is for backend developers",
        )
        self.group_two = Group.objects.create(
            title="general",
            description="this is a general group",
        )
        self.group_three = Group.objects.create(
            title="finance",
            description="this is for finance developers",
        )
        self.group_six = Group.objects.create(
            title="UiUx",
            description="this is for UiUx users",
        )

        # (soft delete)
        self.group_five = Group.objects.create(
            title="deleted_group",
            description="this group will be deleted",
        )
        self.deleted_group_id = self.group_five.id
        self.group_five.deleted_at = timezone.now()
        self.group_five.save()

        # ===== UserGroups =====
        UserGroup.objects.create(
            user=self.regular_user,
            group=self.group_one,
            is_primary=False,
        )
        UserGroup.objects.create(
            user=self.limited_user,
            group=self.group_three,
            is_primary=True,
        )
        UserGroup.objects.create(
            user=self.target_user,
            group=self.group_two,
            is_primary=True,
        )

    # ============================================================
    #  GET
    # ============================================================

    def test_unauthenticated_user1_gets_401(self):
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cant_see_group_detail(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_cant_see_group_detail(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-detail', args=[self.group_three.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_sees_group_detail(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_three.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('finance', response.data['title'])

    @patch('group_management.views.group_detail.log_critical_event')
    def test_log_critical_event_receives_correct_group_detail(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_three.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_DETAIL')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'success')
        self.assertEqual(mock_log.call_args.kwargs['extra']['group_id'], self.group_three.id)

    def test_super_admin_sees_group_detail(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[self.group_six.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('UiUx', response.data['title'])
        self.assertEqual('uiux', response.data['title_normalized'])
        self.assertEqual('this is for UiUx users', response.data['description'])
        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['code'])
        self.assertTrue(response.data['is_active'])
        self.assertIsNone(response.data['deleted_at'])


    def test_get_deleted_group_returns_404(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[self.deleted_group_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)


    def test_get_nonexistent_group_returns_404(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[999])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    # ============================================================
    #  PATCH
    # ============================================================

    def test_unauthenticated_user2_gets_401(self):
        url = reverse('group-detail', args=[self.group_three.id])
        data = {"description": "this is a test group"}
        response = self.client.patch(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_update_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        valid_data = {"title": "backend_v2","description":"this is for backend developers"}
        response = self.client.patch(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'backend_v2')
        self.assertEqual(response.data['description'],"this is for backend developers")

    def test_super_admin_can_update_group(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[self.group_two.id])
        valid_data = {"title": "Liorad","description":"this is for unique developers"}
        response = self.client.patch(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('group_management.views.group_detail.log_critical_event')
    def test_log_critical_event_receives_correct_group_update(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[self.group_two.id])
        payload = {"title": "Liorad","description":"this is for unique developers"}
        response = self.client.patch(url,payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'],'GROUP_UPDATE')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'success')
        self.assertEqual(mock_log.call_args.kwargs['extra']['group_id'], self.group_two.id)


    def test_update_invalid_data_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        invalid_data = {"title": ""}
        response = self.client.patch(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'],10)

    def test_update_invalid_group_error_code_65(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[999])
        data = {"title": "migrate"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    @patch('group_management.views.group_detail.log_critical_event')
    def test_log_critical_event_receives_wrong_group_update(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-detail', args=[999])
        payload = {"title": "migrate"}
        response = self.client.patch(url,payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_UPDATE')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'failed')
        self.assertEqual(mock_log.call_args.kwargs['error_code'], 65)


    def test_update_soft_deleted_group_error_code_65(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_five.id])
        data = {"title": "migrate"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    def test_update_deleted_group_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.deleted_group_id])
        response = self.client.patch(url, {"title": "x"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_regular_user_cant_update_group(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.patch(url, {"title": "x"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_cant_update_group(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-detail', args=[self.group_five.id])
        response = self.client.patch(url, {"title": "x"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('group_management.views.group_detail.log_critical_event')
    def test_validation_failure_logs_correct_action_name(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_six.id])
        response = self.client.patch(url, {'title': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_UPDATE')


    def test_update_group_with_duplicate_title_returns_error(self):
        """
         Test that updating a group with a title that already exists
         returns a validation error
         """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        valid_data = {"title": "general"}
        response = self.client.patch(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_update_group_with_duplicate_title_returns_error(self):
        """
         Test that updating a group with a title that already exists
         returns a validation error
         """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        valid_data = {"title": "general"}
        response = self.client.patch(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)


    # ============================================================
    #  DELETE
    # ============================================================

    def test_unauthenticated_user3_gets_401(self):
        url = reverse('group-detail', args=[self.group_three.id])
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_delete_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.group_one.refresh_from_db()
        self.assertIsNotNone(self.group_one.deleted_at)
        response2=self.client.get(url, format='json')
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)

    @patch('group_management.views.group_detail.log_critical_event')
    def test_validation_success_logs_successful_soft_delete(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_DELETE')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'success')
        self.assertEqual(mock_log.call_args.kwargs['user_id'], self.admin_user.id)
        self.assertEqual(mock_log.call_args.kwargs['extra'], {"group_id": self.group_one.id})



    def test_delete_already_deleted_group_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.deleted_group_id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_group_returns_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[999])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_regular_user_cant_delete_group(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-detail', args=[self.group_one.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_cant_delete_group(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-detail', args=[self.group_five.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unavailable_group_can_not_be_soft_delete_404(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[self.group_five.id])
        data = {"title": "migrate"}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_group_delete_returns_error_code_65(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[999])
        data = {"title": "migrate"}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    @patch('group_management.views.group_detail.log_critical_event')
    def test_delete_nonexistent_group_logs_failure(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-detail', args=[999])
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_DELETE')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'failed')
        self.assertEqual(mock_log.call_args.kwargs['user_id'], self.admin_user.id)
        self.assertEqual(mock_log.call_args.kwargs['extra'], {"group_id": 999})