from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role,Tag

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
        self.admin_user1 = User.objects.create(
            username="admin",
            password="admin_password123",
            email="adminn@test.com",
            phone="09111166111",
            status="suspended",
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

        #create tag
        self.existing_tag = Tag.objects.create(
            title = "urgent",
            description = "",
            is_active = True
        )

        # define urls
        self.tag_create_url = reverse('tag-create')

    # Permission
    def test_admin_can_create_tag(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_super_admin_can_create_tag(self):
        self.client.force_authenticate(user=self.super_admin_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_can_not_create_tag(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_create_tag(self):
        self.client.force_authenticate(user=self.limited_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_none_role_user_can_not_create_tag(self):
        self.client.force_authenticate(user=self.none_role_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_create_tag(self):
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_with_non_active_status_can_not_create_tag(self):
        self.client.force_authenticate(user=self.admin_user1)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    # Success
    def test_create_tag_sets_created_by(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'park',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tag = Tag.objects.get(title="park")
        self.assertEqual(tag.created_by, self.admin_user)

    def test_create_tag_response_contains_correct_data(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'backend',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'],'backend')

    # Validation — error_code 10
    def test_empty_title_returns_error_code_10(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.tag_create_url, {"title": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_missing_title_returns_error_code_10(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.tag_create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    # Validation — duplicate tag (error_code 11)
    def test_duplicate_title_returns_error_code_11(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'urgent',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 11)

    def test_duplicate_title_case_insensitive_returns_error_code_11(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'URGENT',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 11)

    def test_duplicate_title_with_whitespace_returns_error_code_11(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': '  urgent  ',
            'description': '',
            'is_active': True,
        }
        response = self.client.post(self.tag_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 11)

    # Logging
    @patch('domain_tag_management.views.tag_create.log_critical_event')
    def test_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(self.tag_create_url, {"title": "logged-tag"}, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'CREATE_TAG')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['tag_title'], 'logged-tag')

    @patch('domain_tag_management.views.tag_create.log_critical_event')
    def test_duplicate_logs_error_code_11(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(self.tag_create_url, {"title": "urgent"}, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['status_type'], 'failed')
        self.assertEqual(kwargs['error_code'], 11)

    @patch('domain_tag_management.views.tag_create.log_critical_event')
    def test_invalid_data_logs_error_code_10(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(self.tag_create_url, {"title": ""}, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['status_type'], 'failed')
        self.assertEqual(kwargs['error_code'], 10)

    # Exception
    @patch('domain_tag_management.views.tag_create.log_critical_event')
    @patch('domain_tag_management.views.tag_create.TagRegisterSerializer')
    def test_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.tag_create_url, {"title": "crash-tag"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Method not allowed
    def test_get_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.tag_create_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)