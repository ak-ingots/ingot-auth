The values of the attributes of the session of the source `transport`,
the IP: the starts of the flows take them by the names of their
attributes, `transport_attr_values` of `AuthStartSignUpParameters` and
`AuthStartSignInParameters`, which the transport alone sets, and keep
those the registry has of the transport, under their ids, with the
values of the client, in the record of the sign-up and in the session;
a value of no attribute is dropped, one of an attribute of another source
or type too, with a warning. Over gRPC, the servicers of the methods
extend `BaseAuthGrpcMethodServicer`, whose hook
`_get_transport_attr_values()` binds each name to the function reading it
from the call: `ip` to the IP of the peer, which an application behind a
proxy binds to the header of its proxy.
