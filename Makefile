SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

SRC := ingot_auth tests docs/conf.py examples perf
DOC_OUT := docs/build

PYTHONS ?= 3.14 3.15

EXTRAS ?= grpcio,pymongo,redis,starlette

AGAINST ?= origin/main

# Where `doc-serve` listens. The default is every interface, so the docs built
# on a headless dev server open in a browser elsewhere; DOC_HOST=127.0.0.1
# keeps them local.
DOC_HOST ?= 0.0.0.0
DOC_PORT ?= 8000


##@ Checks

.PHONY: check
check: lint test coverage wheel-test example-test doc cl-check  ## Every check: lint, test, coverage, wheel-test, example-test, doc, cl-check

# docs/conf.py is checked too: mypy needs the doc group to see Sphinx.
.PHONY: lint
lint: proto-lint  ## black --check, flake8, mypy --strict, the contract by Buf
	uv run black --check --diff $(SRC)
	uv run flake8 $(SRC)
	uv run --group doc mypy $(filter-out examples perf,$(SRC))
	# each example an application of its own, its modules at its root: a run
	# each, as two have modules of one name; the stand of the load with the
	# game, whose scenarios it imports
	uv run --group doc mypy $(GAME) perf
	uv run --group doc mypy $(WEB)

# The gRPC contract by buf.yaml, by Buf of the version the ecosystem pins:
# that of ingots-libs when this repository lies in its checkout, fetched there
# on the first use; else the one on the PATH, where the action setup-buf of
# ingots-libs puts it in CI. BUF=<path> gives another.
META := $(abspath ..)
BUF_VERSION_FILE := $(META)/.github/actions/setup-buf/version
ifneq ($(wildcard $(BUF_VERSION_FILE)),)
BUF ?= $(META)/.cache/buf/$(shell cat $(BUF_VERSION_FILE))/buf
endif
BUF ?= buf
.PHONY: proto-lint
proto-lint:  ## The gRPC contract by Buf STANDARD (ADR 0013)
	@if [ "$(BUF)" != buf ] && [ ! -x "$(BUF)" ]; then $(MAKE) -C $(META) buf; fi
	@command -v $(BUF) >/dev/null || { \
		echo "no Buf: clone this repository inside ingots-libs, or put on the"; \
		echo "PATH the version ingots-libs pins in"; \
		echo ".github/actions/setup-buf/version, or give its path as BUF"; exit 1; }
	$(BUF) lint
	# the contract of main kept, its JSON too (WIRE_JSON of buf.yaml), but
	# where a change breaks it on purpose: BREAKING=skip, told by its CI
	@if [ "$(BREAKING)" = skip ]; then echo "buf breaking skipped: BREAKING=skip"; \
	else $(BUF) breaking --against '.git#ref=$(AGAINST)'; fi

.PHONY: test
test:  ## unittest on the working tree
	uv run python -m unittest discover -s tests -t .

# The storage in MongoDB and the cache in Redis are tested on real servers: the
# targets below start those of docker-compose.yml, and need Docker. Without it
# `make test` skips them.
WITH_SERVERS := trap 'docker compose down --volumes --timeout 1' EXIT; \
	docker compose up --detach --wait --quiet-pull; \
	export INGOT_AUTH_TEST_PORT=$${INGOT_AUTH_TEST_PORT:-27118}; \
	export INGOT_AUTH_TEST_REDIS_PORT=$${INGOT_AUTH_TEST_REDIS_PORT:-16380};

.PHONY: coverage
coverage:  ## unittest on the working tree under coverage, with MongoDB and Redis; fails below 99%
	@$(WITH_SERVERS) \
	uv run coverage run -m unittest discover -s tests -t . && uv run coverage report

.PHONY: integration
integration:  ## The storage in MongoDB and the cache in Redis against docker-compose.yml
	@$(WITH_SERVERS) \
	uv run python -m unittest -v tests.test_mongodb_storage tests.test_redis_cache

