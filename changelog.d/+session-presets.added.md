The presets of the sessions: a registry of presets, flat, with the
attributes of the sessions bound to them many to many, each binding
telling whether the preset requires the attribute. Operations,
`auth session presets` commands (`bind`, `unbind`, `bindings` among
them), the storage in memory and in MongoDB with its contract, and the
gRPC service `ingot_auth.session.presets.v1.Presets` in
`AuthGrpcAdminBinding`.
