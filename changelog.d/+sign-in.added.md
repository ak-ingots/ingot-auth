The sign-in, `auth.sign_in`, `op_start` and `op_answer`, as the sign-up
goes, over a base of the flows they share, `BaseAuthFlowOperation` of
`ingot_auth.methods`: a method verifies, in one step or after the answers to
a challenge, the sign-in finds the profile bound to what it verified, an
identifier bound to none refused as a wrong secret, checks the profile may
sign in by the method, `AuthMethodDeniedError` otherwise, and opens a
session, `AuthSignedIn` giving its token once and its id. It requires
`CAN_SIGN_IN` of `auth.sign_in`, `AuthSignInPermissions`, and the
`CAN_SIGN_IN` of the method. The group `signed_in` of the core,
`AuthSignedInGroup`, has every signed-in user, none stored, refused by the
operations of the members, and grants the `CAN_SIGN_IN` of each method open,
an application adding what it grants every signed-in user by its own class
in the slot. `auth.sessions.open()` gives `AuthSessionToken`, the token
and the id of the session.
