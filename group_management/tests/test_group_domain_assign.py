from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from identity.models import User, Role, Group, UserGroup,Domain,User_Domain_Tag,Tag

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

        # create_domain
        Domain.objects.create(
            domain_name="git.ir",
            description="Domain for version control and Git-related services, tailored for backend developers and DevOps teams.",
        )
        Domain.objects.create(
            domain_name="ai-lab.com",
            description="Research and development platform for artificial intelligence, machine learning models, and data science experiments.",
        )

        Domain.objects.create(
            domain_name="cloud-native.io",
            description="Enterprise domain for cloud-native applications, container orchestration, and microservices architecture patterns.",
        )

        Domain.objects.create(
            domain_name="security-hub.net",
            description="Cybersecurity intelligence hub for vulnerability assessment, penetration testing, and security best practices.",
        )

        Domain.objects.create(
            domain_name="data-flow.org",
            description="Data engineering and ETL pipeline domain, focusing on real-time data processing and big data analytics.",
            group = self.group_one
        )

        Domain.objects.create(
            domain_name="devops.ir",
            description="",
            group=self.group_two
        )
    ##########################################List user#########################################

    def test_unauthenticated_user_can_not_assign_domain_to_group(self):
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_one.id})
        data = {
            "add": [{"domain_name":"git.ir"}],
            "remove": []
        }
        response = self.client.post(url,data,format='json')

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_does_not_access_for_assign_domain_to_group(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_one.id})
        data = {
            "add": [{"domain_name":"git.ir"}],
            "remove": []
        }
        response = self.client.post(url,data,format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_limited_user_does_not_access_for_assign_domain_to_group(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_one.id})
        data = {
            "add": [{"domain_name":"git.ir"}],
            "remove": []
        }
        response = self.client.post(url,data,format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_not_assign_domain_to_deleted_group(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_five.id})
        data = {
            "add": [{"domain_name":"git.ir"}],
            "remove": []
        }
        response = self.client.post(url,data,format='json')

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    def test_empty_request_body_is_accepted_as_no_op(self):
        """
        "An empty request is completely valid because both add and remove are optional
        (default is list). Result: 200 OK with added=0, removed=0 — not an error."
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 0)
        self.assertEqual(response.data['result']['removed'], 0)

    def test_explicit_empty_lists_are_accepted_as_no_op(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        response = self.client.post(url, {"add": [], "remove": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 0)
        self.assertEqual(response.data['result']['removed'], 0)

    def test_blank_domain_name_returns_400(self):
        """
        An empty domain_name is rejected by the CharField (since allow_blank is False by default).
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        data = {"add": [{"domain_name": ""}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

###############Successful Add######################|

    def test_admin_can_assign_domain_to_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        data = {"add": [{"domain_name": "git.ir"}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result']['added'], 1)
        self.assertEqual(response.data['result']['removed'], 0)

    def test_admin_can_change_assign_domain_to_another_group(self):
        self.client.force_authenticate(user=self.admin_user)
        data_flow_domain  = Domain.objects.get(domain_name="data-flow.org")
        self.assertEqual(data_flow_domain.domain_name, "data-flow.org")
        self.assertEqual(data_flow_domain.group_id, self.group_one.id)

        url = reverse('group-domain-assign', kwargs={'group_id': self.group_three.id})
        data = {"add": [{"domain_name": "data-flow.org"}], "remove": []}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 1)

        data_flow_domain.refresh_from_db()
        self.assertEqual(data_flow_domain.domain_name, "data-flow.org")
        self.assertEqual(data_flow_domain.group_id,self.group_three.id)

    ###############Unsuccessful Add######################|

    def test_no_change_for_assign_domain_to_own_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"add": [{"domain_name": "data-flow.org"}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_domain_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"add": [{"domain_name": "data.org"}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ###############Successful Remove######################|

    def test_admin_can_remove_domain_to_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = { "add": [],"remove": [{"domain_name": "data-flow.org"}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result']['added'], 0)
        self.assertEqual(response.data['result']['removed'], 1)

    ###############Unsuccessful Remove######################|

    def test_admin_can_change_assign_domain_to_another_group(self):
        self.client.force_authenticate(user=self.admin_user)
        data_flow_domain = Domain.objects.get(domain_name="data-flow.org")
        self.assertEqual(data_flow_domain.domain_name, "data-flow.org")
        self.assertEqual(data_flow_domain.group_id, self.group_one.id)

        url = reverse('group-domain-assign', kwargs={'group_id': self.group_three.id})
        data = {"remove": [{"domain_name": "data-flow.org"}]}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['result']['removed'], 1)

    def test_admin_can_change_assign_domain_to_another_group(self):
        self.client.force_authenticate(user=self.admin_user)
        data_flow_domain = Domain.objects.get(domain_name="data-flow.org")
        self.assertEqual(data_flow_domain.domain_name, "data-flow.org")
        self.assertEqual(data_flow_domain.group_id, self.group_one.id)

        url = reverse('group-domain-assign', kwargs={'group_id': self.group_three.id})
        data = {"add": [{"domain_name": "data-flow.org"}],"remove": []}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 1)

    def test_nonexistent_domain_cant_be_remove(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"remove": [{"domain_name": "data.org"}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    ##################################Idempotency & race condition###################################
    def test_same_domain_in_add_and_remove_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        data_flow_domain = Domain.objects.get(domain_name="data-flow.org")
        self.assertEqual(data_flow_domain.group_id,self.group_one.id)
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_three.id})
        data = {
            "add": [{"domain_name": "data-flow.org"}],
            "remove": [{"domain_name": "data-flow.org"}]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'],60)
        self.assertEqual(response.data['detail'][0]['operation'],'remove')
        self.assertEqual(response.data['detail'][0]['domain_name'],'data-flow.org')

        data_flow_domain.refresh_from_db()
        self.assertEqual(data_flow_domain.group_id,self.group_one.id)

    def test_add_and_remove_domains_in_same_request(self):
        self.client.force_authenticate(user=self.admin_user)
        data_devops_domain  = Domain.objects.get(domain_name="devops.ir")
        self.assertEqual(data_devops_domain.domain_name, "devops.ir")
        self.assertEqual(data_devops_domain.group_id, self.group_two.id)

        url = reverse('group-domain-assign',kwargs={'group_id': self.group_two.id})
        data = {
            "add": [{"domain_name": "git.ir"}],
            "remove": [{"domain_name": "devops.ir"}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['result']['added'], 1)
        self.assertEqual(response.data['result']['removed'], 1)

        data_git_domain = Domain.objects.get(domain_name="git.ir")
        self.assertEqual(data_git_domain.group_id, self.group_two.id)

        data_devops_domain.refresh_from_db()
        self.assertIsNone(data_devops_domain.group_id)

    def test_invalid_add_prevents_valid_remove(self):
        self.client.force_authenticate(user=self.admin_user)
        data_devops_domain = Domain.objects.get(domain_name="devops.ir")
        self.assertEqual(data_devops_domain.group_id,self.group_two.id)
        url = reverse('group-domain-assign',kwargs={'group_id': self.group_two.id})
        data = {
            "add": [{"domain_name": "not-exist.ir"}],
            "remove": [{"domain_name": "devops.ir"}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'],60)

        data_devops_domain.refresh_from_db()
        self.assertEqual(data_devops_domain.group_id,self.group_two.id)

    @patch('group_management.views.group_domain_assign.log_critical_event')
    def test_group_domain_assign_logs_success(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        data = {"add": [{"domain_name": "git.ir"}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['result']['added'], 1)
        self.assertEqual(response.data['result']['removed'], 0)

        data_git_domain = Domain.objects.get(domain_name="git.ir")
        mock_log.assert_called_once()
        self.assertEqual(mock_log.call_args.kwargs['action'], 'GROUP_DOMAIN_ASSIGN')
        self.assertEqual(mock_log.call_args.kwargs['status_type'], 'success')
        self.assertEqual(mock_log.call_args.kwargs['user_id'], self.admin_user.id)
        self.assertEqual(mock_log.call_args.kwargs['extra']['group_id'], self.group_two.id)
        self.assertEqual(mock_log.call_args.kwargs['extra']['added_count'], 1)
        self.assertEqual(mock_log.call_args.kwargs['extra']['removed_count'], 0)

    @patch('group_management.views.group_domain_assign.log_critical_event')
    def test_group_domain_assign_logs_failure(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_two.id})
        data = {"add": [{"domain_name":"nm.com"}], "remove": []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(mock_log.call_args.kwargs['error_code'], 60)
        mock_log.assert_not_called()

    def test_wrong_http_method1(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"add": [{"domain_name": "git.ir"}], "remove": []}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_wrong_http_method2(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"add": [{"domain_name": "git.ir"}], "remove": []}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_wrong_http_method3(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_wrong_http_method4(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domain-assign', kwargs={'group_id': self.group_one.id})
        data = {"add": [{"domain_name": "git.ir"}], "remove": []}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


