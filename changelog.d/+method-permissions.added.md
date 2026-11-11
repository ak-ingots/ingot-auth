The flows of a method are permissions, a domain a method,
`AuthNicknamePermissions` of `auth.methods.nickname`,
`AuthEmailCodePermissions`, `AuthTestingPermissions`, a flag a flow,
`CAN_SIGN_UP`, `CAN_SIGN_IN`, which a method gives by a hook a flow,
`_get_sign_up_permissions()`, `_get_sign_in_permissions()`, a flow
unsupported without it. A sign-up by a method needs its `CAN_SIGN_UP`,
`OperationPermissionsError` without it, on the start and the answers
alike; `get_sign_up_permissions()` and `get_sign_in_permissions()` of a
method give what a flow needs, and `auth.methods.get_anonymous_permissions()`
the flags of the flows open by their toggles, for the anonymous caller. The
method of the tests opens both of its flows.
