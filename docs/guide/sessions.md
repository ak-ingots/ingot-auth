# Sessions

A session lives as the strategy of its lifetime says, which the
application declares, as the sessions have none. The core has three:

- `AuthSlidingLifetime`: a session lives while used, and expires idle
  `AUTH_SESSION_IDLE_TTL` seconds, `EXPIRED_IDLE`;
- `AuthFixedLifetime`: a session lives `AUTH_SESSION_TTL` seconds from the
  sign-in, however used, `EXPIRED_ABSOLUTE`;
- `AuthSlidingFixedLifetime`: both, whichever comes first.

```python
class AppSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthSlidingFixedLifetime)
```

Both limits are what the guides of the sessions ask for: every session
has an overall timeout, and an inactivity one besides but at the lowest
level of assurance.
[NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/aal) bounds
them by the level: 30 days overall at AAL1, no inactivity timeout
required; 24 hours and an hour idle at AAL2; 12 hours and 15 minutes at
AAL3. The
[OWASP cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
gives 15 to 30 minutes idle for an application of low risk, 2 to 5 for
one of high value. The defaults are 30 days overall,
`AUTH_SESSION_TTL`, and an hour idle, `AUTH_SESSION_IDLE_TTL`: an
application tunes them by its configs, per environment.

A sliding lifetime writes the time a session is seen at once per
`AUTH_SESSION_TOUCH_INTERVAL` seconds at most, five minutes by default,
not on every request: the idle limit is precise to that interval, which
stays well below it. An expired session closes on its next request, with
its reason, and the request is refused. A strategy of the application's
own extends `BaseAuthSessionLifetime`: a session of an operator living an
hour, the others a month.

## Callers

A request brings the token of its session, and
`auth.sessions.authenticate(token)` gives its caller, with the uid of the
profile and the permissions of its groups, from the cache. A member added
to a group or removed has it on its next request, signed in still: the
operations of the members forget its callers. A deploy changing what the
groups grant finds none of the callers formed before. A change made past
the operations, by hand in the database, shows past
`AUTH_SESSION_CACHE_TTL`.
