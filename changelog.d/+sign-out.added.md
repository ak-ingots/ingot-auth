The sign-out: `auth.sign_out`, `AuthSignOutUnit`, its operation
`op_sign_out` closing the session of the caller, `SIGNED_OUT`, its token
working no more from the very next request. Any caller may, requiring no
permission: one of no session, the anonymous one of a token closed, expired
or unknown, signs out of nothing. Over gRPC, the service `SignOut` of
`ingot_auth.sign_out.v1`, in `AuthGrpcSignOutBinding`, which
`AuthGrpcFlowsBinding` takes. `auth.sessions.close()` closes an open
session of a profile for a reason and forgets it in the cache.
