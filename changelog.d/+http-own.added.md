Over HTTP too, by the extra `starlette`: the method of an email and a code,
`POST /v1/methods/emailCode:startSignUp` and `:startSignIn`; the answers of
the flows, `POST /v1/signUp:answer` and `/v1/signIn:answer`; the sessions of
the caller's own, `GET /v1/ownSessions`, `POST
/v1/ownSessions/{session_uid}:revoke`, `POST /v1/ownSessions:revokeOthers`;
the profile of the caller, `GET /v1/ownProfile`. Their services, the
sessions and the profiles whole, are RPCs of the contract the servicers of
gRPC mix in.
