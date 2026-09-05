from django.urls import path

from group_management.views.group_list import ListOfGroupsView
from group_management.views.group_register import GroupRegisterView
from group_management.views.group_detail import GroupDetailOREditView
from group_management.views.group_user_bulk_assign import GroupUserAssignView
from group_management.views.group_domains import GroupDomainView
from group_management.views.group_members import GroupMembersListView, GroupMemberDeleteView
from group_management.views.group_domain_assign import GroupDomainAssignView

urlpatterns = [
    # Group CRUD (not scoped to a specific group_id path segment)
    path('list/', ListOfGroupsView.as_view(), name='list-of-groups'),
    path('create/', GroupRegisterView.as_view(), name='group-register'),
    path('<int:pk>/detail/', GroupDetailOREditView.as_view(), name='group-detail'),

    # Everything scoped to a single group uses the same "group/<id>/..." prefix
    path('group/<int:group_id>/domains/', GroupDomainView.as_view(), name='group-domains'),
    path('group/<int:group_id>/domains/assign/', GroupDomainAssignView.as_view(), name='group-domain-assign'),
    path('group/<int:group_id>/members/', GroupMembersListView.as_view(), name='group-members-get'),
    path('group/<int:group_id>/members/<int:user_id>/', GroupMemberDeleteView.as_view(), name='group-member-delete'),
    path('group/<int:group_id>/users/assign/', GroupUserAssignView.as_view(), name='group-user-assign'),
]
