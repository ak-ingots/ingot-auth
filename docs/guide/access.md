# Access

A signed-in user has what its groups grant, `grp_signed_in` first, a group of
the core every signed-in user is a member of, none stored, granting the
`CAN_SIGN_IN` of each method open; an application grants every signed-in
user more by its own `AuthSignedInGroup` in the slot. A caller that tells
no one has what the group `grp_anonymous` of the core grants, none stored
either: what anyone may of the auth, the flags of the sign-up and of the
sign-in, those of the methods open, the reading of the metadata; an
application grants anyone more, or less, by its own `AuthAnonymousGroup`.
A signed-in user is not a member of `grp_anonymous`: one its groups do not let
in uses what is open to anyone until it signs in, refused once it has. The
groups are
declared in the code, slots of the groups of the access, each granting by
its hook; the addons grant to a group as the application does, which
declares the class joining them when two of its bases hold the group:

```python
class AppAdminsGroup(ShopAdminsGroup, ArticlesAdminsGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | Permissions(
            AuthMembersPermissions.CAN_ADD | AuthMembersPermissions.CAN_REMOVE
        )


class AppGroupsUnit(ShopGroupsUnit, ArticlesGroupsUnit):
    admins = Slot(AppAdminsGroup)  # joins what the two grant to it
    editors = Slot(EditorsGroup)


class AppAccessUnit(AuthAccessUnit):
    groups = Slot(AppGroupsUnit)
```

## Members

The storage keeps the members of the groups only, added and removed by the
operations of `auth.access.members`, a group no source has granting
nothing. The command line runs them as the root, so the first
administrator is made there; then an administrator does the rest over
gRPC, the services `Groups` and `Members` of `AuthGrpcAccessBinding`:

```console
$ python -m app auth access groups list
$ python -m app auth access members add admins <uid>
```

A member added to a group or removed has it on its next request, signed in
still: the operations of the members forget its callers in the cache
({doc}`sessions`).
