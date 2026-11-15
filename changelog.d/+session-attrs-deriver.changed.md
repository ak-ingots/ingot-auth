An application declares the strategy deriving the attributes of its
sessions in the slot `deriver` of `AuthSessionsUnit`, as it declares their
lifetime, `AuthNoSessionAttrsDeriver` for none. The composite binding of the
registries of the sessions is `AuthGrpcSessionRegistriesBinding`,
`AuthGrpcSessionsBinding` now the one of the service `Sessions`;
`build_transport_attr_values()` of `ingot_auth.sessions.attrs` is
`build_attr_values()`, of the values of a source.
