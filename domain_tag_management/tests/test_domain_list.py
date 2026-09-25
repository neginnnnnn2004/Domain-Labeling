from django.utils import timezone
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Domain, Group, UserGroup


class DomainListViewTest(APITestCase):

    def setUp(self):
        # -------------------- Roles --------------------
        self.admin_role = Role.objects.create(
            code='admin', title='ادمین', level=100, is_system=True
        )
        self.super_admin_role = Role.objects.create(
            code='super_admin', title='سوپر ادمین', level=999, is_system=True
        )
        self.limited_role = Role.objects.create(
            code='limited', title='کاربر محدود شده', level=20, is_system=True
        )
        self.regular_role = Role.objects.create(
            code='regular', title='کاربر معمولی', level=20, is_system=True
        )

        # -------------------- Users --------------------
        self.admin_user = User.objects.create(
            username="admin",
            password="admin_password123",
            email="admin@test.com",
            phone="09111111111",
            status="active",
            role=self.admin_role
        )
        self.super_admin_user = User.objects.create(
            username="super_admin",
            password="super_admin_password123",
            email="superadmin@test.com",
            phone="09222222222",
            status="active",
            role=self.super_admin_role
        )
        self.regular_user = User.objects.create_user(
            username="regular_user",
            password="password123",
            email="regular@test.com",
            phone="09333333333",
            status="active",
            role=self.regular_role
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
        self.user_no_group = User.objects.create_user(
            username="no_group_user",
            password="password123",
            email="nogroup@test.com",
            phone="09120000000",
            status="active",
            role=self.regular_role
        )

        # -------------------- Groups --------------------
        self.group_one = Group.objects.create(title="backend", description="backend developers")
        self.group_two = Group.objects.create(title="general", description="general group")
        self.group_three = Group.objects.create(title="UiUx", description="uiux users")
        self.group_four = Group.objects.create(title="Frontend", description="frontend developers")
        self.group_five = Group.objects.create(
            title="Design", description="designers", deleted_at=timezone.now()
        )

        # -------------------- UserGroup --------------------
        UserGroup.objects.create(user=self.regular_user, group=self.group_one, is_primary=False)
        UserGroup.objects.create(user=self.limited_user, group=self.group_four, is_primary=True)
        UserGroup.objects.create(user=self.none_role_user, group=self.group_two, is_primary=False)

        # -------------------- Domains --------------------
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
        )
        self.liorad_domain = Domain.objects.create(
            domain_name="liorad.ir",
            description="company website",
            group=self.group_three,
            created_by=self.admin_user,
        )
        self.afarinesh_domain = Domain.objects.create(
            domain_name="afarinesh.com",
            description="IELTS journey",
            group=self.group_one,
            created_by=self.admin_user,
        )
        self.safir_domain = Domain.objects.create(
            domain_name="safir.ir",
            description="english learning",
            group=None,
            created_by=self.admin_user,
        )

        self.domain_list_url = reverse('list-of-domains')

    # =====================================================
    # 1. Permission Tests
    # =====================================================

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_active_admin_can_access(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_active_super_admin_can_access(self):
        self.client.force_authenticate(user=self.super_admin_user)
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_can_access(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_limited_user_can_access(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_without_role_can_access(self):
        self.client.force_authenticate(user=self.none_role_user)
        response = self.client.get(self.domain_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # =====================================================
    # 2. Domain Visibility - Admin / Super Admin
    # =====================================================

    def test_admin_sees_all_active_domains(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]

        expected = [
            "tahlilgaran.com",
            "liorad.ir",
            "afarinesh.com",
            "safir.ir",
        ]
        for name in expected:
            self.assertIn(name, returned_names)

        active_count = Domain.objects.filter(deleted_at__isnull=True).count()
        self.assertEqual(len(response.data), active_count)

    def test_admin_does_not_see_soft_deleted_domains(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertNotIn("school.ir", returned_names)

    def test_super_admin_sees_all_active_domains(self):
        self.client.force_authenticate(user=self.super_admin_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active_count = Domain.objects.filter(deleted_at__isnull=True).count()
        self.assertEqual(len(response.data), active_count)

    # =====================================================
    # 3. Domain Visibility - Regular User
    # =====================================================

    def test_regular_user_sees_domains_of_his_groups(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertIn("afarinesh.com", returned_names)

    def test_regular_user_sees_domains_without_group(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertIn("safir.ir", returned_names)

    def test_regular_user_does_not_see_domains_of_other_groups(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]

        self.assertNotIn("tahlilgaran.com", returned_names)  # group_two
        self.assertNotIn("liorad.ir", returned_names)        # group_three

    def test_regular_user_does_not_see_soft_deleted_domains(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertNotIn("school.ir", returned_names)

    def test_regular_user_with_no_groups_only_sees_ungrouped_domains(self):
        self.client.force_authenticate(user=self.user_no_group)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]

        self.assertEqual(returned_names, ["safir.ir"])
        self.assertNotIn("afarinesh.com", returned_names)
        self.assertNotIn("tahlilgaran.com", returned_names)
        self.assertNotIn("liorad.ir", returned_names)

    # =====================================================
    # 4. Domain Visibility - Limited User
    # =====================================================

    def test_limited_user_sees_domains_of_his_groups_and_ungrouped(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get(self.domain_list_url, {'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]

        self.assertIn("safir.ir", returned_names)
        self.assertNotIn("afarinesh.com", returned_names)
        self.assertNotIn("tahlilgaran.com", returned_names)
        self.assertNotIn("liorad.ir", returned_names)

    # =====================================================
    # 5. Search Tests
    # =====================================================

    def test_search_by_domain_name_partial_match(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'search': 'liorad', 'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertEqual(returned_names, ["liorad.ir"])

    def test_search_case_insensitive(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'search': 'SAFIR', 'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item['domain_name'] for item in response.data]
        self.assertIn("safir.ir", returned_names)

    def test_search_no_match_returns_empty_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'search': 'nonexistentdomain123', 'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_empty_string_returns_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'search': '', 'page_size': 100})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active_count = Domain.objects.filter(deleted_at__isnull=True).count()
        self.assertEqual(len(response.data), active_count)

    # =====================================================
    # 6. Pagination Tests
    # =====================================================

    def test_default_page_size_is_20(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) <= 20)

    def test_custom_page_size(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'page_size': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 2)

    def test_page_size_cannot_exceed_100(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'page_size': 500})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 100)

    # =====================================================
    # 7. Logging Test
    # =====================================================

    @patch('domain_tag_management.views.domain_list.log_critical_event')
    def test_successful_list_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.domain_list_url, {'search': 'safir'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_log.assert_called()
        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'DOMAIN_LIST')
        self.assertEqual(kwargs['status_type'], 'success')