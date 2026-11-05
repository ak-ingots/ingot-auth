The metadata lists the methods, `methods`, each by the path of its slot
with whether its sign-up and its sign-in are open, and so does
`GetMetadataResponse` over gRPC. A method tells it by
`get_sign_up_enabled()` and `get_sign_in_enabled()`, closed in the base,
the nickname and the email code by the configs of their packages,
`AuthNicknameConfigs` and `AuthEmailCodeConfigs`, on by default, which a
project taking the method mixes into its own. `AuthMethods.get_all()`
gives the methods.
