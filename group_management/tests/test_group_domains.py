from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from identity.models import User, Role, Group, UserGroup, Domain, Tag, User_Domain_Tag


class GroupDomainTest(APITestCase):
    def setUp(self):
        # ===== Roles =====
        self.admin_role = Role.objects.create(
            code='admin', title='ادمین', level=100, is_system=True,
        )
        self.super_admin_role = Role.objects.create(
            code='super_admin', title='سوپر ادمین', level=999, is_system=True,
        )
        self.limited_role = Role.objects.create(
            code='limited', title='کاربر محدود شده', level=20, is_system=True,
        )
        self.regular_role = Role.objects.create(
            code='regular', title='کاربر معمولی', level=20, is_system=True,
        )

        # ===== Users =====
        self.admin_user = User.objects.create(
            username="admin_dara", password="admin_password123",
            email="admin@test.com", phone="09111111111",
            status="active", role=self.admin_role,
        )
        self.super_admin_user = User.objects.create(
            username="super_admin_nima", password="super_admin_password123",
            email="superadmin@test.com", phone="09222222222",
            status="active", role=self.super_admin_role,
        )
        self.regular_user = User.objects.create_user(
            username="normal_user", password="password123",
            email="normal@test.com", phone="09333333333",
            status="unverified", role=self.regular_role,
        )
        self.target_user = User.objects.create_user(
            username="pending_user", password="password123",
            email="target@test.com", phone="09444444444",
            status="pending",
        )
        self.limited_user = User.objects.create_user(
            username="limited_user", password="password123",
            email="limited@test.com", phone="09555555555",
            status="active", role=self.limited_role,
        )

        # ===== Groups =====
        self.group_one = Group.objects.create(title="frosh", description="")
        self.group_two = Group.objects.create(title="test", description="")
        self.group_three = Group.objects.create(title="mali", description="")
        self.group_four = Group.objects.create(
            title="fanni", description="", deleted_at=timezone.now()
        )

        # ===== Domains  =====
        self.domain_one = Domain.objects.create(
            domain_name="khanoumi.com", description="", group=self.group_one,
        )
        self.domain_two = Domain.objects.create(
            domain_name="rojashop.com", description="", group=self.group_one,
        )
        self.domain_three = Domain.objects.create(
            domain_name="modiage.com", description="", group=self.group_two,
        )
        self.domain_four = Domain.objects.create(
            domain_name="beautycode.ir", description="", group=self.group_three,
        )
        self.domain_five = Domain.objects.create(
            domain_name="GKS.com", description="", group=self.group_two,
            deleted_at=timezone.now(),
        )

        # ===== Tags =====
        self.tag_new = Tag.objects.create(title="new", description="")
        self.tag_wiki = Tag.objects.create(title="wiki", description="")
        self.tag_qa = Tag.objects.create(title="Q&A", description="")
        self.tag_deleted = Tag.objects.create(
            title="deleted-tag", description="", deleted_at=timezone.now(),
        )

        # ===== User_Domain_Tag  =====
        self.udt_regular_wiki = User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.domain_one,
            tag=self.tag_wiki,
        )
        self.udt_admin_new = User_Domain_Tag.objects.create(
            user=self.admin_user,
            domain=self.domain_one,
            tag=self.tag_new,
        )
        self.udt_deleted = User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.domain_one,
            tag=self.tag_qa,
            deleted_at=timezone.now(),
        )

        # ===== UserGroups =====
        UserGroup.objects.create(user=self.regular_user, group=self.group_one, is_primary=False)
        UserGroup.objects.create(user=self.limited_user, group=self.group_three, is_primary=True)
        UserGroup.objects.create(user=self.target_user, group=self.group_two, is_primary=True)

    # ============================================================
    #  GET
    # ============================================================

    def test_unauthenticated_user_gets_401(self):
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_can_view_own_group_domains(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]
        self.assertIn('khanoumi.com', domain_names)
        self.assertIn('rojashop.com', domain_names)
        self.assertNotIn('modiage.com', domain_names)

    def test_regular_user_cant_view_other_group_domains(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_three.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'],66)

    def test_limited_user_cant_view_other_group_domains(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_code'],66)

    def test_limited_user_can_view_own_group_domains(self):
        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-domains', args=[self.group_three.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]
        self.assertIn('beautycode.ir', domain_names)
        self.assertNotIn('khanoumi.com', domain_names)

    def test_admin_can_view_all_group_domains(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[self.group_two.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]
        self.assertIn('modiage.com', domain_names)

    def test_super_admin_can_view_all_group_domains(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]
        self.assertIn('khanoumi.com', domain_names)
        self.assertIn('rojashop.com', domain_names)

    def test_get_domains_for_nonexistent_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[999])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    def test_get_domains_for_deleted_group(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[self.group_four.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 65)

    def test_returns_correct_domains_for_group(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]

        self.assertCountEqual(domain_names, ['khanoumi.com', 'rojashop.com'])

    def test_soft_deleted_domain_not_returned(self):
        from django.utils import timezone

        self.domain_one.deleted_at = timezone.now()
        self.domain_one.save()

        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain_names = [item['domain_name'] for item in response.data]

        self.assertNotIn('khanoumi.com', domain_names)
        self.assertIn('rojashop.com', domain_names)

    def test_response_has_required_fields(self):
        self.client.force_authenticate(user=self.super_admin_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for item in response.data:
            self.assertIn('domain_name', item)
            self.assertIn('tags', item)
            self.assertIn('can_add_tag', item)
            self.assertIn('has_main_tag', item)

        self.assertTrue(all(item['can_add_tag'] is True for item in response.data))

    def test_admin_sees_all_tags_and_can_add(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        domain = next(d for d in response.data if d['domain_name'] == 'khanoumi.com')
        self.assertTrue(domain['can_add_tag'])

####################################################################
    def test_admin_sees_all_tags_and_overview(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain = next(d for d in response.data if d['domain_name'] == 'khanoumi.com')

        self.assertTrue(domain['can_add_tag'])
        self.assertTrue(domain['has_main_tag'])
        self.assertIn('tags_overview', domain)

        tag_titles = [t['title'] for t in domain['tags']]
        self.assertIn('new', tag_titles)  # admin tag
        self.assertIn('wiki', tag_titles)  #   regular user tag
        self.assertNotIn('Q&A', tag_titles)  # soft-deleted UDT  should not be in list

        # tags_overview construct
        overview_titles = [item['tag']['title'] for item in domain['tags_overview']]
        self.assertIn('new', overview_titles)
        self.assertIn('wiki', overview_titles)

    def test_regular_with_main_tag_sees_only_main(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain = next(d for d in response.data if d['domain_name'] == 'khanoumi.com')

        self.assertTrue(domain['has_main_tag'])
        self.assertFalse(domain['can_add_tag'])
        self.assertNotIn('tags_overview', domain)

        tag_titles = [t['title'] for t in domain['tags']]
        self.assertIn('new', tag_titles)
        self.assertNotIn('wiki', tag_titles)

    def test_regular_without_main_tag_sees_own_and_can_add(self):
        User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.domain_two,
            tag=self.tag_wiki,
        )

        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        domain = next(d for d in response.data if d['domain_name'] == 'rojashop.com')

        self.assertFalse(domain['has_main_tag'])
        self.assertFalse(domain['can_add_tag'])  # caz her self just added a tag

        tag_titles = [t['title'] for t in domain['tags']]
        self.assertIn('wiki', tag_titles)

    def test_regular_without_main_tag_and_no_own_tag_can_add(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        domain = next(d for d in response.data if d['domain_name'] == 'rojashop.com')

        self.assertFalse(domain['has_main_tag'])
        self.assertTrue(domain['can_add_tag'])
        self.assertEqual(domain['tags'], [])

    def test_limited_sees_only_main_tags(self):
        # put a main_tag and a regular tag on domain_four
        User_Domain_Tag.objects.create(
            user=self.admin_user,
            domain=self.domain_four,
            tag=self.tag_new,
        )
        User_Domain_Tag.objects.create(
            user=self.regular_user,
            domain=self.domain_four,
            tag=self.tag_wiki,
        )

        self.client.force_authenticate(user=self.limited_user)
        url = reverse('group-domains', args=[self.group_three.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domain = response.data[0]
        self.assertFalse(domain['can_add_tag'])
        self.assertTrue(domain['has_main_tag'])
        self.assertNotIn('tags_overview', domain)

        tag_titles = [t['title'] for t in domain['tags']]
        self.assertIn('new', tag_titles)
        self.assertNotIn('wiki', tag_titles)

    def test_soft_deleted_user_domain_tag_not_shown(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        domain = next(d for d in response.data if d['domain_name'] == 'khanoumi.com')
        tag_titles = [t['title'] for t in domain['tags']]

        self.assertNotIn('Q&A', tag_titles)  # udt_deleted

    def test_non_admin_has_no_tags_overview(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('group-domains', args=[self.group_one.id])
        response = self.client.get(url)

        for item in response.data:
            self.assertNotIn('tags_overview', item)