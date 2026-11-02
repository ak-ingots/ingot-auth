The sign-up, by methods in steps. A method, a slot of `AuthMethods`,
verifies who it is: each step ends with a challenge for the client to
answer or with the verified subject, and an attempt keeps the flow in the
cache between the steps, taken once, with a limit of refused answers
(`AUTH_ATTEMPT_TTL`, `AUTH_ATTEMPT_MAX_FAILURES`). The sign-up then binds
the subject to a new profile and keeps the record of what it happened on,
the values of the attributes of the session the client gave, checked to
be the client's. `AuthStartSignUp` and `AuthAnswerSignUp` require
`CAN_SIGN_UP` of `auth.sign_up`. The profiles, the identities, the records
and the attempts in memory, with their contracts; `AuthTestingMethod` in
`ingot_auth.testing.methods` for the tests of applications.
