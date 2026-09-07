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
        self.nor_user = User.objects.create_user(
            username="nor_user",
            password="password123",
            email="nor@test.com",
            phone="09555555559",
            status="deleted",
            role=self.regular_role,
            deleted_at=timezone.now(),
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
        UserGroup.objects.create(
            user=self.nor_user,
            group=self.group_one,
            is_primary=False
        )

    def test_admin_can_get_group_members(self):
        self.client.force_authenticate(user=self.admin_user)
        url1 = reverse('group-members-get',kwargs={'group_id': self.group_one.id})
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response1.data),1)

        self.assertEqual(response1.data[0]['user_id'],self.regular_user.id)

        # deleted user must not be returned
        member_user_ids = [member['user_id']for member in response1.data]
        self.assertNotIn(self.nor_user.id,member_user_ids)


        url2 = reverse('group-members-get',kwargs={'group_id': self.group_two.id})
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response2.data),2)


        url3 = reverse('group-members-get',kwargs={'group_id': self.group_three.id})
        response3 = self.client.get(url3)
        self.assertEqual(response3.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response3.data),2)


        url4 = reverse('group-members-get',kwargs={'group_id': self.group_four.id})
        response4 = self.client.get(url4)
        self.assertEqual(response4.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response4.data),0)
        self.assertEqual(response4.data,[])

    def test_super_admin_can_get_group_members(self):
        self.client.force_authenticate(user=self.super_admin_user)

        url = reverse('group-members-get',kwargs={'group_id': self.group_four.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),0)
        self.assertEqual(response.data,[])

    @patch('group_management.views.group_members.log_critical_event')
    def test_admin_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-members-get', args=[self.group_four.id])
        self.client.get(url,format='json')

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_MEMBERS_LIST')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'success')
        self.assertEqual(mock_log.call_args.kwargs['user_id'], self.admin_user.id)
        self.assertEqual(mock_log.call_args.kwargs['extra'], {"group_id": self.group_four.id})


    def test_unauthenticated_user_can_not_get_group_members(self):
        url = reverse('group-members-get',kwargs={'group_id': self.group_four.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_can_not_get_group_members(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-members-get',kwargs={'group_id': self.group_four.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_get_group_members(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-members-get',kwargs={'group_id': self.group_four.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_soft_deleted_group_not_allowed_for_get_group_members(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-members-get',kwargs={'group_id': self.group_five.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code',65])

    def test_not_available_group_can_not_for_get_group_members(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-members-get',kwargs={'group_id':999})
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code',65])


    @patch('group_management.views.group_members.log_critical_event')
    def test_admin_access_type_logged_correctly(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-members-get', args=[999])
        self.client.get(url,format='json')

        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_MEMBERS_LIST')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'failed')
        self.assertEqual(mock_log.call_args.kwargs['user_id'], self.admin_user.id)
        self.assertEqual(mock_log.call_args.kwargs['extra'], {"group_id": 999})