# CLAUDE.md

Guidance for Claude Code in this repository. Keep it under 200 lines and do not
repeat what README or the ADRs say: link to them.

## What this is

`ingot-auth`: an addon of [Ingots](https://github.com/ak-ingots/ingots) for
the sign-up, the sign-in and the sessions of the users of an application.
`AuthProject` (`project.py`) takes the addon's `AuthSettingsUnit` (`settings/`)
with its `AuthConfigs` (`settings/configs.py`, named `AUTH_*`), its
`AuthLoggingUnit` (`logging/`, the logger `ingot_auth`) and `AuthUnit` (`auth/`,
the auth of the project: the units `profiles/`, with the registries `tags/`
and `attrs/`, and `sessions/`, with the registries `attrs/`, each attribute of
a session with its source, and `presets/`, bound to the attributes many to
many, all on the shared `registry/`, the sessions themselves kept by the hash
of their token, their lifetime a strategy in the slot `lifetime`, none by
default, and `authenticate()` turning a token into an `AuthCaller`, the
session and the caller cached apart, the caller by the digest of the groups
too, its callers forgotten by `forget_callers()` on a change of the
memberships; the `access/`, its `groups/` entities
in slots of `AuthGroupsUnit`, declared in the code, granting by a hook, its
`members/` the memberships in the storage, `signed_in` of the core, of every
signed-in user, none stored, granting the sign-in of each method open, and
`AuthGroupsGrants`, the permissions of a user from its groups; the `metadata/` for the consumers, by the subdomains, of the sessions what is the client's; the
methods of signing up and in `methods/`, units in slots of `AuthMethodsUnit`, a
catalogue in the core, a subpackage a method (`nickname/`, `email_code/`),
none bound until an application declares its slot, in
steps kept by attempts, a hook to start each flow they take, their flows
their permissions too, a domain a method, its flag a flow by a hook
(`_get_<flow>_permissions`), given by the toggles, each naming
the kind of the identifier it verifies (`IDENTIFIER_KIND`), an identity
`(kind, value)` bound to a profile once whatever method, their groups of
the policies their slots `policies_<flow>_<field>`, each a `Factories` of
ingots typed by its parameters, made by the method, which runs the group
together (`run_group`); the password of the
profile in `methods/password/`, the slot `password` of the methods, not a
method, its hash the secret of the uid in `storages/profiles/secrets.py`, its group
`policies_set` of a new one by any method; the `policies/`, rules a value is checked
against, each an operation taking a part of its parameters by a protocol,
raising `AuthPolicyViolationError` with its name, configured by the `CONFIG`
of its class; the `sign_up/` and `sign_in/` flows, over the base
of the flows of the methods, `methods/operations.py`, the sign-in opening a
session, its replies held by the strategy in its slot `timing`, none by
default; the storages `storages/`, the
interfaces a backend implements with what they keep and raise, depending on
no other part of the auth, laid out as a contrib of storages is, `AuthStorage`
with the transactions of a backend over all its storages; and the caches
`caches/`, the same for what lives minutes, the attempts, the sessions and
their callers, `AuthCache` the facade, depending on the storages alone, for
the records they keep too); a unit lives in the
`__init__.py` of its package, as in `ingots.defaults`, and a class takes the
prefix `Auth`, so that an application imports it under its own name. A unit
names its operations `op_*` and its commands `cmd_*`, the commands taking
their CLI names from `cli_name`. The goal of the core: assume no details, as
far as it goes; the methods of sign-in are bound by the application, the
storage and the transport plug in. The core holds the facades; their
implementations are in `contrib/` (`contrib/storages/<backend>/`,
`contrib/transports/<addon>/`, `contrib/caches/<backend>/`), each under
its own extra when it needs more than the core. A contrib is laid out by the
subdomains of the core, `profiles/`, `sessions/`, as the core is.
The gRPC contract is named and shaped by ADRs 0009, 0011 and 0013: a file per
service at the path of its package, in the tree of the core next to the
subdomain it serves, `ingot_auth/profiles/tags/v1/tags.proto` for
`ingot_auth.profiles.tags.v1`, an RPC a verb then its subject,
`ListTags(ListTagsRequest)`, as `buf.yaml` lints it; `make proto` generates
the code next to it, committed, imported as `protoc` writes it, by
`contrib/transports/grpcio/` alone: the core imports no `v1` module. A method
of the core has its service in its package, `ingot_auth/methods/nickname/v1/`,
its servicer in `contrib/transports/grpcio/methods/`, the results of the flows
in `ingot_auth/sign_up/v1/` and `ingot_auth/sign_in/v1/`, the values of the
attributes of a session, `AttrValue`, in `ingot_auth/sessions/attrs/v1/`. A set of
operations has its permissions in a `permissions.py` of its own, the enum
`Permission` of its contract repeating them. A contrib gives the class of the slot it fills
(`AuthMemoryStorage` for `AuthUnit.storage`), no unit or project: the
application composes. What a backend chooses is changed by subclassing, not a config: a client by a
hook, the names of its collections by a `ClassVar`; the
configs of the environment belong to the infrastructure addon. `testing/contracts/` holds the guarantees of the addon as tests a consumer runs (ADR 0005),
`python -m ingot_auth` runs the addon on its own
(prefix `INGOT`) with the storage in memory. A library (ADR 0003), Python >= 3.14, part of the
[ak-ingots](https://github.com/ak-ingots) ecosystem; the meta repository
`ingots-libs` holds the ecosystem-wide decisions in `docs/adr/`.

## Commands

Everything goes through `make` (run `make` alone for the target list); uv
provides the environments and interpreters.

```bash
make check        # what CI runs: lint, test, coverage, wheel-test, doc, cl-check
make lint         # black --check, flake8, mypy --strict, buf lint (Buf of ingots-libs)
make test         # unittest on the working tree
make coverage     # the same under coverage, with MongoDB; fails below 99%
make integration  # the storage in MongoDB against docker-compose.yml, a replica set
make wheel-test   # unittest on the built wheel, PYTHONS="3.14 3.15"
make format       # black
make doc          # apidoc, then Sphinx; warnings are errors
make doc-serve    # doc, then serve docs/build/ [DOC_HOST=0.0.0.0 DOC_PORT=8000]
```

One test: `uv run python -m unittest tests.test_canary.CanaryTestCase`.

## Commits and GitHub

- Never commit, amend, push, open a pull request, tag or rewrite history on
  your own initiative: show a summary and the proposed message, wait for an
  explicit approval of that commit. One approval does not extend to the
  next. Never merge a pull request: the user does (`gh pr merge` is denied).
- The remote is `ak-ingots/ingot-auth`. Inside the `ingots-libs`
  checkout, run gh and git network commands as
  `direnv exec /home/bee/work/ingots-libs <cmd>` (the token comes from its
  `.envrc`; never read it).
- `main` and `release/X.Y` are protected by a ruleset: no direct push, force
  push or deletion; pull requests only, squash-merged, with every CI job
  green on a branch up to date with `main`. One change per branch and PR,
  kept to one commit; the squash commit takes the PR title and description,
  so write them as the commit message. The `Co-Authored-By` trailer goes in
  the branch commit only: GitHub carries it to the end of the squash commit.
- Before pushing a branch, rebase it onto the current `main` and run
  `make check`. After the user merges, switch to `main`, pull and delete the
  local branch.
- A release: a pull request sets the version (`uv version X.Y.Z`) and
  collates the changelog (`make cl-build VERSION=X.Y.Z`); after the merge,
  the tag `vX.Y.Z` on its commit starts the `release` workflow, which
  publishes to TestPyPI, tests the package installed from it
  (the shared workflow `index-test`), then publishes to PyPI once the user approves the
  `pypi` environment. Run by hand, the workflow rehearses on TestPyPI only.

## Rules

- The guide of the consumers is in `docs/guide/`, published on Read the Docs
  as a subproject of `ingots`, `https://ingots.readthedocs.io/projects/ingot-auth/`;
  a change of what a consumer writes updates it. The README stays short,
  the status, the install and the link, its links absolute, as PyPI renders
  it; its status and that of `docs/index.md` go together.
- Every change users should know about adds a fragment to `changelog.d/`
  (`<issue>.<type>.md` or `+<slug>.<type>.md`, see `changelog.d/README.md`);
  `cl-check` fails CI without one.
- The version is static in `pyproject.toml` (`uv_build`, no setuptools-scm);
  it changes only at release time.
- Versions start at 0.1.0: the name holds no older release; a version is
  published only once.
- `ingots` is pinned to a minor version: before 1.0 a minor
  version of the framework may break its addons. Moving on to the next one
  is a change of its own, with a news fragment.
- Flat layout: the package is `ingot_auth/` at the root. The wheel must be
  complete: `make wheel-test` imports the package only from the wheel.
- Tests are stdlib `unittest`, no pytest. Code passes `mypy --strict` with
  `explicit-override`: every override takes `@t.override`; black at 88
  columns.
- The supported interpreters are listed in three places with nothing linking
  them: `PYTHONS` in the Makefile, the classifiers and the `wheel` matrix in
  `.github/workflows/ci.yml`. Change them together.
- CI runs exactly the `make` targets; a new check goes into `make check` and
  `ci.yml` together.
- Code layout and naming follow ADR 0007; the PUER rules of `ingots` apply to
  an addon too: hooks start with an underscore and are overridden, not
  called; a protected member is touched only by its class, its subclasses
  and its own package.
- The errors of a package live in its `errors.py`, apart from the entity
  they are of, and the package exports them as before.

## Design

An addon extends the framework through slots and subclassing (ADR 0004) and
ships contract tests that its consumers run (ADR 0005); design principles in
ADR 0006. The settings it extends are documented in `ingots`:
`docs/defaults/settings.md` and `docs/defaults/addon.md`.
