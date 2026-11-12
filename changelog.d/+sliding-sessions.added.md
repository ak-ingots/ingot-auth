The sliding lifetimes of the sessions: `AuthSlidingLifetime`, a session
living while used and expiring idle `AUTH_SESSION_IDLE_TTL` seconds, an
hour by default, `EXPIRED_IDLE`, and `AuthSlidingFixedLifetime`, sliding
and fixed, expiring by whichever comes first, as NIST SP 800-63B-4 and
OWASP ask for an overall timeout always. A sliding lifetime writes the
time a session is seen at, `seen_at` of `AuthSessionRecord`, by
`storage.sessions.touch()`, at most once per
`AUTH_SESSION_TOUCH_INTERVAL` seconds, five minutes by default; a
strategy tells it by `is_touch_due()`. A cached session past its
lifetime is found again in the storage before it closes, as another
process may have seen it since. The sessions of MongoDB opened by 0.1.0
are seen at their sign-in.
