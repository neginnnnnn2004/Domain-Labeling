from rest_framework import serializers
from identity.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializes a group with all its model fields.

    Administrative and system-managed fields are read-only and cannot be
    set through the API; they are populated automatically by the system.

    Enforces the business rule that a group's title (case-insensitive and
    whitespace-trimmed) must remain unique among groups. On update, the
    instance being edited is excluded from this check, so saving a group
    with its own unchanged title does not raise a duplicate-title error.

    Attributes:
        All writable fields of the ``Group`` model (e.g. title,
        description, is_active, etc.).

    Read-only fields (auto-managed by the system):
        assigned_by: The user who assigned/created the group.
        deleted_at: Soft-delete timestamp.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        code: A stable machine-readable code for the group, derived
            automatically from its normalized title.

    Raises:
        serializers.ValidationError: If a group with the same normalized
            title already exists (excluding the instance itself on update).

    Example:
        >>> serializer = GroupSerializer(group)
        >>> serializer.data
        {'id': 1, 'code': 274813652910, 'title': 'Admins',
         'title_normalized': 'admins', 'description': '...',
         'is_active': True, 'deleted_at': None}
    """
    class Meta:
        model = Group
        fields = "__all__"
        read_only_fields = ["assigned_by", "deleted_at", "created_at", "updated_at", "code"]

    def validate_title(self, value):
        normalized = value.strip().lower()
        qs = Group.objects.filter(title_normalized=normalized)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                "fa": "این عنوان یا مشابه آن قبلاً ثبت شده است.",
                "en": "This title or a similar one has already been registered."
            })
        return value