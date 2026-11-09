The RPCs are named after their operations, a verb then its subject, as
ADR 0013 of the ecosystem says: `Tags.CreateTag`, `ListTags`,
`RenameTag`, `DeleteTag`, the same for the attributes of the profiles
and of the sessions and for the presets, with `BindAttr` and
`UnbindAttr`, and `Metadata.GetMetadata`. The messages keep their names;
a client calls the new names, the methods of a servicer overridden take
them too.
