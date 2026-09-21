from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from identity.models import User, Role, Tag


class TagUpdateViewTest(APITestCase):

    def setUp(self):
        self.admin_role = Role.objects.create(code='admin', title='ادمین', level=100, is_system=True)
        self.regular_role = Role.objects.create(code='regular', title='کاربر معمولی', level=20, is_system=True)

        self.admin_user = User.objects.create_user(
            username="admin_dara", password="pass123", email="admin@test.com",
            phone="09111111111", status="active", role=self.admin_role,
        )
        self.regular_user = User.objects.create_user(
            username="normal_user", password="pass123", email="normal@test.com",
            phone="09333333333", status="active", role=self.regular_role,
        )

        self.tag_one = Tag.objects.create(title="urgent", description="...")
        self.tag_two = Tag.objects.create(title="important", description="...")
        self.deleted_tag = Tag.objects.create(title="old-tag", description="...")
        self.deleted_tag.deleted_at = timezone.now()
        self.deleted_tag.is_active = False
        self.deleted_tag.save(update_fields=["deleted_at", "is_active"])

        self.tag_url = lambda pk: reverse('tag-detail', kwargs={'pk': pk})

    # ===========================================================
    # PATCH — permission
    # ===========================================================

    def test_admin_can_edit_tag(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "renamed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_can_not_edit_tag(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "renamed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_can_not_edit_tag(self):
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "renamed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pending_admin_can_not_edit_tag(self):
        self.admin_user.status = 'pending'
        self.admin_user.save()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "renamed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ===========================================================
    # PATCH — not found
    # ===========================================================

    def test_edit_nonexistent_tag_returns_404_with_code_55(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(99999), {"title": "renamed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 55)

    # ===========================================================
    # PATCH — soft-deleted tag (رفتار فعلی: پیدا و قابل‌ویرایش می‌شود)
    # ===========================================================

    def test_edit_soft_deleted_tag_currently_succeeds(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.tag_url(self.deleted_tag.id), {"title": "revived-tag"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ===========================================================
    # PATCH — validation
    # ===========================================================

    def test_edit_with_invalid_data_returns_error_code_10(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 10)

    def test_edit_with_duplicate_title_returns_error_code_11(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.tag_url(self.tag_one.id), {"title": "important"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 11)

    def test_edit_keeping_same_title_succeeds(self):
        # چون سریالایزر instance رو exclude می‌کنه، خودِ تگ نباید duplicate بشه
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.tag_url(self.tag_one.id), {"title": "urgent", "description": "updated desc"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ===========================================================
    # PATCH — success
    # ===========================================================

    def test_edit_updates_tag_in_database(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            self.tag_url(self.tag_one.id), {"title": "renamed-urgent"}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.tag_one.refresh_from_db()
        self.assertEqual(self.tag_one.title, "renamed-urgent")

    # ===========================================================
    # PATCH — logging
    # ===========================================================

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    def test_delete_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(self.tag_url(self.tag_one.id))

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'DELETE_TAG')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['tag_id'], self.tag_one.id)

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    def test_delete_not_found_logs_error_code_55(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(self.tag_url(99999))

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 55)

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    @patch('domain_tag_management.views.tag_edit_or_delete.TagRegisterSerializer')
    def test_patch_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "x"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    @patch('domain_tag_management.views.tag_edit_or_delete.timezone')
    def test_delete_returns_500_on_unexpected_exception(self, mock_timezone, mock_log):
        mock_timezone.now.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===========================================================
    # DELETE — permission
    # ===========================================================

    def test_admin_can_delete_tag(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_can_not_delete_tag(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_can_not_delete_tag(self):
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ===========================================================
    # DELETE — not found
    # ===========================================================

    def test_delete_nonexistent_tag_returns_404_with_code_55(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error_code'], 55)

    # ===========================================================
    # DELETE — success
    # ===========================================================

    def test_delete_sets_deleted_at_and_is_active_false(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.tag_one.refresh_from_db()
        self.assertIsNotNone(self.tag_one.deleted_at)
        self.assertFalse(self.tag_one.is_active)

    # ===========================================================
    # DELETE — از‌قبل حذف‌شده (رفتار فعلی: بدون خطا دوباره حذف می‌شود)
    # ===========================================================

    def test_delete_already_deleted_tag_currently_succeeds_again(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(self.deleted_tag.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ===========================================================
    # DELETE — logging
    # ===========================================================

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    def test_delete_success_logs_correct_params(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(self.tag_url(self.tag_one.id))

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['action'], 'DELETE_TAG')
        self.assertEqual(kwargs['status_type'], 'success')
        self.assertEqual(kwargs['extra']['tag_id'], self.tag_one.id)

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    def test_delete_not_found_logs_error_code_55(self, mock_log):
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(self.tag_url(99999))

        _, kwargs = mock_log.call_args
        self.assertEqual(kwargs['error_code'], 55)

    # ===========================================================
    # Exception (بعد از اضافه کردن try/except به هر دو متد)
    # ===========================================================

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    @patch('domain_tag_management.views.tag_edit_or_delete.TagRegisterSerializer')
    def test_patch_returns_500_on_unexpected_exception(self, mock_serializer, mock_log):
        mock_serializer.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.tag_url(self.tag_one.id), {"title": "x"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('domain_tag_management.views.tag_edit_or_delete.log_critical_event')
    @patch('domain_tag_management.views.tag_edit_or_delete.timezone')
    def test_delete_returns_500_on_unexpected_exception(self, mock_timezone, mock_log):
        mock_timezone.now.side_effect = Exception("boom")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===========================================================
    # Method not allowed
    # ===========================================================

    def test_get_method_not_allowed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.tag_url(self.tag_one.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)