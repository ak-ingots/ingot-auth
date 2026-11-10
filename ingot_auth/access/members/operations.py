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

from .items import AuthMembership
from .permissions import AuthMembersPermissions
from .storage import BaseAuthMembersStorage

if t.TYPE_CHECKING:
    from ingots.defaults.operations import OperationMetadata

    from ingot_auth.project import AuthProject


class BaseAuthMembersOperation[ParametersType, ResultType](
    BaseOperation[ParametersType, ResultType]
):
    """
    An operation of the memberships: the group is one of a source, the uid
    of a profile.
    """

    project: "AuthProject"

    @t.final
    def _get_storage(self) -> BaseAuthMembersStorage:
        return self.project.auth.storage.access.members

    @t.final
    def _check_group(self, name: str) -> None:
        """:raises AuthGroupNotFoundError: no group has the name."""
        self.project.auth.access.groups.get(name)

    @t.final
    async def _check_uid(self, uid: str) -> None:
        """:raises AuthProfileNotFoundError: no profile has the uid."""
        await self.project.auth.storage.profiles.get(uid)


class AuthAddMemberOperation(BaseAuthMembersOperation[AuthMembership, None]):
    """
    Adds a user to a group; a member already stays one.

    :raises AuthGroupNotFoundError: no group has the name.
    :raises AuthProfileNotFoundError: no profile has the uid.
    """

    PERMISSIONS = Permissions(AuthMembersPermissions.CAN_ADD)

    @t.override
    async def _run(
        self, parameters: AuthMembership, metadata: "OperationMetadata"
    ) -> None:
        self._check_group(parameters.group)
        await self._check_uid(parameters.uid)
        await self._get_storage().add(parameters)


class AuthRemoveMemberOperation(BaseAuthMembersOperation[AuthMembership, None]):
    """
    Removes a user from a group; one not a member is no error.

    :raises AuthGroupNotFoundError: no group has the name.
    :raises AuthProfileNotFoundError: no profile has the uid.
    """

    PERMISSIONS = Permissions(AuthMembersPermissions.CAN_REMOVE)

    @t.override
    async def _run(
        self, parameters: AuthMembership, metadata: "OperationMetadata"
    ) -> None:
        self._check_group(parameters.group)
        await self._check_uid(parameters.uid)
        await self._get_storage().remove(parameters)


class AuthListMembersOperation(BaseAuthMembersOperation[str, tuple[str, ...]]):
    """
    The uids of the members of a group, sorted.

    :raises AuthGroupNotFoundError: no group has the name.
    """

    PERMISSIONS = Permissions(AuthMembersPermissions.CAN_READ)

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

    PERMISSIONS = Permissions(AuthMembersPermissions.CAN_READ)

    @t.override
    async def _run(
        self, parameters: str, metadata: "OperationMetadata"
    ) -> tuple[str, ...]:
        await self._check_uid(parameters)
        return await self._get_storage().get_groups(parameters)
