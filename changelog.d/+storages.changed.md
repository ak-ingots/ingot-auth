The interfaces of the storages are in `ingot_auth.storages`, which depends on
no other part of the auth: `AuthStorage` with its transactions, the storage
of each subdomain and of each part of it, and what they keep and raise, the
profiles, the identities, the items of the registries, the sessions, the
records of the sign-ups and the memberships, with their errors. The
subdomains no more export them: `from ingot_auth.storages import AuthProfile`
in place of `from ingot_auth.profiles import AuthProfile`. The errors of what
a storage does not raise stay where they are raised, `AuthItemInvalidError`
in `ingot_auth.registry`, `AuthSessionExpiredError` in `ingot_auth.sessions`,
each on its base in `ingot_auth.storages`.
