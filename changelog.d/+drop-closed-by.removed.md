`closed_by` of a session, of `AuthSessionRecord` and `AuthSessionInfo`: the
activity log tells who closed a session, by its id, its user signing out or
revoking, the server when it expired. A storage of the sessions takes no
`closed_by` in `_close()`; `auth.sessions.close()` takes none; the field of
`SessionRecord` of `ingot_auth.sessions.v1` is reserved; `auth sessions
list` prints no closer. A session of MongoDB keeps the field it had, read
no more.
