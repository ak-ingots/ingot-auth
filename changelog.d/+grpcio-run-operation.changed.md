The servicers of the auth run their operations by `run_operation()` of
ingot-grpcio 0.12.1, which the extra `grpcio` now requires, on ingots
0.33.2, for the caller of the hook `_get_caller()`: those open to anyone,
the metadata, the starts of the methods, the answers of the flows, extend
`GrpcServicer` alone and run for the anonymous caller of the project
whatever a call bears; the others extend `BaseAuthGrpcServicer`, for the
caller of the token, the anonymous one with none. `_get_anonymous_caller()`
is gone: a subclass overrides `_get_caller()`, an application closes the
metadata by its group `grp_anonymous`.
