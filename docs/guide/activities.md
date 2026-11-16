# Activities

The auth keeps a log of every change of state of its entities, by
[ADR 0015](https://github.com/ak-ingots/ingots-libs/blob/main/docs/adr/0015-keep-an-activity-log-in-each-addon.md):
who changed what and when, written by the operation of the change, in its
transaction. A read is never recorded, nor a refusal.

A record tells its actor, `who`, the uid of the caller, `root` on the
command line, `auth.system` for what the server does by itself, and the
session of the caller, `session_uid`, none of a caller of none; its
`action`, create, update, delete, or a verb of the domain, `bind`,
`sign_in`; the type of its entity, the full name of its unit,
`auth.profiles.tags`, and its id; its `context`, what the change was, the
attributes the code of its time wrote, none for many: a tag created tells
nothing more, an attribute its name and its type; the uid of its run, of
the request or of a job; its time. A record stays as it was written: a
reader assumes no attribute of a type of entity, and shows the set each
record has.

## A failure to write it

What a failure to write a record does is a strategy in the slot `failure`
of `auth.activities`, which the application declares:

```python
class AppActivitiesUnit(AuthActivitiesUnit):
    failure = Slot(AuthStrictActivityFailure)
```

`AuthStrictActivityFailure` fails the change with the error, the
transaction rolled back, so that no change goes without its record;
`AuthSwallowActivityFailure` logs it at `ERROR`, with the record, and lets
the change through. `python -m ingot_auth` is strict.

## The auditors

The auditors read the log, the members of `auth.activities.grp_auditors`,
by the flag `CAN_READ` of `auth.activities`, filtered by the entity, the
actor, its session, the action and a span of time, the newest first:

```console
$ python -m app auth activities list --entity auth.profiles.tags:1 --limit 20
2026-11-15T12:00:00+00:00	root	-	create	auth.profiles.tags	1	9f2c…
```

Over gRPC, `ListActivities` of the service `Activities` of
`ingot_auth.activities.v1`, in `AuthGrpcActivitiesBinding`, which
`AuthGrpcAdminBinding` takes; its context a struct, a decimal and a time in
it as texts.

## Recording a change

An operation of the auth, or of an addon of it, records its change in its
transaction, its unit giving the type of the entity, a context if it needs
one, a dataclass extending `AuthActivityContext`, never a secret in it:

```python
async with self.project.auth.storage.transaction():
    await storage.create(attr)
    await self.project.auth.activities.record(
        self.parent,
        str(attr.uid),
        AuthActivityAction.CREATE,
        metadata,
        context=AuthAttrCreated(name=attr.name, type=attr.type.value),
    )
```

## What the core records

| Entity | Action | Context |
|---|---|---|
| `auth.profiles` | `create`, by a sign-up | the method, the kind of its identifier |
| `auth.profiles` | `bind`, the identifier of a sign-up | its kind, never its value |
| `auth.profiles` | `update`, the tags set | `tag_uids` |
| `auth.profiles` | `update`, the values set | `attr_values`, by the ids of the attributes |
| `auth.sessions` | `sign_in` | the uid of the profile, the method |
| `auth.sessions` | `sign_out`, `revoke` | none |
| `auth.sessions` | `expire`, by `auth.system`, or by the caller of a sweep | the reason |
| `auth.access.members` | `bind`, `unbind` a profile, the uid | the group |
| the registries | `create`, `update` renamed, `delete` | an attribute created its name, type and source, renamed its name |
| `auth.sessions.presets` | `bind`, `unbind` an attribute | its id, whether required |

A session expiring is closed by the server, `auth.system`, in a run of its own,
which the line of the log of the server tells: `the session … expired, …,
run …`; a sweep closes those expired in its run, by its caller.
