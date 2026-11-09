"""The members of the groups: the memberships, the users bound to them."""

__all__ = (
    "AuthAddMember",
    "AuthListMemberGroups",
    "AuthListMembers",
    "AuthMembers",
    "AuthMembersPermissions",
    "AuthMembership",
    "AuthRemoveMember",
    "BaseAuthMembersStorage",
)

from ingots.puer import Factory, Unit

from .items import AuthMembership
from .operations import (
    AuthAddMember,
    AuthListMemberGroups,
    AuthListMembers,
    AuthRemoveMember,
)
from .permissions import AuthMembersPermissions
from .storage import BaseAuthMembersStorage


class AuthMembers(Unit):
    """
    The operations of the memberships; the memberships themselves are in
    the storage of the auth.
    """

    op_add = Factory(AuthAddMember)
    op_remove = Factory(AuthRemoveMember)
    op_list = Factory(AuthListMembers)
    op_list_groups = Factory(AuthListMemberGroups)
