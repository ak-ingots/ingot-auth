Added the transport of HTTP and JSON, `contrib/transports/starlette/`, by
the extra `starlette` on ingot-starlette, no grpcio: the metadata, the
method of a nickname and the sign-out, the RPCs of the contract transcoded
by the annotations `google.api.http` their methods now take, `GET
/v1/metadata`, `POST /v1/methods/nickname:signUp` and `:signIn`, `POST
/v1/session:signOut`, the canonical JSON of proto3 of their messages; the
token of the caller in `Authorization: Bearer`, the hash of its profile in
the header `ingot-auth-user-profile-hash` by
`AuthStarletteProfileHashMiddleware`; the errors problems of RFC 9457 by
`AuthStarletteErrorsUnit`, the statuses of HTTP of their codes of gRPC, the
reason, the domain and the metadata as the extensions. The statuses of the
errors live in the contract, `contrib/transports/contract/errors.py`, both
transports telling alike; `buf breaking` checks the JSON of the contract
too.
