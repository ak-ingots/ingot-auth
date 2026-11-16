# Guide

An application inherits `AuthProject`, the project of the mail of
[ingot-mail](https://pypi.org/project/ingot-mail/) with the addon's
settings, logging and `auth` unit, or takes the classes of the addon
among the bases of its own, as the
[addon guide](https://ingots.readthedocs.io/en/latest/defaults/addon.html)
of Ingots shows. It chooses its storage, its cache, its transports and its mailer
among those of {doc}`../contrib/index`.

```{toctree}
:maxdepth: 2

methods
sign-in
access
profiles
sessions
activities
configs
```
