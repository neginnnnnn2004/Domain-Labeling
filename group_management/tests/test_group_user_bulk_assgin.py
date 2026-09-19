from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from identity.models import User, Role, Group, UserGroup

class GroupMembersViewTest(APITestCase):
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
        self.limited_user = User.objects.create_user(
            username="limited_user",
            password="password123",
            email="limited@test.com",
            phone="09555555556",
            status="active",
            role=self.limited_role
        )
        self.nastaran_user = User.objects.create_user(
            username="nastaran_user",
            password="password123",
            email="nastaran@test.com",
            phone="09555555557",
            status="active",
            role=self.regular_role
        )
        self.mahsa_user = User.objects.create_user(
            username="mahsa_user",
            password="password123",
            email="mahsa@test.com",
            phone="09555555558",
            status="active",
            role=self.limited_role
        )
        self.deleted_user = User.objects.create_user(
            username="deleted_user",
            password="password123",
            email="del@test.com",
            phone="09555555458",
            status="deleted",
            role=self.limited_role,
            deleted_at=timezone.now()
        )
        # create_group
        self.group_one= Group.objects.create(
            title = "backend",
            description = "this is for backend developers",
        )
        self.group_two = Group.objects.create(
            title = "general",
            description = "this is a general group",
        )
        self.group_three = Group.objects.create(
            title = "UiUx",
            description = "this is for uiux users",
        )
        self.group_four = Group.objects.create(
            title="Frontend",
            description="this is for frontend developers",
        )
        self.group_five = Group.objects.create(
            title="Design",
            description="this is for designer",
            deleted_at=timezone.now(),

        )
        # create_user_group
        UserGroup.objects.create(
            user = self.regular_user,
            group =  self.group_one,
            is_primary = False
        )
        UserGroup.objects.create(
            user = self.limited_user,
            group =  self.group_two,
            is_primary = True
        )
        UserGroup.objects.create(
            user = self.target_user,
            group =  self.group_three,
            is_primary = True
        )
        UserGroup.objects.create(
            user=self.nastaran_user,
            group=self.group_two,
            is_primary=True
        )
        UserGroup.objects.create(
            user = self.mahsa_user,
            group =  self.group_three,
            is_primary = False
        )

        self.assign_url = lambda group_id: reverse('group-user-assign', kwargs={'group_id': group_id})


    def test_admin_user_can_assign(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_user_can_assign(self):
        self.client.force_authenticate(user=self.super_admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_can_not_assign(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            self.assign_url(self.group_four.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_assign(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.post(
            self.assign_url(self.group_three.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_role_user_can_not_assign(self):
        self.client.force_authenticate(user=self.target_user)
        response = self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_can_not_assign(self):
        response = self.client.post(
            self.assign_url(self.group_four.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_active_admin_user_can_not_assign(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(999),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'],65)

    def test_soft_deleted_group(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_five.id),
            {"add": [], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'],65)

    def test_serializer_validation_fails_with_malformed_payload(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": "not-a-list", "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 60)

    def test_serializer_validation_fails_missing_user_id(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"is_primary": True}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 60)

    def test_serializer_validation_fails_wrong_type_for_user_id(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": "abc"}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 60)

    def test_serializer_validation_fails_empty_payload(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 0)
        self.assertEqual(response.data['result']['removed'], 0)

    def test_add_successfully(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.limited_user.id}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_duplicate_user_in_request_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.limited_user.id},{"user_id": self.limited_user.id}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 60)
        self.assertFalse(
            UserGroup.objects.filter(user=self.limited_user, group=self.group_one).exists()
        )

    def test_add_nonexistent_user_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": 99999}], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_deleted_user_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.deleted_user.id}], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_already_member_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.regular_user.id}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_second_primary_group_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_three.id),
            {"add": [{"user_id": self.limited_user.id, "is_primary": True}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            UserGroup.objects.filter(
                user=self.limited_user, group=self.group_three, is_primary=True
            ).exists()
        )
        self.assertTrue(
            UserGroup.objects.filter(
                user=self.limited_user, group=self.group_two, is_primary=True
            ).exists()
        )

    def test_add_already_member_group_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [{"user_id": self.limited_user.id, "is_primary": True}], "remove": []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_successfully(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [], "remove": [{"user_id": self.regular_user.id}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_duplicate_user_in_request_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [], "remove": [{"user_id": self.regular_user.id},{"user_id": self.regular_user.id}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_nonexistent_user_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [], "remove": [{"user_id": 99999}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conflict_user_fails(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.limited_user.id}], "remove": [{"user_id": self.limited_user.id}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_valid_remove_invalid_rolls_back_nothing(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [{"user_id": self.mahsa_user.id}], "remove": [{"user_id": 99999}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(
            UserGroup.objects.filter(user=self.mahsa_user, group=self.group_two, deleted_at__isnull=True).exists()
        )
        self.assertTrue(
            UserGroup.objects.filter(user=self.limited_user, group=self.group_two, deleted_at__isnull=True).exists()
        )

    def test_atomicity_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [{"user_id": self.regular_user.id}], "remove": [{"user_id": self.limited_user.id}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 1)
        self.assertEqual(response.data['result']['removed'], 1)

        self.assertTrue(UserGroup.objects.filter(user=self.regular_user, group=self.group_two, deleted_at__isnull=True).exists())

        removed_membership = UserGroup.objects.get(user=self.limited_user, group=self.group_two,deleted_at__isnull=False)
        self.assertIsNotNone(removed_membership.deleted_at)

    @patch('group_management.views.group_user_bulk_assign.log_critical_event')
    def test_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(
            self.assign_url(self.group_two.id),
            {"add": [{"user_id": self.regular_user.id}], "remove": []}, format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'GROUP_USER_ASSIGN')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['added_count'], 1)
        self.assertEqual(kwargs['extra']['removed_count'], 0)

    @patch('group_management.views.group_user_bulk_assign.log_critical_event')
    def test_group_not_found_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(
            self.assign_url(99999),
            {"add": [], "remove": []}, format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 65)
        self.assertEqual(kwargs['extra']['group_id'], 99999)

    @patch('group_management.views.group_user_bulk_assign.UserGroup.objects.bulk_create')
    def test_returns_500_on_unexpected_exception_during_bulk_create(self, mock_bulk_create):
        mock_bulk_create.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.nastaran_user.id}], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.assign_url(self.group_one.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.nastaran_user.id}], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.assign_url(self.group_one.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.assign_url(self.group_one.id),
            {"add": [{"user_id": self.nastaran_user.id}], "remove": []}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)