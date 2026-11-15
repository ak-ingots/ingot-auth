The profile of the caller: `auth.profiles.op_get_own`, `AuthOwnProfile`, its
tags, the values of its attributes, its permissions and its hash, by the
flag `CAN_READ_OWN` of `auth.profiles`, which `auth.grp_signed_in` grants;
over gRPC `GetOwnProfile` of the service `Profiles`. The hash, computed once
when the caller is formed, is carried by `AuthCaller`, `profile_hash`, and
told in the trailing metadata of every reply to a signed-in caller,
`ingot-auth-user-profile-hash`, by `BaseAuthGrpcServicer`, which the
servicers of an application extend: a client asks for the profile again
when it differs from its own.
