from rest_framework import serializers


class UserRefSerializer(serializers.Serializer):
    """
    A single user reference inside an add/remove list.
    """
    user_id = serializers.IntegerField()


class UserAddRefSerializer(serializers.Serializer):
    """
    A single user reference inside the add list.

    is_primary is optional; when omitted it defaults to False.
    Business rule (enforced in the view, not here, since bulk_create
    bypasses serializer-level validation): a user may have at most
    one active primary group.
    """
    user_id = serializers.IntegerField()
    is_primary = serializers.BooleanField(required=False, default=False)


class GroupUserAssignSerializer(serializers.Serializer):
    """
    Bulk add/remove payload for group membership.

    Example:
        {
            "add": [{"user_id": 1}, {"user_id": 2}],
            "remove": [{"user_id": 5}]
        }
    """
    add = UserAddRefSerializer(many=True, required=False, default=list)
    remove = UserRefSerializer(many=True, required=False, default=list)
