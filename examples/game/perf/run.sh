#!/usr/bin/env bash
# A run of the load of the game, on the dev server alone (story 9 of its
# design): make perf BASELINE=X.Y.Z, from the root of ingot-auth.
#
# The baseline, the release X.Y.Z, is built from a worktree of its tag, its
# own game and lock; the candidate from the tree. Round after round, each
# role is brought up by compose on the cores of docker-compose.perf.yml,
# its players seeded, then every scenario of SCENARIOS loaded by each of its
# numbers of clients, by a pool of LOAD_PROCS processes on the cores of the
# load, which reads the CPU of the services too; each point appends its
# rows to results.csv. At the end, the median of the rounds of each point.
#
#   BASELINE    the release to compare with, X.Y.Z (0.8.0 at least)
#   SCENARIOS   [get-own-profile sign-in sign-up]
#   CLIENTS     the numbers of clients swept, by every scenario
#   CLIENTS_<SCENARIO>  those of one, CLIENTS_SIGN_IN, over CLIENTS
#               [get-own-profile 1 2 4 8 16, sign-in and sign-up 1 2 4 8 16 32]
#   ROUNDS      the rounds, the roles alternating           [3]
#   WARMUP      seconds of each point before it is measured [10]
#   DURATION    seconds measured                            [30]
#   LOAD_PROCS  the processes of the load                   [4]
#   TRIAL=1     runs on a host that is not quiet, the run marked a trial,
#               its rows in $PERF_WORK/results.csv
set -euo pipefail

