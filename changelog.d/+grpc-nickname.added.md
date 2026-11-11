The method of a nickname over gRPC: the service `Nickname` of
`ingot_auth.methods.nickname.v1`, `SignUp` and `SignIn`, in
`AuthGrpcNicknameBinding`, its servicer `AuthGrpcNicknameServicer` running
them for the anonymous caller of `_get_anonymous_caller()`, given the flags
of the flows and of the methods open by their toggles. Their results are of
the flows, `SignUpResult` of `ingot_auth.sign_up.v1` and `SignInResult` of
`ingot_auth.sign_in.v1`, the token of a session with its id; the values of
the attributes of the session a client gives are `AttrValue` of
`ingot_auth.sessions.attrs.v1`, a variant of `oneof` a type, a decimal as a
string. `AuthGrpcErrorsUnit` gives the errors of the methods their
statuses: refused `UNAUTHENTICATED`, denied `PERMISSION_DENIED`, invalid
`INVALID_ARGUMENT`, unsupported `FAILED_PRECONDITION`, no such method
`NOT_FOUND`, an identifier taken `ALREADY_EXISTS`. The anonymous caller of
every servicer comes from `_get_anonymous_caller()`, the metadata giving its
`CAN_READ` there.
