The secrets of the identities: a method gives one with the verified
subject, the hash of a password, say, and the sign-up keeps it in
`profile.secrets` of the storage, in its transaction; in memory, with its
contract. A method starts each flow by a hook of its own,
`_start_sign_up` and `_start_sign_in`, and takes those it overrides,
refusing the others with `AuthMethodUnsupportedError`.
