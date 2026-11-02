The policies and their presets. A policy is an entity of the project, a
rule a value is checked against with the config a binding gives it: the
length and the characters, by the sets of Unicode, in the core, others as
slots `policy_*` of `AuthPolicies`, found by their class. A policy takes
the part of a context its protocol tells; a preset, a slot `preset_*`, is
of a context, and binds in order the policies taking its parts, each by
`bind()` with a config of its type, so mypy refuses a policy or a config
that does not fit. The presets of the nickname and the password of a
sign-up come empty: an application binds policies to them in subclasses,
from a hook that extends, replaces or drops the bindings of the base.
`check()` raises `AuthPolicyViolationError`, naming the binding broken,
and `get_bindings()` gives them as data, for the clients. The method of a
nickname and a password checks them on a sign-up by these presets, and
raises `AuthMethodInvalidError`, naming the field and the binding.