.PHONY: wheel-test
wheel-test: all  ## unittest on the built wheel, once per interpreter in PYTHONS
	@$(MAKE) --no-print-directory installed-test WHEEL="$$(echo dist/*.whl)"

# What the tests need beside the wheel: the client of Starlette's TestClient.
TOOLS ?= httpx

# The tests of tests/ on WHEEL, with TOOLS, once per interpreter in PYTHONS: for `wheel-test`
# and for the workflow `index-test` of the meta repository, which the `release`
# workflow calls between TestPyPI and PyPI, on the files it has just published.
.PHONY: installed-test
installed-test:
	@test -n "$(WHEEL)" || { echo "WHEEL=path/to.whl is required"; exit 1; }
	@$(WITH_SERVERS) \
	for py in $(PYTHONS); do \
		echo "== $(notdir $(WHEEL)) on Python $$py"; \
		tmp=$$(mktemp -d); \
		uv venv --quiet --python $$py "$$tmp/venv"; \
		uv pip install --quiet --python "$$tmp/venv/bin/python" "$(WHEEL)[$(EXTRAS)]" $(TOOLS); \
		cp -r tests README.md "$$tmp/"; \
		(cd "$$tmp" && INGOT_AUTH_WHEEL_TEST=1 venv/bin/python -m unittest discover -s tests -t .) \
			|| { rm -rf "$$tmp"; exit 1; }; \
		rm -rf "$$tmp"; \
	done

# The game of examples/game as an application runs it (ADR 0016 of
# ingots-libs): its image installs the wheel and the versions of uv.lock, its
# servers by its docker-compose.yml; the scenarios, a project of their own,
# call it from here, `testing run` of ingots. The image takes the newest of
# PYTHONS, as a new application would; the others are proven by wheel-test.
# GAME_TEST_* configure the scenarios and the ports compose publishes alike.
GAME := examples/game
export GAME_PYTHON := $(lastword $(PYTHONS))
export GAME_TEST_GRPC_DEFAULT_HOST ?= 127.0.0.1
export GAME_TEST_GRPC_DEFAULT_PORT ?= 50061
export GAME_TEST_GAME_SECOND_PORT ?= 50062
export GAME_TEST_MAILPIT_PORT ?= 18025
export GAME_TEST_IS_STRICT_CONFIGS ?= on
# the scenarios of the load, of their own prefix, their ports by perf.ini
export PERF_TEST_IS_STRICT_CONFIGS ?= on
WEB := examples/web
export WEB_PYTHON := $(lastword $(PYTHONS))
export WEB_TEST_SITE_PORT ?= 8080
export WEB_TEST_MAILPIT_PORT ?= 8081
export WEB_TEST_IS_STRICT_CONFIGS ?= on
.PHONY: example-test
example-test: all  ## The scenarios of examples/game and examples/web against them in Docker
	uv export --quiet --no-dev --extra game --no-emit-project --no-hashes \
		--output-file dist/game-requirements.txt
	uv export --quiet --no-dev --extra web --no-emit-project --no-hashes \
		--output-file dist/web-requirements.txt
	@trap 'docker compose -f $(GAME)/docker-compose.yml down --volumes --timeout 1' EXIT; \
	docker compose -f $(GAME)/docker-compose.yml up --build --detach --wait --quiet-pull; \
	(cd $(GAME) && uv run python -m scenarios testing run -v)
	@trap 'docker compose -f $(WEB)/docker-compose.yml down --volumes --timeout 1' EXIT; \
	docker compose -f $(WEB)/docker-compose.yml up --build --detach --wait --quiet-pull; \
	(cd $(WEB) && uv run python -m scenarios testing run -v)


##@ Code

# The code of the .proto files: grpcio's _pb2.py and _pb2_grpc.py, with the
# stubs of mypy-protobuf, committed next to them. A contract lies at the path of
# its proto package, ingot_auth/<path>/v<N>/<service>.proto, so its code is
# imported as protoc writes it (ADR 0011): no rewrite.
# The protos of google.api, of googleapis-common-protos, beside its code
GOOGLEAPIS = $(shell uv run python -c "import google.api.annotations_pb2 as m, pathlib; print(pathlib.Path(m.__file__).parents[2])")

