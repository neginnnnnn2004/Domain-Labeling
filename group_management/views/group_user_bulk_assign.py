from django.db import transaction
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from identity.services import log_critical_event
from identity.permissions import IsAdminRole
from identity.models import Group, User, UserGroup

from group_management.serializers.group_user_bulk_assign import GroupUserAssignSerializer


class GroupUserAssignView(APIView):
    """
    Bulk assign/unassign users to/from a group (admin access).

    All operations are validated before any database changes are made.
    If validation fails, no changes are applied.
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_group(self, group_id):
        return Group.objects.filter(pk=group_id, deleted_at__isnull=True).first()

    @swagger_auto_schema(
        operation_description="""
        Bulk assign or unassign users to/from a group (admin access).

        - `add`: list of user IDs to assign to this group.
        - `remove`: list of user IDs to unassign from this group.

        All operations are validated before execution.
        If any operation fails, no changes are applied.

        Custom error codes:

        code 65: The requested group does not exist or has been deleted.
        code 60: Some of the submitted changes are invalid.
        """,
        manual_parameters=[
            openapi.Parameter(
                'group_id', openapi.IN_PATH,
                description="(ID) Group",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=GroupUserAssignSerializer,
        responses={
            200: "Changes were saved successfully.",
            400: "Bad Request (Code 60)",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found (Code 65)",
        }
    )
    def post(self, request, group_id):
        group = self.get_group(group_id)
        if not group:
            log_critical_event(
                action="GROUP_USER_ASSIGN",
                status_type='failed',
                request=request,
                user_id=request.user.id,
                error_code=65,
                extra={'group_id': group_id},
            )
            return Response({
                "error_code": 65,
                "message": {
                    "fa": "گروه مورد نظر یافت نشد.",
                    "en": "The requested group was not found."
                },
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = GroupUserAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "error_code": 60,
                "message": {
                    "fa": "اطلاعات ارسال شده نامعتبر است.",
                    "en": "The submitted data is invalid."
                },
                "detail": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        add_items = data.get("add", [])
        remove_items = data.get("remove", [])

        errors = []
        users_to_add = []
        memberships_to_remove = []

        seen_ids = set()

        # ---- Validate ADD ----
        for index, item in enumerate(add_items):
            user_id = item.get("user_id")
            is_primary = item.get("is_primary", False)

            if user_id in seen_ids:
                errors.append({
                    "operation": "add",
                    "index": index,
                    "user_id": user_id,
                    "fa": f"کاربر «{user_id}» بیش از یک‌بار در درخواست تکرار شده است.",
                    "en": f"User «{user_id}» is duplicated in the request."
                })
                continue

            target_user = User.objects.filter(
                pk=user_id,
                deleted_at__isnull=True
            ).first()

            if not target_user:
                errors.append({
                    "operation": "add",
                    "index": index,
                    "user_id": user_id,
                    "fa": f"کاربر «{user_id}» یافت نشد.",
                    "en": f"User «{user_id}» was not found."
                })
                continue

            already_member = UserGroup.objects.filter(
                user=target_user,
                group=group,
                deleted_at__isnull=True
            ).exists()

            if already_member:
                errors.append({
                    "operation": "add",
                    "index": index,
                    "user_id": user_id,
                    "fa": f"کاربر «{user_id}» از قبل عضو این گروه است.",
                    "en": f"User «{user_id}» is already assigned to this group."
                })
                continue

            # ---- Business rule: at most one active primary group ----
            # bulk_create bypasses UserGroupSerializer.validate(), so this
            # rule must be enforced here explicitly.
            if is_primary:
                has_other_primary = UserGroup.objects.filter(
                    user=target_user,
                    is_primary=True,
                    deleted_at__isnull=True
                ).exists()

                if has_other_primary:
                    errors.append({
                        "operation": "add",
                        "index": index,
                        "user_id": user_id,
                        "fa": f"کاربر «{user_id}» در حال حاضر یک گروه اصلی دارد.",
                        "en": f"User «{user_id}» already has a primary group."
                    })
                    continue

            seen_ids.add(user_id)
            users_to_add.append((target_user, is_primary))

        # ---- Validate REMOVE ----
        for index, item in enumerate(remove_items):
            user_id = item.get("user_id")

            if user_id in seen_ids:
                errors.append({
                    "operation": "remove",
                    "index": index,
                    "user_id": user_id,
                    "fa": f"کاربر «{user_id}» بیش از یک‌بار در درخواست تکرار شده است.",
                    "en": f"User «{user_id}» is duplicated in the request."
                })
                continue

            membership = UserGroup.objects.filter(
                user_id=user_id,
                group=group,
                deleted_at__isnull=True
            ).first()

            if not membership:
                errors.append({
                    "operation": "remove",
                    "index": index,
                    "user_id": user_id,
                    "fa": f"کاربر «{user_id}» عضو این گروه نیست.",
                    "en": f"User «{user_id}» does not belong to this group."
                })
                continue

            seen_ids.add(user_id)
            memberships_to_remove.append(membership)

        if errors:
            log_critical_event(
                action="GROUP_USER_ASSIGN",
                status_type='failed',
                request=request,
                user_id=request.user.id,
                error_code=60,
                extra={'group_id': group.id, 'errors': errors},
            )
            return Response({
                "error_code": 60,
                "message": {
                    "fa": "برخی از تغییرات معتبر نیستند.",
                    "en": "Some changes are invalid."
                },
                "detail": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # ---- Apply changes atomically ----
        with transaction.atomic():
            if users_to_add:
                UserGroup.objects.bulk_create([
                    UserGroup(
                        user=target_user,
                        group=group,
                        assigned_by=request.user,
                        is_primary=is_primary,
                    )
                    for target_user, is_primary in users_to_add
                ])

            if memberships_to_remove:
                now = timezone.now()
                for membership in memberships_to_remove:
                    membership.deleted_at = now
                UserGroup.objects.bulk_update(memberships_to_remove, ['deleted_at'])

        log_critical_event(
            action="GROUP_USER_ASSIGN",
            status_type='success',
            request=request,
            user_id=request.user.id,
            extra={
                'group_id': group.id,
                'added_count': len(users_to_add),
                'removed_count': len(memberships_to_remove),
            },
        )

        return Response({
            "message": {
                "fa": "تغییرات با موفقیت اعمال شد.",
                "en": "Changes were applied successfully."
            },
            "result": {
                "added": len(users_to_add),
                "removed": len(memberships_to_remove),
            }
        }, status=status.HTTP_200_OK)
