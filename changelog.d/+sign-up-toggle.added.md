The toggle of the sign-up, `AUTH_SIGN_UP_ENABLED`, on by default: off, no
one signs up by any method, and the metadata lists the sign-up of each
method closed. The flags the flows give the anonymous caller come from
their units, `auth.sign_up.get_anonymous_permissions()` and
`auth.sign_in.get_anonymous_permissions()`, as those of the methods do.
