The gRPC contract lies in the tree of the core, at the path of its proto
package, its code generated next to it: `ingot_auth.profiles.tags.v1`
instead of
`ingot_auth.contrib.transports.grpcio.proto.ingot_auth.profiles.tags.v1`,
the name of the module that of the contract, imported as `protoc` writes
it. A contract may now hold a message of another subdomain.
