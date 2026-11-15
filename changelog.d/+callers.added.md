The group of every caller that tells no one, `auth.grp_anonymous`,
`AuthAnonymousGroup`, in the slot `grp_anonymous` of `AuthUnit`, none
stored, as `auth.grp_signed_in` is of every signed-in user: it grants what
anyone may of the auth, as its units tell it, the flags of the sign-up and
of the sign-in, those of the methods their toggles open, and the reading
of the metadata, `auth.metadata.get_anonymous_permissions()`; an
application grants anyone more, or less, by its own class in the slot.
`AuthProject` takes `AuthOperationsUnit`, whose `AuthCallersProvider`
gives the anonymous caller of the project,
`operations.callers.get_anonymous()`, what the group grants. A signed-in
user is not a member: it has what its groups grant alone. A membership of
`auth.grp_anonymous` is refused as one of `auth.grp_signed_in`, the message of
both `the group '<name>' keeps no members`.
