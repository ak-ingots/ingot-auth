The values of the attributes of a session are `attr_values`, not `values`,
wherever they go: the parameters of the start of a sign-up,
`AuthStartSignUpParameters.attr_values`, the attempt, the record of a
sign-up, the session and their documents in MongoDB; the functions of them
too, `check_client_attr_values` of `ingot_auth.sessions.attrs`,
`build_bson_attr_values` and `build_attr_values` of the storage in MongoDB.
