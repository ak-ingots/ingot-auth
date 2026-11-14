Moved on to ingots 0.34, ingot-grpcio 0.13 and ingot-pymongo 0.14. The
flags of the permissions take no `domain=` now: each enum is bound by the
slot `permissions` of its unit, a `PermissionsSlot`, the unit an
`OperationsOwner`, its domain the full name of the unit, the same names as
before, `auth.profiles.tags`, `auth.methods.nickname`. The operations
declare no constant `PERMISSIONS`: each builds its permissions by its hook
`_get_permissions()`, through the permissions of its unit, its parent; a
method builds its flags so in its `_get_<flow>_permissions()`,
`self.permissions(self.permissions.flags.CAN_SIGN_UP)`. The storages, the
caches, the dispatcher and the mailer in memory take no project in their
`__init__`.
