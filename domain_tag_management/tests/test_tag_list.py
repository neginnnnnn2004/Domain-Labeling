from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Tag


class ListOfTagViewTest(APITestCase):

    def setUp(self):
        self.regular_role = Role.objects.create(code='regular', title='کاربر معمولی', level=20, is_system=True)
        self.limited_role = Role.objects.create(code='limited', title='کاربر محدود شده', level=20, is_system=True)
        self.admin_role = Role.objects.create(code='admin', title='ادمین', level=100, is_system=True)

        self.regular_user = User.objects.create_user(
            username="normal_user", password="pass123", email="normal@test.com",
            phone="09333333333", status="active", role=self.regular_role,
        )
        self.limited_user = User.objects.create_user(
            username="limited_user", password="pass123", email="limited@test.com",
            phone="09444444444", status="active", role=self.limited_role,
        )
        self.admin_user = User.objects.create_user(
            username="admin_dara", password="pass123", email="admin@test.com",
            phone="09111111111", status="active", role=self.admin_role,
        )
        self.no_role_user = User.objects.create_user(
            username="no_role_user", password="pass123", email="norole@test.com",
            phone="09555555555", status="active",
        )

        self.tag_active_1 = Tag.objects.create(title="zebra", description="...")
        self.tag_active_2 = Tag.objects.create(title="alpha", description="...")
        self.tag_inactive = Tag.objects.create(title="inactive-tag", description="...", is_active=False)
        self.tag_deleted = Tag.objects.create(title="deleted-tag", description="...")
        self.tag_deleted.deleted_at = timezone.now()
        self.tag_deleted.save(update_fields=["deleted_at"])

        self.list_tag_url = reverse('list-of-tag')

    # ===========================================================
    # Permission
    # ===========================================================

    def test_regular_user_can_list_tags(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_limited_user_can_list_tags(self):
        self.client.force_authenticate(user=self.limited_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_list_tags(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_role_user_can_list_tags(self):
        self.client.force_authenticate(user=self.no_role_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_not_list_tags(self):
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ===========================================================
    # Filter correctness
    # ===========================================================

    def test_only_active_non_deleted_tags_are_returned(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_tag_url)

        returned_titles = {item['title'] for item in response.data}
        self.assertIn('zebra', returned_titles)
        self.assertIn('alpha', returned_titles)
        self.assertNotIn('inactive-tag', returned_titles)
        self.assertNotIn('deleted-tag', returned_titles)

    def test_returns_correct_count(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(len(response.data), 2)

    # ===========================================================
    # Ordering
    # ===========================================================

    def test_tags_are_ordered_alphabetically(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_tag_url)

        titles = [item['title'] for item in response.data]
        self.assertEqual(titles, sorted(titles))
        self.assertEqual(titles, ['alpha', 'zebra'])

    # ===========================================================
    # Logging
    # ===========================================================

    @patch('domain_tag_management.views.tag_list.log_critical_event')
    def test_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.regular_user)
        self.client.get(self.list_tag_url)

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'LIST_TAG')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['user_id'], self.regular_user.id)

    @patch('domain_tag_management.views.tag_list.log_critical_event')
    def test_exception_logs_error_code(self, mock_log):
        with patch('domain_tag_management.views.tag_list.TagListSerializer') as mock_serializer:
            mock_serializer.side_effect = Exception("boom")
            self.client.force_authenticate(user=self.regular_user)
            self.client.get(self.list_tag_url)

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'LIST_TAG')
        self.assertEqual(kwargs['status_type'], 'error')
        self.assertEqual(kwargs['error_code'], 'LIST_TAG_FAILED')

    # ===========================================================
    # Exception path
    # ===========================================================

    @patch('domain_tag_management.views.tag_list.log_critical_event')
    @patch('domain_tag_management.views.tag_list.TagListSerializer')
    def test_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_tag_url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===========================================================
    # Method not allowed
    # ===========================================================

    def test_post_method_not_allowed(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.list_tag_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)