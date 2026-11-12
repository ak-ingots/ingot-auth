The method of an email and a code is whole: `AuthEmailCodeMethod`, no
more `BaseAuthEmailCodeMethod`, which an application declared with its
own `_send_code()`. It builds its mail, a plain text in English, by
`_build_code_mail()` and `_build_denial_mail()`, which a subclass
overrides to change it, and sends it by the mailer of the auth in the
background, `AuthSendCodeOperation` and `AuthSendDenialOperation` in its
slots `op_send_code` and `op_send_denial`, run by the dispatcher of the
auth, so that a start replies at once, for an email bound and one not
alike: an application taking the method declares the dispatcher and the
mailer of its auth. A sign-in by email checks at its start that the
profile may sign in by the method: one that may not is asked for a code
all the same, none sent, and its email gets the word that the way is
closed.
