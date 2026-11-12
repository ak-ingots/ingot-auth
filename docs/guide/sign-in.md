# Sign-in

A sign-in finds the profile bound to what the method verified, checks the
profile may sign in by the method, its `CAN_SIGN_IN` from the groups,
`AuthMethodDeniedError` otherwise, and opens a session, giving its token
once, in one step or after the answers to a challenge, as a sign-up goes:

```python
start = AuthStartSignInParameters(
    method="nickname",
    parameters=AuthNicknameStart(nickname="alice", password="..."),
)
result = await project.operations.runner.run(
    project.auth.sign_in.op_start, start, metadata
)
if isinstance(result, AuthSignedIn):
    token = result.token  # the client sends it with each call
```

## Timing

A step of the sign-in replies no sooner than the strategy of its timing
says, which the application declares, as the sign-in has none, so that the
time of a reply tells nothing of who signed up: `AuthFloorTiming` holds
every reply, a refusal as a success, to `AUTH_SIGN_IN_MIN_DURATION`
seconds, over the slowest branch; `AuthNoTiming` holds none.

```python
class AppSignInUnit(AuthSignInUnit):
    timing = Slot(AuthFloorTiming)
```
