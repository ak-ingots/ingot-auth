The storage in MongoDB keeps the profiles, their identities and secrets, the
records of the sign-ups and the members of the groups too, so a sign-up runs
on it whole. Its storages share `AuthMongoDbCollectionMixin`: a subclass
names its collection by `MONGODB_COLLECTION`, its database by
`MONGODB_DATABASE`, its client by `_mongodb_get_client()`.