.PHONY: proto
proto:  ## Generate the code of the .proto files
	uv run python -m grpc_tools.protoc -I . -I $(GOOGLEAPIS) --python_out=. --grpc_python_out=. \
		--mypy_out=. --mypy_grpc_out=. $$(find ingot_auth -name '*.proto')

.PHONY: format
format:  ## Format code with black
	uv run black $(SRC)


##@ Documentation

# docs/modules/ is gitignored and regenerated. Read the Docs runs this target
# too, with its own environment, so the flags live in one place.
.PHONY: apidoc
apidoc:  ## Regenerate the API reference stubs in docs/modules/
	rm -rf docs/modules
	uv run --group doc sphinx-apidoc --separate --force --no-toc --module-first \
		--ext-viewcode --output-dir=docs/modules ingot_auth "*_pb2*"

.PHONY: doc
doc: apidoc  ## Build the HTML documentation into docs/build/, warnings are errors
	rm -rf $(DOC_OUT)
	uv run --group doc sphinx-build -j auto -b html -W --keep-going docs $(DOC_OUT)

.PHONY: doc-serve
doc-serve: doc  ## Build the documentation and serve it over HTTP [DOC_HOST=0.0.0.0 DOC_PORT=8000]
	@echo "Serving $(DOC_OUT) on http://$(DOC_HOST):$(DOC_PORT)/ (Ctrl+C to stop)"
	uv run python -m http.server $(DOC_PORT) --bind $(DOC_HOST) --directory $(DOC_OUT)


##@ Build

.PHONY: all
all:  ## Build the sdist and the wheel into dist/
	rm -rf dist
	uv build --quiet


##@ Load

.PHONY: perf-build
perf-build: all  ## The distributions of the example, what a stand builds a role by
	uv export --quiet --no-dev --extra game --no-emit-project --no-hashes \
		--output-file dist/game-requirements.txt

PERF_PYTHON ?= uv run python

.PHONY: perf-smoke
perf-smoke: perf-build  ## The scenarios of the stands of perf/, dry, against the game in Docker
	@trap 'docker compose -f $(GAME)/docker-compose.yml down --volumes --timeout 1' EXIT; \
	docker compose -f $(GAME)/docker-compose.yml up --build --detach --wait --quiet-pull; \
	(cd $(GAME) && for scenario in ../../perf/game/scenarios/*.py; do \
		$(PERF_PYTHON) -m ingots.perf $$scenario \
			--config IS_PRINT_CONFIGS=off perf smoke; \
	done)


##@ Changelog

.PHONY: cl-check
cl-check:  ## Fail if the branch adds no news fragment [AGAINST=origin/main]
	uv run --group changelog towncrier check --compare-with $(AGAINST)

.PHONY: cl-preview
cl-preview:  ## Preview the collated changelog [VERSION=X.Y.Z]
	uv run --group changelog towncrier build --draft --version $(or $(VERSION),UNRELEASED)

.PHONY: cl-build
cl-build:  ## Collate changelog.d/ into CHANGELOG.md (VERSION=X.Y.Z)
	@test -n "$(VERSION)" || { echo "VERSION=X.Y.Z is required"; exit 1; }
	uv run --group changelog towncrier build --version $(VERSION) --yes


##@ Housekeeping

.PHONY: clean
clean:  ## Remove build artefacts and caches (keeps the virtualenv)
	rm -rf build dist docs/modules $(DOC_OUT) .mypy_cache .coverage
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

.PHONY: help
help:  ## Show this help
	@echo "ingot-auth - make targets:"
	@awk 'BEGIN {FS = ":.*## "} \
		/^##@ / {printf "\n%s\n", substr($$0, 5); next} \
		/^[a-z][a-zA-Z0-9_-]*:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Variables: PYTHONS, EXTRAS, AGAINST, VERSION, DOC_HOST, DOC_PORT"
