The mailer of the auth, the slot `mailer` of `AuthUnit`, `BaseAuthMailer`
of `ingot_auth.mailers`, delivering an `AuthMail`, its address, subject
and text, the address and the text out of its `repr`. In memory,
`AuthMemoryMailer` of `ingot_auth.contrib.mailers.memory`, delivering
nothing and keeping the mail, `get_sent()`, for the tests and the addon
run on its own. `AuthMailerContract` tells what a backend guarantees, the
mail delivered as sent, read back by `get_delivered()` of its test case.
An application declares the mailer in the slot, as the storage and the
cache.
