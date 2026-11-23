The API of the addon, `ingot_auth.api`: the contract of gRPC under
`ingot_auth.api.<path>.v1`, its files in `ingot_auth/api/<path>/v1/`, beside
the RPCs of each service as mixins, exported by `ingot_auth.api`. Every
binding of the transport of gRPC binds its service under it too, as
`<attribute>_temp`, its servicer `<Servicer>Temp`, so that a client moves
on while a server serves both.
