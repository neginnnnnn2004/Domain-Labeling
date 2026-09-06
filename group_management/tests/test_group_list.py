from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Group, UserGroup,Domain,User_Domain_Tag,Tag

class GroupListTest(APITestCase):
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
            phone="09555555555",
            status="active",
            role=self.limited_role
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
            title = "finance",
            description = "this is for finance developers",
        )
        # create_user_group
        # self.active_regular_user_group_list
        UserGroup.objects.create(
            user = self.regular_user,
            group =  self.group_one,
            is_primary = False
        )
        # self.active_limited_user_group_list
        UserGroup.objects.create(
            user = self.limited_user,
            group =  self.group_three,
            is_primary = True
        )
        # self.pending_user_cant_list_group
        UserGroup.objects.create(
            user = self.target_user,
            group =  self.group_two,
            is_primary = True
        )


        # define urls
        self.list_group_url = reverse('list-of-groups')

    def test_regular_user_sees_only_their_groups(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        titles = [g['title'] for g in response.data]
        self.assertIn('backend', titles)
        self.assertNotIn('general', titles)
        self.assertNotIn('finance', titles)

        for group_data in response.data:
            self.assertNotIn('code', group_data)
            self.assertNotIn('is_active', group_data)
            self.assertNotIn('user_count', group_data)
            self.assertNotIn('tag_count', group_data)
            self.assertIn('id', group_data)
            self.assertIn('title', group_data)
            self.assertIn('description', group_data)

    @patch('group_management.views.group_list.log_critical_event')
    def test_regular_user_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)
        self.client.get(self.list_group_url)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['extra']['access_type'], 'member')


    def test_limited_user_sees_only_their_group(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        titles = [g['title'] for g in response.data]
        self.assertIn('finance', titles)
        self.assertNotIn('backend', titles)
        self.assertNotIn('general', titles)

        for group_data in response.data:
            self.assertNotIn('code', group_data)
            self.assertNotIn('is_active', group_data)
            self.assertNotIn('user_count', group_data)
            self.assertNotIn('tag_count', group_data)
            self.assertIn('id', group_data)
            self.assertIn('title', group_data)
            self.assertIn('description', group_data)

    @patch('group_management.views.group_list.log_critical_event')
    def test_limited_user_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.limited_user)
        self.client.get(self.list_group_url)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['extra']['access_type'], 'member')

    def test_admin_sees_all_groups(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # backend + general + finance

        titles = [g['title'] for g in response.data]
        self.assertIn('backend', titles)
        self.assertIn('general', titles)
        self.assertIn('finance', titles)

        for group_data in response.data:
            self.assertIn('code', group_data)
            self.assertIn('is_active', group_data)
            self.assertIn('user_count', group_data)

        group_one_data = next(g for g in response.data if g['id'] == self.group_one.id)
        self.assertEqual(group_one_data['code'], self.group_one.code)
        self.assertTrue(group_one_data['is_active'])

    @patch('group_management.views.group_list.log_critical_event')
    def test_admin_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.get(self.list_group_url)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['extra']['access_type'], 'admin')

    def test_super_admin_sees_all_groups(self):
        self.client.force_authenticate(user=self.super_admin_user)
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for group_data in response.data:
            self.assertIn('code', group_data)
            self.assertIn('is_active', group_data)
            self.assertIn('user_count', group_data)

        group_two_data = next(g for g in response.data if g['id'] == self.group_two.id)
        self.assertEqual(group_two_data['code'], self.group_two.code)
        self.assertTrue(group_two_data['is_active'])

    @patch('group_management.views.group_list.log_critical_event')
    def test_super_admin_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.super_admin_user)
        self.client.get(self.list_group_url)

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['extra']['access_type'], 'admin')


    def test_unauthenticated_user_gets_401(self):
        response = self.client.get(self.list_group_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_with_no_group_sees_empty_list(self):
        no_group_user = User.objects.create_user(
            username="no_group",
            password="password123",
            email="nogroup@test.com",
            phone="09666666666",
            status="active",
            role=self.regular_role
        )
        self.client.force_authenticate(user=no_group_user)
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def _make_user(self, suffix, **extra):
        """Helper to create a user with all unique fields auto-filled."""
        defaults = {
            "password": "x",
            "email": f"user_{suffix}@test.com",
            "phone": f"0910000{suffix:04d}",
        }
        defaults.update(extra)
        return User.objects.create_user(username=f"user_{suffix}", **defaults)

    def test_user_count_annotation_is_correct(self):
        self.client.force_authenticate(user=self.admin_user)
        group = Group.objects.create(title="Count Test", code="counttest")

        for i in range(3):
            u = self._make_user(i)
            UserGroup.objects.create(user=u, group=group, is_primary=False)

        response = self.client.get(self.list_group_url)
        data = next(g for g in response.data if g['id'] == group.id)
        self.assertEqual(data['user_count'], 3)

###################Soft-delete#################
    def test_admin_does_not_see_deleted_groups(self):
        self.client.force_authenticate(user=self.admin_user)
        self.group_three.deleted_at = timezone.now() # after the changes it should be saved
        self.group_three.save(update_fields=['deleted_at'])
        response = self.client.get(self.list_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertNotEqual(len(response.data), 3)

        titles = [g['title'] for g in response.data]
        self.assertIn('backend', titles)
        self.assertIn('general', titles)
        self.assertNotIn('finance', titles)

        for group_data in response.data:
            self.assertIn('code', group_data)
            self.assertIn('is_active', group_data)
            self.assertIn('user_count', group_data)

    def test_group_with_no_user(self):
        self.client.force_authenticate(user=self.admin_user)

        group_four = Group.objects.create(
            title="UiUx",
            description="this is for UiUx Users",
        )

        response = self.client.get(self.list_group_url)

        group_four_data = next(
            g for g in response.data if g['id'] == group_four.id
        )

        self.assertEqual(group_four_data['user_count'], 0)

    def test_group_count_logged_correctly(self):
        with patch('group_management.views.group_list.log_critical_event') as mock_log:
            self.client.force_authenticate(user=self.admin_user)
            response = self.client.get(self.list_group_url)

            mock_log.assert_called_once()
            actual_count = len(response.data)
            self.assertEqual(
                mock_log.call_args.kwargs['extra']['group_count'],
                actual_count
            )

    @patch('group_management.views.group_list.log_critical_event')
    def test_error_status_logged_on_exception(self, mock_log):
        with patch(
                'group_management.views.group_list.AdminListOfGroupsSerializer'
        ) as mock_serializer:
            mock_serializer.side_effect = Exception("boom")
            self.client.force_authenticate(user=self.admin_user)
            self.client.get(self.list_group_url)

            mock_log.assert_called_once()
            self.assertEqual(mock_log.call_args.kwargs['status_type'], 'error')
            self.assertEqual(mock_log.call_args.kwargs['error_code'], 500)
            self.assertIn('error_type', mock_log.call_args.kwargs['extra'])
            self.assertIn('error_message', mock_log.call_args.kwargs['extra'])


    def test_wrong_http_methods_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)

        for method_name in ['post', 'put', 'patch', 'delete']:
            with self.subTest(method=method_name):
                method = getattr(self.client, method_name)
                response = method(self.list_group_url, {}, format='json')
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
