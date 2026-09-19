from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Group, UserGroup

class GroupRegisterViewTest(APITestCase):

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
        self.none_role_user = User.objects.create_user(
            username="none_role_user",
            password="password123",
            email="none_role@test.com",
            phone="09666666666",
            status="active",
            role=None
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
        self.register_group_url = reverse('group-register')

    def test_successful_registers(self):
        self.client.force_authenticate(user=self.admin_user)
        valid_data1 = {'title': 'UiUx','description': 'this is for UiUx developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert  Group.objects.filter(title='UiUx').exists()

        valid_data2 = {'title': 'AI','description': 'this is for AI developers',}
        response = self.client.post(self.register_group_url,valid_data2,format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert  Group.objects.filter(title='AI').exists()

    @patch('group_management.views.group_register.log_critical_event')
    def test_log_critical_event_receives_correct_group_name(self,mock_log):
        self.client.force_authenticate(user=self.admin_user)
        payload = {"title": "Sales", "description": "this is for Sales developers"}
        self.client.post(self.register_group_url,payload,format='json')

        success_call = [
            c for c in mock_log.call_args_list
            if c.kwargs.get('status_type') == 'success'
        ][0]
        assert success_call.kwargs['extra']['group_name'] == 'Sales'

    def test_unsuccessful_register_unauthorized_401(self):
        valid_data1 = {'title': 'AI','description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_unsuccessful_register_regular_role(self):
        self.client.force_authenticate(user=self.regular_user)
        valid_data1 = {'title': 'AI','description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_unsuccessful_register_limited_role(self):
        self.client.force_authenticate(user=self.limited_user)
        valid_data1 = {'title': 'AI','description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_successful_register_super_admin_user(self):
        self.client.force_authenticate(user=self.super_admin_user)
        valid_data1 = {'title': 'AI','description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        assert  Group.objects.filter(title='AI').exists()


    def test_successful_register_admin_user(self):
        self.client.force_authenticate(user=self.admin_user)
        valid_data1 = {'title': 'AI', 'description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url, valid_data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert  Group.objects.filter(title='AI').exists()

    def test_unsuccessful_register_error_code_10(self):
        self.client.force_authenticate(user=self.admin_user)
        valid_data1 = {'title': '', 'description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url, valid_data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_unsuccessful_registers_with_duplicate_title(self):
        self.client.force_authenticate(user=self.admin_user)
        valid_data1 = {'title': 'UiUx','description': 'this is for UiUx developers'}
        response = self.client.post(self.register_group_url,valid_data1,format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert  Group.objects.filter(title='UiUx').exists()

        with patch('group_management.views.group_register.log_critical_event') as mock_log:
            valid_data2 = {'title': 'UiUx','description': 'this is for UiUx developers',}
            response = self.client.post(self.register_group_url,valid_data2,format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['error_code'], 10)
            mock_log.assert_called_once()
            self.assertEqual(mock_log.call_args.kwargs['status_type'], 'failed')

    def test_unsuccessful_register_wrong_methods(self):
        self.client.force_authenticate(user=self.admin_user)
        valid_data1 = {'title': 'Back', 'description': 'this is for Backend developers'}
        response = self.client.patch(self.register_group_url, valid_data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotContains(response, 'Back',status_code=405)

        valid_data2 = {'title': 'Back', 'description': 'this is for Backend developers'}
        response = self.client.put(self.register_group_url, valid_data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotContains(response, 'Back', status_code=405)

        valid_data3 = {'title': 'Back', 'description': 'this is for Backend developers'}
        response = self.client.get(self.register_group_url, valid_data3, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotContains(response, 'Back',status_code=405)

        valid_data4 = {'title': 'Back', 'description': 'this is for Backend developers'}
        response = self.client.delete(self.register_group_url, valid_data4, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotContains(response, 'Back',status_code=405)

    def test_pending_admin_can_not_register_group(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        valid_data = {'title': 'AI', 'description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsuccessful_register_none_role(self):
        self.client.force_authenticate(user=self.none_role_user)
        valid_data = {'title': 'AI', 'description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('group_management.views.group_register.log_critical_event')
    @patch('group_management.views.group_register.GroupCreateSerializer')
    def test_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        valid_data = {'title': 'AI', 'description': 'this is for AI developers'}
        response = self.client.post(self.register_group_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)