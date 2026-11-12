A change of the groups of a user shows on its next request, signed in
still: adding a member to a group and removing one forget the callers of
its open sessions in the cache, `auth.sessions.forget_callers(uid)`, the
sessions kept, found by `storage.sessions.get_open(uid)`. A caller is cached
by the hash of its token and the digest of the groups,
`auth.access.groups.get_digest()`, computed once: a deploy changing what
the groups grant finds none of the callers formed before.
`cache.callers` takes the digest with the hash.
