# Profiles

A profile is its uid, what the rest of an application knows the user by,
and the time of its sign-up. What it holds besides is of two registries,
which an operator keeps: the tags, marks a profile has or has not, `beta`,
and the attributes, typed values, a first name, a birth date. Each is known
by its id, the same in every environment once created, and its name:

```console
$ python -m app auth profiles tags create --id 1 --name beta
$ python -m app auth profiles attrs create --id 1 --name first_name --type str
```

## Values

An operator sets the values of a profile, the whole set each time, so that
a script runs it twice safely: its tags, `auth.profiles.op_set_tags`, and the
values of its attributes, `op_set_attr_values`, by the ids of their
registries. A tag or an attribute out of its registry is refused, a value of
another type too; a profile of none has empty ones.

```console
$ python -m app auth profiles tags set 0f6c… 1 3
$ python -m app auth profiles attrs values set 0f6c… --value 1=Ann --value 2=2026-01-01T00:00:00+00:00
```

On the command line a value is read by the type of its attribute: `true` or
`false`, a number, a decimal, a time of ISO 8601 with its offset, a text.
Over gRPC, `SetProfileTags` and `SetProfileAttrValues` of the service
`Profiles` of `ingot_auth.profiles.v1`, in `AuthGrpcProfilesBinding`, which
`AuthGrpcAdminBinding` takes. `auth.profiles.grp_managers` grants the flag,
`CAN_UPDATE` of `auth.profiles`. A change forgets the callers of the
profile, as a change of its memberships does.
