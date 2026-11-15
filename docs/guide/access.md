# Access

A signed-in user has what its groups grant, `auth.grp_signed_in` first, a group
of the core every signed-in user is a member of, none stored, granting the
`CAN_SIGN_IN` of each method open; an application grants every signed-in
user more by its own `AuthSignedInGroup` in the slot `grp_signed_in` of
its auth. A caller that tells no one has what the group `auth.grp_anonymous`
of the core grants, none stored either: what anyone may of the auth, the
flags of the sign-up and of the sign-in, those of the methods open, the
reading of the metadata; an application grants anyone more, or less, by
its own `AuthAnonymousGroup` in the slot `grp_anonymous`. A signed-in user
is not a member of `auth.grp_anonymous`: one its groups do not let in uses
what is open to anyone until it signs in, refused once it has.

## Groups

The groups are declared in the code, each in a slot of a unit of its
domain, prefixed `grp_`, as the operations take `op_` and the commands
`cmd_`. A unit owning groups extends `AuthGroupsOwner`; the groups of a
project are found from it down the owners alone, as its commands are down
its units of the command line, a plain unit and everything in it staying
out. The name of a group is its full name, where it is, `shop.grp_buyers`,
as the domain of the permissions of a unit is its full name: the scripts
and the memberships name it, and a group moved is renamed. A group grants
by its hook, each class adding to `super()`, building the masks of a unit by
its permissions:

```python
class ShopBuyersGroup(AuthGroup):
    parent: "ShopUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return super()._get_permissions() | permissions(permissions.flags.CAN_BUY)


class ShopUnit(AuthGroupsOwner, OperationsOwner, Unit):
    class Flags(PermissionFlags):
        CAN_BUY = 1 << 0

    permissions = PermissionsSlot(Flags)

    grp_buyers = Slot(ShopBuyersGroup)  # shop.grp_buyers
```

A class in no slot is a mixin of what it grants: an addon grants to a group
of the application by one, and the application declares the group joining
them in a unit of its own:

```python
class AppAdminsGroup(ShopAdminsGroup, ArticlesAdminsGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        members = self.project.auth.access.members.permissions
        return super()._get_permissions() | members(
            members.flags.CAN_ADD, members.flags.CAN_REMOVE
        )


class AppUnit(AuthGroupsOwner):
    grp_admins = Slot(AppAdminsGroup)  # app.grp_admins


class AppProject(AuthProject):
    app = Slot(AppUnit)
```

A group in a slot of `AuthGroupsUnit`, which finds the groups and holds
none, is refused when its class is created. The core declares the groups of
the work of its registries:

| Group | Grants |
|---|---|
| `auth.profiles.grp_consumers` | reading the tags and the attributes of the profiles |
| `auth.profiles.grp_managers` | creating, reading, updating and deleting them |
| `auth.sessions.grp_consumers` | reading the attributes and the presets of the sessions |
| `auth.sessions.grp_managers` | creating, reading, renaming and deleting them, binding none |
| `auth.sessions.grp_admins` | all a manager does, and binding the attributes to the presets |

## Members

The storage keeps the members of the groups only, added and removed by the
operations of `auth.access.members`, a group no source has granting
nothing. The command line runs them as the root, so the first
administrator is made there; then an administrator does the rest over
gRPC, the services `Groups` and `Members` of `AuthGrpcAccessBinding`:

```console
$ python -m app auth access groups list
$ python -m app auth access members add auth.profiles.grp_managers <uid>
```

A member added to a group or removed has it on its next request, signed in
still: the operations of the members forget its callers in the cache
({doc}`sessions`).
