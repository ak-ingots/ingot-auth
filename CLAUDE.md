# CLAUDE.md

Guidance for Claude Code in this repository. Keep it under 200 lines and do not
repeat what README, `docs/` or the ADRs say: link to them.

## What this is

`ingot-auth`: an addon of [Ingots](https://github.com/ak-ingots/ingots) for
the sign-up, the sign-in and the sessions of the users of an application. The
goal of the core: assume no details, as far as it goes; the application binds
the methods of sign-in, plugs the storage, the cache and the transport. A
library (ADR 0003), Python >= 3.14, part of the
[ak-ingots](https://github.com/ak-ingots) ecosystem; the meta repository
`ingots-libs` holds the ecosystem-wide decisions in `docs/adr/`.

## Layout

The map of the package, part by part, is
[docs/contributing/architecture.md](docs/contributing/architecture.md); read
it before a change that crosses parts. `api/` and `contrib/` have a
`CLAUDE.md` of their own.

- `project.py`, `settings.py`, `logging.py`, `operations/`: `AuthProject` on
  the `MailProject` of ingot-mail, its units, the configs `AUTH_*`.
- `auth.py`: `AuthUnit`, the units of the domains: `profiles/`,
  `sessions/`, `access/`, `activities/`, `metadata/`, on `registry/`.
- `methods/`, `policies/`, `sign_up/`, `sign_in/`, `sign_out/`: the methods
  and their flows; `methods/password/` the password of the profile.
- `storages/`, `caches/`, `dispatchers.py`: the facades of the backends.
- `api/`: the contract of gRPC and the RPCs the transports share.
- `contrib/`: the backends, the transports, `policies/` that call out.
- `testing/contracts/`: the guarantees a consumer runs (ADR 0005).
- `examples/game`, `examples/web`: the stacks of the extras, run by their
  scenarios; `perf/game` their load.
- `python -m ingot_auth` runs the addon on its own (prefix `INGOT`), the
  storage in memory.

## Commands

Everything goes through `make` (run `make` alone for the target list); uv
provides the environments and interpreters.

```bash
make check        # what CI runs: lint, test, coverage, wheel-test, doc, cl-check
make lint         # black --check, flake8, mypy --strict, buf lint (Buf of ingots-libs)
make test         # unittest on the working tree
make coverage     # the same under coverage, with MongoDB and Redis; fails below 99%
make integration  # the storage in MongoDB, a replica set, and the cache in Redis
make wheel-test   # unittest on the built wheel, PYTHONS="3.14 3.15"
make format       # black
make proto        # the code of the contract, next to its .proto
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
  publishes to TestPyPI, tests the package installed from it (the shared
  workflow `index-test`), then publishes to PyPI once the user approves the
  `pypi` environment. Run by hand, the workflow rehearses on TestPyPI only.

## Rules

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
- A comment tells what the code cannot: why it is so, a constraint from
  outside (a bug of a library, a standard, a measure), a trap for the next
  change. None repeats the code, a name, a docstring or what a key of a
  config says, nor tells the history of a change: that is the commit's.
  Reading it, one thinks "ah, so that's it"; a comment that gives no such
  moment states the obvious and goes.
- A TODO names its issue of GitHub, `# TODO(#42): ...`, of another
  repository `# TODO(ak-ingots/ingots#42): ...`: one without an issue is
  never done. No issue, no TODO: do it now, or open the issue first.
- A type is narrowed by an annotation in the class, not by `t.cast` at
  each use: an entity its project or parent, `project: "AuthProject"`,
  `parent: AuthProofsOwner`, a mixin too, a mixin of two projects naming a
  type of both; an error its `args`, `args: tuple[str, int]`. `t.cast`
  stays where no class can carry the type: a function whose parameter
  cannot be narrowed, a value from a library or from outside.
- Code layout and naming follow ADR 0007; the PUER rules of `ingots` apply to
  an addon too: hooks start with an underscore and are overridden, not
  called; a protected member is touched only by its class, its subclasses
  and its own package.

Of this package:

- The guide of the consumers is in `docs/guide/`, published on Read the Docs
  as a subproject of `ingots`, `https://ingots.readthedocs.io/projects/ingot-auth/`;
  a change of what a consumer writes updates it, a change of the map
  `docs/contributing/architecture.md`. The README stays short, the status,
  the install and the link, its links absolute, as PyPI renders it; its
  status and that of `docs/index.md` go together.
- A unit lives in the `__init__.py` of its package, as in `ingots.defaults`,
  or in a module of its name when it has nothing beside it (`settings.py`,
  `logging.py`, `auth.py`). A class takes the prefix `Auth`, so that an
  application imports it under its own name. A unit names its operations
  `op_*`, its commands `cmd_*` (their CLI names by `cli_name`), its groups
  `grp_*` (named by their full names), its events `ev_*`.
- A set of operations has its flags in its unit, a `PermissionFlags` nested
  as `Flags`, bound by the slot `permissions` (`PermissionsSlot`) of the
  unit, an `OperationsOwner`, their domain the full name of the unit; an
  operation builds its permissions by its hook `_get_permissions()`; the
  enum `Permission` of its contract repeats them.
- A method of the catalogue is whole, a plain default for what it sends, so
  that an application plugs only the backends. A variation of behaviour is a
  strategy in a slot, none by default, or a policy in a group.
- The errors of a package live in its `errors.py`, apart from the entity
  they are of, and the package exports them as before.
- The parameters of an operation, `*Parameters`, and a result of its own,
  `*Result`, live in its `operations.py`, above it, or above the base of
  a family of operations they serve; `data.py` holds the data of a
  package, bare nouns, what several parts pass around: a token, what a
  client sees, the context of an activity, the records of a storage, the
  items of a registry.
- An entity names its own identifier `uid`, a reference to another
  `<entity>_uid`, `profile_uid`, `session_uid`, `attr_uid`, never `id`, a
  builtin of Python; the fields a backend stores are named alike, MongoDB
  keeping its `_id`.

## Design

An addon extends the framework through slots and subclassing (ADR 0004) and
ships contract tests that its consumers run (ADR 0005); design principles in
ADR 0006. The settings it extends are documented in `ingots`:
`docs/defaults/settings.md` and `docs/defaults/addon.md`. The design of the
auth, its stories and slices, is `docs/design/auth/` of the meta repository.
