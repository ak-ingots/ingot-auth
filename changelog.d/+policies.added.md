The policies and their presets. A policy is an entity of the project, a
rule a value is checked against with the config a binding gives it: the
length and the characters, by the sets of Unicode, in the core, others as
slots of `AuthPolicies`, found by their class. A policy takes the part of
a context its protocol tells; a preset is of a context, and binds in order
the policies taking its parts, each by `bind()` with a
config of its type, so mypy refuses a policy or a config that does not
fit. A preset is of a method: a method is a unit, its presets its slots
`preset_<flow>_<field>`, each of a class and a context of its own, empty
until an application binds policies to them in subclasses, from a hook
that extends, replaces or drops the bindings of the base. The method
makes the context on the step that checks it, by `_check()`, and a value
breaking a policy raises `AuthMethodInvalidError`, naming the field and
the binding. `get_bindings()` gives the bindings as data, for the clients.
