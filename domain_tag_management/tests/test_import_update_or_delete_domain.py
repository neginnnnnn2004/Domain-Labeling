from django.utils import timezone
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role,Domain,Group

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

        # create Group
        self.group_one = Group.objects.create(
            title="backend",
            description="this is for backend developers",
        )
        self.group_two = Group.objects.create(
            title="general",
            description="this is a general group",
        )
        self.group_three = Group.objects.create(
            title="UiUx",
            description="this is for uiux users",
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

        # Domains
        self.soft_deleted_domain = Domain.objects.create(
            domain_name="school.ir",
            description="old description",
            group=self.group_two,
            created_by=self.admin_user,
            deleted_at=timezone.now(),
        )

        self.active_domain = Domain.objects.create(
            domain_name="tahlilgaran.com",
            description="",
            group=self.group_two,
            created_by=self.admin_user,
            deleted_at=None,
        )
        self.liorad_domain = Domain.objects.create(
            domain_name="liorad.ir",
            description="company_website",
            group=self.group_three,
            created_by=self.admin_user,
        )

        self.afarinesh_domain = Domain.objects.create(
            domain_name="afarinesh.com",
            description="IELT_journey website",
            group=self.group_one,
            created_by=self.admin_user,
            deleted_at=None,
        )

        # define urls
        self.domain_import_url = reverse('domain-import/edit-bulk')
#POST
    # permission
    def test_active_admin_can_import_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'Harvard.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_active_super_admin_can_import_domain(self):
        self.client.force_authenticate(user=self.super_admin_user)
        data = {
            'domain_name': 'MIT.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_none_active_admin_can_not_import_domain(self):
        self.client.force_authenticate(user=self.admin_user1)
        data = {
            'domain_name': 'Shahrood.uni.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_not_import_domain(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'domain_name': 'Shahrood.univer.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_import_domain(self):
        self.client.force_authenticate(user=self.limited_user)
        data = {
            'domain_name': 'Shahrood.university.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_import_domain(self):
        data = {
            'domain_name': 'Shahrood.uni.com',
            'description': '',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #Success
    def test_import_single_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'greece.ir',
            'description': '',
            'group': self.group_three.id,
        }
        response = self.client.post(self.domain_import_url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'],1)


    def test_normalize_domain_name(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {
                'domain_name': 'https://www.example.com',
                'description': '',
                'group': self.group_one.id,
            },
            {
                'domain_name': 'http://example.com',
                'description': '',
                'group': self.group_one.id,
            },
            {
                'domain_name': 'www.example.com',
                'description': '',
                'group': self.group_one.id,
            }
        ]
        response = self.client.post(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'],1)
        self.assertEqual(response.data['skipped_count'], 2)
        self.assertEqual(len(response.data['skipped_domains']), 2)
        self.assertEqual(Domain.objects.filter(domain_name='example.com').count(), 1)

    def test_import_bulk_domains(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {
                'domain_name': 'test.ir',
                'description': '',
                'group': self.group_two.id,
            },
            {
                'domain_name': 'mock.ir',
                'description': '',
                'group': self.group_one.id,
            },
            {
                'domain_name': 'IELTS.ir',
                'description': '',
                'group': self.group_four.id,
            }
        ]
        response = self.client.post(self.domain_import_url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'],3)


    def test_import_duplicate_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'tahlilgaran.com',
            'description': '',
            'group': self.group_three.id,
        }
        response = self.client.post(self.domain_import_url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_count'],0)
        self.assertEqual(response.data['skipped_count'],1)

    def test_import_bulk_domain_one_duplicate_onr_new(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {
                'domain_name': 'tahlilgaran.com',
                'description': '',
                'group': self.group_three.id,
            },
            {
                'domain_name': 'HarryPotter.com',
                'description': '',
                'group': self.group_one.id
            }
        ]
        response = self.client.post(self.domain_import_url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'],1)
        self.assertEqual(response.data['skipped_count'],1)

    #Reactivate
    def test_reactivate_single_soft_deleted_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data ={
            'domain_name': 'https://www.school.ir',
            'description': 'new description after reactivate',
            'group': self.group_three.id
        }

        response = self.client.post(self.domain_import_url, data,format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_count'],0)
        self.assertEqual(response.data["reactivated_count"], 1)
        self.assertEqual(response.data['skipped_count'],0)
        self.assertEqual(response.data["reactivated_domains"], ["school.ir"])
        self.assertEqual(response.data["created_domains"], [])

        #check database
        self.soft_deleted_domain.refresh_from_db()
        self.assertIsNone(self.soft_deleted_domain.deleted_at)
        self.assertEqual(self.soft_deleted_domain.description, 'new description after reactivate')
        self.assertEqual(self.soft_deleted_domain.group_id, self.group_three.id)
        self.assertEqual(self.soft_deleted_domain.created_by, self.admin_user)

    def test_bulk_new_plus_reactivate(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = [
            {
                "domain_name": "brand-new.com",
                "description": "completely new",
                "group": self.group_one.id,
            },
            {
                "domain_name": "school.ir",
                "description": "",
                "group": self.group_two.id,
            },
        ]

        response = self.client.post(self.domain_import_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["created_count"], 1)
        self.assertEqual(response.data["reactivated_count"], 1)
        self.assertEqual(response.data["skipped_count"], 0)

        self.assertIn(
            'brand-new.com',
            [d['domain_name'] for d in response.data['created_domains']]
        )
        self.assertEqual(response.data['reactivated_domains'], ['school.ir'])

        self.soft_deleted_domain.refresh_from_db()
        self.assertIsNone(self.soft_deleted_domain.deleted_at)
        self.assertEqual(self.soft_deleted_domain.group_id, self.group_two.id)

        self.assertTrue(
            Domain.objects.filter(domain_name='brand-new.com', deleted_at__isnull=True).exists()
        )

    def test_reactivate_duplicate_in_same_request(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = [
            {
                'domain_name': 'school.ir',
                'description': 'first',
                'group': self.group_one.id,
            },
            {
                'domain_name': 'https://www.school.ir',
                'description': 'second - should be skipped',
                'group': self.group_two.id,
            },
        ]

        response = self.client.post(self.domain_import_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_count'], 0)
        self.assertEqual(response.data['reactivated_count'], 1)
        self.assertEqual(response.data['skipped_count'], 1)
        self.assertEqual(response.data['reactivated_domains'], ['school.ir'])
        self.assertEqual(len(response.data['skipped_domains']), 1)

        self.soft_deleted_domain.refresh_from_db()
        self.assertIsNone(self.soft_deleted_domain.deleted_at)
        # فقط اولین description اعمال شده
        self.assertEqual(self.soft_deleted_domain.description, 'first')
        self.assertEqual(self.soft_deleted_domain.group_id, self.group_one.id)

    def test_reactivate_updates_description_group_created_by(self):
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'domain_name': 'school.ir',
            'description': 'updated by reactivate',
            'group': self.group_four.id,
        }
        response = self.client.post(self.domain_import_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reactivated_count'], 1)

        self.soft_deleted_domain.refresh_from_db()
        self.assertIsNone(self.soft_deleted_domain.deleted_at)
        self.assertEqual(self.soft_deleted_domain.description, 'updated by reactivate')
        self.assertEqual(self.soft_deleted_domain.group_id, self.group_four.id)

    def test_empty_request(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = [
            {
                'domain_name': '',
                'description': '',
                'group':'',
            },
            {
                'domain_name': '',
                'description': '',
                'group': '',
            },
        ]

        response = self.client.post(self.domain_import_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_count'], 0)
        self.assertEqual(response.data['skipped_count'], 0)

    def test_import_domain_to_nonexistent_group_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)

        payload ={
            'domain_name': 'valid-new-domain-xyz.com',
            'description': '',
            'group': 9999,
        }

        response = self.client.post(self.domain_import_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_import_domain_to_deleted_group(self):
        self.client.force_authenticate(user=self.admin_user)

        payload ={
            'domain_name': 'another-valid-domain.com',
            'description': '',
            'group': self.group_five.id,
        }

        response = self.client.post(self.domain_import_url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)
    # Logging
    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    def test_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(self.domain_import_url, {'domain_name': 'sara.ir'}, format='json')

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'IMPORT_DOMAIN')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['created_count'], 1)

    # PATCH
    # permission

    def test_active_admin_can_update_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'liorad.ir',
            "description": "",
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_active_super_admin_can_update_domain(self):
        self.client.force_authenticate(user=self.super_admin_user)
        data = {
            'domain_name': 'liorad.ir',
            'group': self.group_four.id,
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_none_active_admin_can_not_update_domain(self):
        self.client.force_authenticate(user=self.admin_user1)
        data = {
            'domain_name': 'liorad.ir',
            "description": "",
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_not_update_domain(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'domain_name': 'liorad.ir',
            "description": "",
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_update_domain(self):
        self.client.force_authenticate(user=self.limited_user)
        data = {
            'domain_name': 'liorad.ir',
            "description": "",
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_update_domain(self):
        data = {
            'domain_name': 'liorad.ir',
            "description": "",
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Success
    def test_single_update_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'afarinesh.com',
            'description': 'my_class',
            'group': self.group_three.id,
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.afarinesh_domain.refresh_from_db()
        self.assertEqual(self.afarinesh_domain.description, 'my_class')
        self.assertEqual(self.afarinesh_domain.group_id, self.group_three.id)

    # Not found / validation

    def test_update_nonexistent_domain_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'does-not-exist.com',
            'description': 'x',
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_update_soft_deleted_domain_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'domain_name': 'school.ir',
            'description': 'trying to edit deleted domain',
        }
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_missing_domain_name_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'description': 'no domain name given'}
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    # Bulk + atomicity

    def test_bulk_update_multiple_domains_succeeds(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {'domain_name': 'tahlilgaran.com', 'description': 'updated 1'},
            {'domain_name': 'afarinesh.com', 'description': 'updated 2'},
        ]
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)

        self.active_domain.refresh_from_db()
        self.afarinesh_domain.refresh_from_db()
        self.assertEqual(self.active_domain.description, 'updated 1')
        self.assertEqual(self.afarinesh_domain.description, 'updated 2')

    def test_bulk_update_partial_failure_rolls_back_all(self):
        self.client.force_authenticate(user=self.admin_user)
        original_description = self.active_domain.description

        data = [
            {'domain_name': 'tahlilgaran.com', 'description': 'should not persist'},
            {'domain_name': 'does-not-exist.com', 'description': 'x'},
        ]
        response = self.client.patch(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.active_domain.refresh_from_db()
        self.assertEqual(self.active_domain.description, original_description)

    # Logging

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    def test_update_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.patch(
            self.domain_import_url,
            {'domain_name': 'tahlilgaran.com', 'description': 'logged update'},
            format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'EDIT_DOMAIN')
        self.assertEqual(kwargs['status_type'], 'success')

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    def test_update_not_found_logs_error_code_10(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.patch(
            self.domain_import_url,
            {'domain_name': 'does-not-exist.com', 'description': 'x'},
            format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'EDIT_DOMAIN')
        self.assertEqual(kwargs['status_type'], 'failed')
        self.assertEqual(kwargs['error_code'], 10)

    # Exception

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    @patch('domain_tag_management.views.import_update_or_delete_domain.DomainImportOrEditSerializer')
    def test_update_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.domain_import_url,
            {'domain_name': 'tahlilgaran.com', 'description': 'x'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Method not allowed

    def test_get_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_import_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # DELETE
    # permission

    def test_active_admin_can_delete_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'domain_name': 'liorad.ir'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_active_super_admin_can_delete_domain(self):
        self.client.force_authenticate(user=self.super_admin_user)
        data = {'domain_name': 'afarinesh.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_none_active_admin_can_not_delete_domain(self):
        self.client.force_authenticate(user=self.admin_user1)
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_not_delete_domain(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_limited_user_can_not_delete_domain(self):
        self.client.force_authenticate(user=self.limited_user)
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_none_role_user_can_not_delete_domain(self):
        self.client.force_authenticate(user=self.none_role_user)
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_delete_domain(self):
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Success

    def test_single_delete_domain(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'domain_name': 'tahlilgaran.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 1)
        self.assertIn('tahlilgaran.com', response.data['deleted_domains'])

        self.active_domain.refresh_from_db()
        self.assertIsNotNone(self.active_domain.deleted_at)

    def test_bulk_delete_multiple_domains_succeeds(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {'domain_name': 'tahlilgaran.com'},
            {'domain_name': 'liorad.ir'},
        ]
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)

        self.active_domain.refresh_from_db()
        self.liorad_domain.refresh_from_db()
        self.assertIsNotNone(self.active_domain.deleted_at)
        self.assertIsNotNone(self.liorad_domain.deleted_at)

    # Not found / validation

    def test_delete_nonexistent_domain_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'domain_name': 'does-not-exist.com'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_delete_already_deleted_domain_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'domain_name': 'school.ir'}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_delete_missing_domain_name_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {}
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Bulk + atomicity

    def test_bulk_delete_partial_failure_rolls_back_all(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {'domain_name': 'tahlilgaran.com'},
            {'domain_name': 'does-not-exist.com'},
        ]
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.active_domain.refresh_from_db()
        self.assertIsNone(self.active_domain.deleted_at)

    def test_bulk_delete_duplicate_domain_in_same_request(self):
        self.client.force_authenticate(user=self.admin_user)
        data = [
            {'domain_name': 'tahlilgaran.com'},
            {'domain_name': 'tahlilgaran.com'},
        ]
        response = self.client.delete(self.domain_import_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.active_domain.refresh_from_db()
        self.assertIsNone(self.active_domain.deleted_at)

    # Logging

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    def test_delete_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(
            self.domain_import_url, {'domain_name': 'tahlilgaran.com'}, format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'DELETE_DOMAIN')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['deleted_count'], 1)
        self.assertIn('tahlilgaran.com', kwargs['extra']['deleted_domains'])

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    def test_delete_not_found_logs_error_code_10(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(
            self.domain_import_url, {'domain_name': 'does-not-exist.com'}, format='json'
        )
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'DELETE_DOMAIN')
        self.assertEqual(kwargs['status_type'], 'failed')
        self.assertEqual(kwargs['error_code'], 10)

    # Exception

    @patch('domain_tag_management.views.import_update_or_delete_domain.log_critical_event')
    @patch('domain_tag_management.views.import_update_or_delete_domain.timezone')
    def test_delete_returns_500_on_unexpected_exception(self, mock_timezone, mock_log):
        mock_timezone.now.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            self.domain_import_url, {'domain_name': 'tahlilgaran.com'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Method not allowed

    def test_put_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(
            self.domain_import_url, {'domain_name': 'tahlilgaran.com'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)