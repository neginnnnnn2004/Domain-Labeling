from rest_framework import serializers


class DomainRefSerializer(serializers.Serializer):
    """
    Reference to a domain by name, used for bulk assign/unassign
    operations within a group.
    """
    domain_name = serializers.CharField()


class GroupDomainAssignSerializer(serializers.Serializer):
    """
    Serializer for bulk assigning/unassigning domains to/from a group.

    Fields:
        add:
            List of domains to assign to this group.

        remove:
            List of domains to unassign from this group
            (their `group` field is set to null).

    Intentional design note:
        Both `add` and `remove` are optional (`required=False`) with a
        default of an empty list. This means a request with an empty
        body (`{}`), or with `add`/`remove` explicitly set to `[]`, is
        considered VALID input — not an error. The view treats it as a
        no-op: no domains are added or removed, and it responds with
        200 OK and `{"added": 0, "removed": 0}`.

        This is deliberate, not a bug: it keeps the endpoint idempotent
        and simple for callers that always send both keys (even when
        one or both are empty) without needing extra client-side
        branching. Do not add a `validate()` that rejects an empty
        add/remove combination unless this behavior is explicitly
        revisited.
    """
    add = DomainRefSerializer(many=True, required=False, default=list)
    remove = DomainRefSerializer(many=True, required=False, default=list)
