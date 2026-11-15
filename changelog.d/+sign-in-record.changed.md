A storage of the sessions implements `_get_all()`, the sessions of a
profile, open and closed, and keeps who closed one, `closed_by` of
`_close()`; the contract of the storages checks both. A session of MongoDB
closed by 0.2.0 is closed by none known.