: "${BASELINE:?BASELINE=X.Y.Z, the release to compare with}"
SCENARIOS=${SCENARIOS:-get-own-profile sign-in sign-up}
ROUNDS=${ROUNDS:-3}
WARMUP=${WARMUP:-10}
DURATION=${DURATION:-30}
LOAD_PROCS=${LOAD_PROCS:-4}
LOAD_CPUS=8-11
# the numbers of clients of a scenario, past which only the queue grows
CLIENTS_GET_OWN_PROFILE=${CLIENTS_GET_OWN_PROFILE:-${CLIENTS:-1 2 4 8 16}}
CLIENTS_SIGN_IN=${CLIENTS_SIGN_IN:-${CLIENTS:-1 2 4 8 16 32}}
CLIENTS_SIGN_UP=${CLIENTS_SIGN_UP:-${CLIENTS:-1 2 4 8 16 32}}
clients_of() { local name=CLIENTS_${1//-/_}; name=${name^^}; echo "${!name}"; }
TARGETS=127.0.0.1:${GAME_TEST_GRPC_DEFAULT_PORT:-50061},127.0.0.1:${GAME_TEST_GAME_SECOND_PORT:-50062}

repo=$(git rev-parse --show-toplevel)
perf=$repo/examples/game/perf
results=$perf/results.csv
# the worktrees of the baselines and the parts of a point, out of the tree
work=${PERF_WORK:-$HOME/.cache/ingot-auth/perf}
python=$repo/.venv/bin/python
mkdir -p "$work"

step() { (cd "$repo/examples/game" && "$python" -m perf "$@"); }

if ! step host --check; then
    [ "${TRIAL:-}" = 1 ] || exit 1
    echo "TRIAL=1: the run goes on, marked a trial"
fi
run=$(date -u +%Y%m%dT%H%M%SZ)
# a trial keeps its rows apart, out of the results of the releases
[ "${TRIAL:-}" = 1 ] && run=$run-trial && results=$work/results.csv
host_state=$(step host)
echo "run $run on $host_state"

# the newest Python of the Makefile, as make example-test builds the game
export GAME_PYTHON
GAME_PYTHON=$(sed -n 's/^PYTHONS ?= //p' "$repo/Makefile" | awk '{print $NF}')

# the distributions of a tree, as make example-test builds them
build() {
    (cd "$1" && rm -rf dist && uv build --quiet \
        && uv export --quiet --no-dev --extra game --no-emit-project \
            --no-hashes --output-file dist/game-requirements.txt)
}

baseline_tree=$work/baseline-$BASELINE
if [ ! -d "$baseline_tree" ]; then
    git -C "$repo" worktree add --quiet --detach "$baseline_tree" "v$BASELINE"
fi
[ -f "$baseline_tree/examples/game/docker-compose.yml" ] &&
    grep -q app2 "$baseline_tree/examples/game/docker-compose.yml" ||
    { echo "v$BASELINE runs no second process of the game: 0.8.0 at least"; exit 1; }
echo "building the baseline v$BASELINE and the candidate"
build "$baseline_tree"
build "$repo"

compose() {
    docker compose -p game-perf -f "$1/examples/game/docker-compose.yml" \
        -f "$perf/docker-compose.perf.yml" "${@:2}"
}

swap_in() { awk '$1 == "pswpin" {print $2}' /proc/vmstat; }

max_clients=0
for scenario in $SCENARIOS; do
    for clients in $(clients_of "$scenario"); do
        (( clients > max_clients )) && max_clients=$clients
    done
done

for round in $(seq "$ROUNDS"); do
    for role in baseline candidate; do
        if [ $role = baseline ]; then
            tree=$baseline_tree
            version=$BASELINE
        else
            tree=$repo
            version=$(sed -n 's/^version = "\(.*\)"/\1/p' "$repo/pyproject.toml")+dev
        fi
        commit=$(git -C "$tree" rev-parse --short HEAD)
        [ -z "$(git -C "$tree" status --porcelain)" ] || commit=$commit-dirty
        trap 'compose "$tree" down --volumes --timeout 1 >/dev/null 2>&1' EXIT
        compose "$tree" up --build --detach --wait --quiet-pull >/dev/null 2>&1 ||
            { compose "$tree" logs --tail 50; exit 1; }
        py=$(compose "$tree" exec -T app python -c \
            'import platform; print(platform.python_version())')
        servers="mongodb $(compose "$tree" exec -T mongodb mongod --version |
            sed -n 's/^db version v//p'); redis $(compose "$tree" exec -T redis \
            redis-server --version | sed -n 's/.* v=\([^ ]*\).*/\1/p')"
        # the cgroups of the services, whose CPU the first process of the
        # load reads in the measured window
        cgroups=
        for service in app app2 mongodb redis; do
            id=$(docker inspect --format '{{.Id}}' "$(compose "$tree" ps -q $service)")
            cgroups+=$service=/sys/fs/cgroup/system.slice/docker-$id.scope,
        done
        players=$work/players.json
        step seed --targets "$TARGETS" --players "$max_clients" --out "$players"
        for scenario in $SCENARIOS; do
            for clients in $(clients_of "$scenario"); do
                procs=$(( clients < LOAD_PROCS ? clients : LOAD_PROCS ))
                before=$(swap_in)
                parts=()
                pids=()
                offset=0
                for i in $(seq 0 $((procs - 1))); do
                    n=$(( clients / procs + (i < clients % procs ? 1 : 0) ))
                    part=$work/part-$i.json
                    parts+=("$part")
                    (cd "$repo/examples/game" && taskset -c $LOAD_CPUS "$python" \
                        -m perf load --scenario "$scenario" --targets "$TARGETS" \
                        --clients "$n" --offset "$offset" --players "$players" \
                        --cgroups "$( ((i == 0)) && echo "${cgroups%,}")" \
                        --warmup "$WARMUP" --duration "$DURATION" --out "$part") &
                    pids+=($!)
                    offset=$((offset + n))
                done
                for pid in "${pids[@]}"; do wait "$pid"; done
                step report "${parts[@]}" --out "$results" --run "$run" \
                    --round "$round" --version "$version" --role "$role" \
                    --commit "$commit" --python "$py" --servers "$servers" \
                    --host-state "$host_state" --scenario "$scenario" \
                    --clients "$clients" --load-cpus 4 \
                    --swap-in-before "$before" --swap-in-after "$(swap_in)"
            done
        done
        compose "$tree" down --volumes --timeout 1 >/dev/null 2>&1
        trap - EXIT
    done
done

step summary --csv "$results" --run "$run"
