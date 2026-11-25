# CLAUDE.md of `api/`

The contract of gRPC of the addon and the business layer of its transports,
protobuf alone. Named and shaped by ADRs 0009, 0011, 0013 and 0017.

- A file per service at the path of its package, the tree of `api/` that of
  the subdomains of the core: `api/profiles/tags/v1/tags.proto` for
  `ingot_auth.api.profiles.tags.v1`. An RPC is a verb then its subject,
  `ListTags(ListTagsRequest)`, as `buf.yaml` lints it.
- `make proto` generates the code next to its `.proto`, committed, imported
  as `protoc` writes it, by `api/` and the transports alone: the core
  imports no `v1` module.
- A method takes its annotation `google.api.http` (AIP-127); `buf breaking`
  keeps the JSON of the contract too (`WIRE_JSON`).
- The RPCs of a service are mixins in the `rpcs.py` next to its `v1/`,
  `rpc_*`, a call told by `BaseAuthRpcContext`, all exported by
  `ingot_auth.api`; a transport mixes them in and adds nothing of the
  business.
- The statuses of the errors are in `errors.py`: `google.rpc.Code`, a
  reason, metadata; a transport takes them in its error policy.
- Shared messages: what a step asks for, `Challenge` by the kind of its
  answer, in `methods/v1/`; the results and the answers of the flows in
  `sign_up/v1/`, `sign_in/v1/`; the values of the attributes, of a session
  or a profile, `AttrValue`, in `attrs/v1/`.
- A service of a set of operations has its enum `Permission`, repeating the
  `Flags` of its unit.
- A new service is bound in both transports, `contrib/transports/grpcio/`
  and `contrib/transports/starlette/`, and in the examples that serve it.
