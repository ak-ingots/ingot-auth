The access, `auth.access`: the groups of the users, declared in the code
as slots of `AuthGroups`, each granting by its hook `_get_permissions()`,
the classes of its MRO adding their own; the memberships of the users,
added, removed and listed by the operations of `AuthMembers`, kept in
`storage.access.members`, in memory and checked by
`AuthMembersStorageContract`; and `AuthGroupsGrants`, the permissions of
a user from its groups. The operations of the groups and the members
require the permissions `auth.access.groups` and `auth.access.members`.
