from rest_framework import serializers
from identity.models import User, Role


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for assigning or changing a user's role.

    The role is identified by its ID and must reference an existing Role.

    Attributes:
        role (serializers.PrimaryKeyRelatedField):
            The ID of the role to assign to the user.
        role_name (serializers.CharField):
            The title of the assigned role. This field is read-only and is
            returned only as part of the serialized response.

    Example:
        >>> user = User.objects.get(pk=24)
        >>> serializer = UserRoleUpdateSerializer(
        ...     user,
        ...     data={'role': 5},
        ...     partial=True
        ... )
        >>> serializer.is_valid()
        True
        >>> serializer.validated_data
        {'role': <Role: سوپر ادمین>}

        >>> serializer.save()
        <User: nilan_m83>

        >>> serializer.data
        {
            'role': 5,
            'role_name': 'سوپر ادمین'
        }
    """

    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all()
    )

    role_name = serializers.CharField(
        source='role.title',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'role',
            'role_name',
        )