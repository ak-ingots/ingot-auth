The RPCs of the metadata, the method of a nickname and the sign-out are
mixins of `contrib/transports/contract/`, of the messages of the contract
and no transport, needing protobuf alone: `AuthMetadataRpcMixin`,
`AuthNicknameRpcMixin`, `AuthSignOutRpcMixin`, over `AuthRpcMixin` and
`AuthSessionRpcMixin`, a call told by a `BaseAuthRpcContext`. Their
servicers of gRPC mix them in, `GrpcAuthRpcContext` adapting the context of
grpcio, and answer as before; HTTP takes them next.
