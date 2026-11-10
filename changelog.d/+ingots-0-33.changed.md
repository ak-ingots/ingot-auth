Moved on to ingots 0.33, ingot-grpcio 0.12 and ingot-pymongo 0.13. The
classes are named by ADR 0014 of the ecosystem: an operation takes the
suffix `Operation`, `AuthCreateTagOperation`; a unit that groups others
`Unit`, `AuthProfilesUnit`, `AuthTagsUnit`, `AuthAccessUnit`,
`AuthSettingsUnit`, `AuthGrpcErrorsUnit`; the storages, the caches and the
methods keep their names, of their role. The commands run their
operations by `BaseOperationCommand` of ingots.
