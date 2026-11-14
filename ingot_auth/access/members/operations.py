"""The operations of the memberships."""

__all__ = (
    "AuthAddMemberOperation",
    "AuthListMemberGroupsOperation",
    "AuthListMembersOperation",
    "AuthRemoveMemberOperation",
    "BaseAuthMembersOperation",
)

import typing as t

from ingots.defaults.operations import BaseOperation, Permissions

from ingot_auth.storages import AuthMembership, BaseAuthMembersStorage

from ..groups import AuthGroupNotFoundError

if t.TYPE_CHECKING:
    from . import AuthMembersUnit
    from ingots.defaults.operations import OperationMetadata

    from ingot_auth.project import AuthProject


class BaseAuthMembersOperation[ParametersType, ResultType](
    BaseOperation[ParametersType, ResultType]
):
    """
    An operation of the memberships: the group is one of a source, but
    ``grp_anonymous`` and ``grp_signed_in``, which keep none; the uid of a
    profile.
    """

    project: "AuthProject"

    @t.final
    def _get_storage(self) -> BaseAuthMembersStorage:
        return self.project.auth.storage.access.members

    @t.final
    def _check_group(self, name: str) -> None:
        """
        :raises AuthGroupNotFoundError: no group has the name, or it is
            ``grp_anonymous`` or ``grp_signed_in``, which keep none.
        """
        groups = self.project.auth.access.groups
        if groups.get(name) in (groups.grp_anonymous, groups.grp_signed_in):
            raise AuthGroupNotFoundError.for_members(name)

    @t.final
    async def _check_uid(self, uid: str) -> None:
        """:raises AuthProfileNotFoundError: no profile has the uid."""
        await self.project.auth.storage.profiles.get(uid)


class AuthAddMemberOperation(BaseAuthMembersOperation[AuthMembership, None]):
    """
    Adds a user to a group; a member already stays one. The callers of the
    user are forgotten in the cache: its next request has the group.

    :raises AuthGroupNotFoundError: no group has the name, or it is
        ``grp_anonymous`` or ``grp_signed_in``, which keep none.
    :raises AuthProfileNotFoundError: no profile has the uid.
    """

    parent: "AuthMembersUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_ADD)

    @t.override
    async def _run(
        self, parameters: AuthMembership, metadata: "OperationMetadata"
    ) -> None:
        self._check_group(parameters.group)
        await self._check_uid(parameters.uid)
        await self._get_storage().add(parameters)
        await self.project.auth.sessions.forget_callers(parameters.uid)


class AuthRemoveMemberOperation(BaseAuthMembersOperation[AuthMembership, None]):
    """
    Removes a user from a group; one not a member is no error. The callers
    of the user are forgotten in the cache: its next request has the group
    no more.

    :raises AuthGroupNotFoundError: no group has the name, or it is
        ``grp_anonymous`` or ``grp_signed_in``, which keep none.
    :raises AuthProfileNotFoundError: no profile has the uid.
    """

    parent: "AuthMembersUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_REMOVE)

    @t.override
    async def _run(
        self, parameters: AuthMembership, metadata: "OperationMetadata"
    ) -> None:
        self._check_group(parameters.group)
        await self._check_uid(parameters.uid)
        await self._get_storage().remove(parameters)
        await self.project.auth.sessions.forget_callers(parameters.uid)


class AuthListMembersOperation(BaseAuthMembersOperation[str, tuple[str, ...]]):
    """
    The uids of the members of a group, sorted.

    :raises AuthGroupNotFoundError: no group has the name, or it is
        ``grp_anonymous`` or ``grp_signed_in``, which keep none.
    """

    parent: "AuthMembersUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)

    @t.override
    async def _run(
        self, parameters: str, metadata: "OperationMetadata"
    ) -> tuple[str, ...]:
        self._check_group(parameters)
        return await self._get_storage().get_uids(parameters)


class AuthListMemberGroupsOperation(BaseAuthMembersOperation[str, tuple[str, ...]]):
    """
    The names of the groups a user is added to, sorted, those of a group
    no source has any more among them, granting nothing.

    :raises AuthProfileNotFoundError: no profile has the uid.
    """

    parent: "AuthMembersUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)

    @t.override
    async def _run(
        self, parameters: str, metadata: "OperationMetadata"
    ) -> tuple[str, ...]:
        await self._check_uid(parameters)
        return await self._get_storage().get_groups(parameters)
