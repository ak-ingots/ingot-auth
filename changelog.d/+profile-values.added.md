The values of a profile: its tags and the values of its attributes, by the
ids of their registries, which an operator sets, the whole set each time,
`auth.profiles.op_set_tags` and `op_set_attr_values`, a tag or an attribute
out of its registry refused, a value of another type too; a change forgets
the callers of the profile. The flag `CAN_UPDATE` of `auth.profiles`,
`AuthProfilesPermissions`, which `auth.profiles.grp_managers` grants. On
the command line `auth profiles tags set <uid> <tag>…` and
`auth profiles attrs values set <uid> --value ID=VALUE`; over gRPC the service `Profiles`
of `ingot_auth.profiles.v1`, in `AuthGrpcProfilesBinding`, which
`AuthGrpcAdminBinding` takes. The storage `storage.profiles.values`,
`BaseAuthProfileValuesStorage`, in memory and in MongoDB, with its contract.
