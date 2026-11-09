The access on the command line, run as the root: `auth access groups
list`, `auth access members add|remove <group> <uid>`, `list <group>`
and `list-groups <uid>`, so that the first administrator is made there.
Over gRPC, the services `Groups` and `Members` of
`ingot_auth.access.groups.v1` and `ingot_auth.access.members.v1`, in
`AuthGrpcAccessBinding`, part of `AuthGrpcAdminBinding`; an unknown
group and a uid of no profile are `NOT_FOUND`, the reasons
`GROUP_NOT_FOUND` and `PROFILE_NOT_FOUND`.
