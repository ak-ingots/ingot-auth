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

## Attributes

A session keeps the values of its attributes, what it was opened on, as
the record of a sign-up does: the attributes are a registry of the
storage, each with its type and its source. The client gives the values
of the source `client`, its device, by their ids; the transport those of
the source `transport`, the IP, by their names, which the client can
never give. The registry tells what is kept: a transport gives what it
reads, and a value of no attribute of its name is dropped, so that an
application keeps the IP only once it registers it:

```console
$ python -m app auth sessions attrs create --uid 1 --name ip --type str --source transport
```

The name binds the attribute to the transport: renamed, it is given no
more. One of the name of another source or type is a mistake of the
registry: its value is dropped, with a warning in the log. The values of
the transport are those of the start of a flow, kept by its attempt to its
end. Over gRPC, a servicer of a method gives `ip`, the IP of the peer of
the call ({doc}`../contrib/transports`).

The values of the source `derived` the server derives from the others,
the place from the IP, by the strategy in the slot `deriver` of the
sessions, which the application declares, as the sessions have none: it
takes the values of the client and of the transport by their names, and
gives its own by theirs, kept as those of the transport are, once the
registry has them derived. `AuthNoSessionAttrsDeriver` derives none; an
application telling the place writes its own, on a base of GeoIP:

```python
class AppDeriver(BaseAuthSessionAttrsDeriver):
    @t.override
    async def _derive(self, attr_values):
        ip = attr_values.get("ip")
        country = geoip.country(ip) if isinstance(ip, str) else None
        return {"country": country} if country else {}


class AppSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthSlidingFixedLifetime)
    deriver = Slot(AppDeriver)
```

## Own sessions

A signed-in user lists its open sessions, `auth.sessions.op_list_own`, by
the time they opened, each with its public id, never its token, the values
of its attributes, the device and the place, the times it opened and was
seen at, and the current one marked; it revokes one, `op_revoke_own`, a
lost phone, closed `REVOKED`, or all but the current one,
`op_revoke_others`, which tells how many. A session of another, closed or
unknown, is not found, `AuthOwnSessionNotFoundError`, the caller signed in
still. `auth.grp_signed_in` grants the flags, `CAN_LIST_OWN` and
`CAN_REVOKE_OWN` of `auth.sessions`; an application takes them off by its
class of the group, a kiosk. Over gRPC, the service `Sessions` of
`ingot_auth.sessions.v1`, in `AuthGrpcSessionsBinding`.

## Callers

A request brings the token of its session, and
`auth.sessions.authenticate(token)` gives its caller, with the uid of the
profile and the permissions of its groups, from the cache. A member added
to a group or removed has it on its next request, signed in still: the
operations of the members forget its callers. A deploy changing what the
groups grant finds none of the callers formed before. A change made past
the operations, by hand in the database, shows past
`AUTH_SESSION_CACHE_TTL`.

## Sign-out

The caller signs out by `auth.sign_out.op_sign_out`, over gRPC
`SignOut.SignOut` of `ingot_auth.sign_out.v1`: its session closes,
`SIGNED_OUT`, kept, and its token works no more from the very next
request, the cache forgetting it once the storage keeps it closed. Any
caller may: one of no session, the anonymous one of a token closed,
expired or unknown, signs out of nothing, so that a client retries safely
and an attacker learns nothing. `AuthGrpcFlowsBinding` serves it with the
answers of the flows, `AuthGrpcSignOutBinding` apart.

## The record of the sign-ins

A session closed stays kept, with the time and the reason it closed: the
record of a sign-in. Who closed it, its own user signing out or revoking,
the server when it expired, the activity log tells, by the uid of the
session, `auth activities list --entity auth.sessions:<uid>`
({doc}`activities`). An operator reads the
sessions of a profile, `auth.sessions.op_list`, those open, or all of them
with the closed ones, by the time they opened, never a token nor its hash:

```console
$ python -m app auth sessions list 0f6c… --closed
```

Over gRPC, `ListSessions` of the service `Sessions`, which
`AuthGrpcAdminBinding` serves too. `auth.sessions.grp_admins` grants the
flag, `CAN_LIST` of `auth.sessions`; a user reads its own open sessions
alone.

## Revoking every session of a profile

An operator closes every open session of a profile, a stolen account,
`auth.sessions.op_revoke_all`, `REVOKED`, each in the activity log by the
operator, the tokens refused from the next request; it prints how many,
none of an unknown profile:

```console
$ python -m app auth sessions revoke-all 0f6c…
2
```

Over gRPC, `RevokeSessions` of the service `Sessions`, telling the count.
`auth.sessions.grp_admins` grants the flag, `CAN_REVOKE` of `auth.sessions`.

## Sweeping the expired sessions

A session expires when a request brings its token; one never brought again
stays open in the storage. `auth.sessions.op_sweep` closes every open
session the lifetime tells expired, with its reason, a page of the storage
at a time, each page in a transaction of its own, so a sweep stopped
halfway keeps what it closed; it prints how many. A schedule of the
application runs it, cron or a job, as `auth.system`, which the group
`auth.grp_system` grants the flag ({doc}`access`):

```console
$ python -m app auth sessions sweep
17
```

An admin sweeps over gRPC, `SweepSessions` of the service `Sessions`, its
uid in each record `expire` of the activity log.
`auth.sessions.grp_admins` grants the flag, `CAN_SWEEP` of `auth.sessions`.
A storage of the sessions gives the open ones in pages by their uid,
`get_all_open(after, limit)`.
