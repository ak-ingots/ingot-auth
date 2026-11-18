"""
The steps of a run of the load, each a command:

- ``seed --players N --out FILE``: N players signed up and in by a
  nickname, their nicknames and tokens kept in FILE;
- ``load --scenario S --clients N ...``: one process of the load, N clients
  each calling as fast as it is answered, warmed up, then measured; the
  latencies, the CPU of the process and, given ``--cgroups``, that of the
  services in the measured window into a JSON file;
- ``report --out CSV ...``: the files of the processes of a point merged,
  its rows appended to the CSV, a line of it printed;
- ``host``: the state of the host as a run keeps it, or why it refuses;
- ``summary --csv CSV --run RUN``: the median of the rounds of each point of
  a run, the baseline and the candidate side by side.
"""

import argparse
import asyncio
import csv
import datetime
import json
import os
import pathlib
import platform
import statistics
import sys
import time
import typing as t
import uuid

import grpc

from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc
from ingot_auth.profiles.v1 import profiles_pb2, profiles_pb2_grpc

# the password of every player: its strength is not under test
PASSWORD = "s3cret-password"

# what a run refuses below: the memory available, in KiB
MIN_AVAILABLE_KIB = 2 * 1024 * 1024

# the load saturated its cores over this share of them: the point is void
MAX_LOAD_CPU = 0.9

# a point measuring fewer calls tells nothing: the point is void
MIN_CALLS = 20

# the IDE connected to the server, which a run wants off
IDE_MARKERS = ("JetBrains/RemoteDev", "pycharm")

# Claude Code, which takes up to a third of a CPU while it works: allowed
# on the cores of the system alone, those docker-compose.perf.yml leaves it
AGENT_COMM = "claude"
SYSTEM_CPUS = frozenset({0, 1})

SCENARIOS = ("get-own-profile", "sign-in", "sign-up")

# the metrics of a point the summary compares
SUMMARY_METRICS = ("rps", "p50_ms", "p95_ms", "cpu_ms_per_call")

CSV_FIELDS = (
    "date",
    "run",
    "round",
    "version",
    "role",
    "commit",
    "python",
    "servers",
    "host",
    "host_state",
    "scenario",
    "clients",
    "metric",
    "value",
)


class Client:
    """A player's calls to one process of the game."""

    def __init__(self, channel: grpc.aio.Channel) -> None:
        self.nickname = nickname_pb2_grpc.NicknameStub(channel)
        self.profiles = profiles_pb2_grpc.ProfilesStub(channel)

    async def sign_up(self, nickname: str) -> None:
        request = nickname_pb2.SignUpRequest(nickname=nickname, password=PASSWORD)
        await self.nickname.SignUp(request)

    async def sign_in(self, nickname: str) -> str:
        request = nickname_pb2.SignInRequest(nickname=nickname, password=PASSWORD)
        response = await self.nickname.SignIn(request)
        return str(response.result.signed_in.token)

    async def get_own_profile(self, token: str) -> None:
        metadata = [("authorization", f"Bearer {token}")]
        await self.profiles.GetOwnProfile(
            profiles_pb2.GetOwnProfileRequest(), metadata=metadata
        )


def read_cgroups(cgroups: dict[str, str]) -> dict[str, float]:
    """The CPU each cgroup has used, in seconds, by its ``cpu.stat``."""
    usage = {}
    for name, path in cgroups.items():
        for line in pathlib.Path(path, "cpu.stat").read_text().splitlines():
            key, value = line.split()
            if key == "usage_usec":
                usage[name] = int(value) / 1_000_000
    return usage


def new_nickname() -> str:
    return f"perf-{uuid.uuid4().hex[:16]}"


async def seed(targets: list[str], players: int, out: pathlib.Path) -> None:
    """Players signed up and in, spread over the processes, in parallel."""
    channels = [grpc.aio.insecure_channel(target) for target in targets]
    clients = [Client(channel) for channel in channels]
    semaphore = asyncio.Semaphore(16)

    async def create(index: int) -> dict[str, str]:
        client = clients[index % len(clients)]
        nickname = new_nickname()
        async with semaphore:
            await client.sign_up(nickname)
            return {"nickname": nickname, "token": await client.sign_in(nickname)}

    seeded = await asyncio.gather(*(create(index) for index in range(players)))
    out.write_text(json.dumps(seeded))
    for channel in channels:
        await channel.close()


async def load(
    scenario: str,
    targets: list[str],
    clients: int,
    offset: int,
    players: list[dict[str, str]],
    warmup: float,
    duration: float,
    cgroups: dict[str, str],
) -> dict[str, t.Any]:
    """
    ``clients`` calling as fast as answered, each its own player from
    ``offset`` on, its own process of the game in turn: the latencies of the
    calls ending in the measured window, the errors, the CPU of the process
    and that of the services by their ``cgroups`` in the window.
    """
    channels = [grpc.aio.insecure_channel(target) for target in targets]
    latencies: list[float] = []
    errors: dict[str, int] = {}
    loop = asyncio.get_running_loop()
    start = loop.time() + warmup
    end = start + duration
    services: dict[str, float] = {}

    async def measure() -> None:
        await asyncio.sleep(start - loop.time())
        before = read_cgroups(cgroups)
        await asyncio.sleep(end - loop.time())
        after = read_cgroups(cgroups)
        services.update({name: after[name] - before[name] for name in after})

    async def call(index: int) -> None:
        client = Client(channels[(offset + index) % len(channels)])
        player = players[(offset + index) % len(players)] if players else {}
        while (begun := loop.time()) < end:
            try:
                if scenario == "get-own-profile":
                    await client.get_own_profile(player["token"])
                elif scenario == "sign-in":
                    await client.sign_in(player["nickname"])
                else:
                    await client.sign_up(new_nickname())
            except grpc.aio.AioRpcError as error:
                if begun >= start:
                    name = error.code().name
                    errors[name] = errors.get(name, 0) + 1
                continue
            done = loop.time()
            if begun >= start and done <= end:
                latencies.append(done - begun)

    cpu = time.process_time()
    await asyncio.gather(measure(), *(call(index) for index in range(clients)))
    cpu = time.process_time() - cpu
    for channel in channels:
        await channel.close()
    return {
        "latencies": latencies,
        "errors": errors,
        "cpu": cpu,
        "services": services,
        "wall": warmup + duration,
        "duration": duration,
    }


def percentile(values: list[float], share: float) -> float:
    return statistics.quantiles(values, n=100, method="inclusive")[int(share) - 1]


def report(args: argparse.Namespace) -> None:
    """The processes of a point merged: its rows appended, a line printed."""
    parts = [json.loads(pathlib.Path(path).read_text()) for path in args.parts]
    latencies = sorted(x for part in parts for x in part["latencies"])
    codes: dict[str, int] = {}
    for part in parts:
        for code, count in part["errors"].items():
            codes[code] = codes.get(code, 0) + count
    errors = sum(codes.values())
    duration = parts[0]["duration"]
    load_cpu = sum(p["cpu"] for p in parts) / parts[0]["wall"] / args.load_cpus
    swapped = args.swap_in_after - args.swap_in_before
    services = {n: cpu for part in parts for n, cpu in part["services"].items()}
    void = []
    if load_cpu > MAX_LOAD_CPU:
        void.append(f"load-cpu {load_cpu:.2f}")
    if swapped:
        void.append(f"swap-in {swapped}")
    if len(latencies) < MIN_CALLS:
        void.append(f"calls {len(latencies)}")
    metrics: dict[str, t.Any] = {
        "calls": len(latencies),
        "rps": len(latencies) / duration,
        "errors": errors,
        **{f"errors_{code}": count for code, count in sorted(codes.items())},
        "load_cpu": round(load_cpu, 3),
        **{f"cpu_cores_{name}": cpu / duration for name, cpu in services.items()},
        "void": "; ".join(void),
    }
    if services and latencies:
        cpu_ms = sum(services.values()) * 1000
        metrics["cpu_ms_per_call"] = cpu_ms / len(latencies)
    if len(latencies) > 1:
        metrics["p50_ms"] = percentile(latencies, 50) * 1000
        metrics["p95_ms"] = percentile(latencies, 95) * 1000
    common = {
        "date": datetime.date.today().isoformat(),
        "run": args.run,
        "round": args.round,
        "version": args.version,
        "role": args.role,
        "commit": args.commit,
        "python": args.python,
        "servers": args.servers,
        "host": platform.node(),
        "host_state": args.host_state,
        "scenario": args.scenario,
        "clients": args.clients,
    }
    out = pathlib.Path(args.out)
    is_new = not out.exists()
    with out.open("a", newline="") as file:
        writer = csv.DictWriter(file, CSV_FIELDS)
        if is_new:
            writer.writeheader()
        for metric, value in metrics.items():
            if isinstance(value, float):
                value = round(value, 3)
            writer.writerow(common | {"metric": metric, "value": value})
    p50 = metrics.get("p50_ms", 0.0)
    p95 = metrics.get("p95_ms", 0.0)
    print(
        f"{args.role:9} {args.round} {args.scenario:15} {args.clients:>4} clients:"
        f" {metrics['rps']:8.1f}/s p50 {p50:7.2f} ms p95 {p95:7.2f} ms"
        f" cpu {metrics.get('cpu_ms_per_call', 0.0):.2f} ms/call"
        f" errors {errors} load {load_cpu:.2f}"
        + "".join(f" {code} {count}" for code, count in sorted(codes.items()))
        + (f" VOID {metrics['void']}" if void else "")
    )


def read_file(path: str) -> str:
    try:
        return pathlib.Path(path).read_text().strip()
    except OSError:
        return "?"


def get_affinity(pid: int) -> frozenset[int]:
    """The CPUs of a process; one gone meanwhile, none."""
    try:
        return frozenset(os.sched_getaffinity(pid))
    except OSError:
        return frozenset()


def host(args: argparse.Namespace) -> None:
    """The state of the host; with --check, why a run refuses to start."""
    cpu = "?"
    for line in read_file("/proc/cpuinfo").splitlines():
        if line.startswith("model name"):
            cpu = line.split(":", 1)[1].strip()
            break
    meminfo = dict(
        line.split(":", 1) for line in read_file("/proc/meminfo").splitlines()
    )
    available = int(meminfo.get("MemAvailable", "0 kB").split()[0])
    boost = read_file("/sys/devices/system/cpu/cpufreq/boost")
    epp = read_file(
        "/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference"
    )
    ide = [
        pid
        for pid in os.listdir("/proc")
        if pid.isdigit()
        and any(m in read_file(f"/proc/{pid}/cmdline") for m in IDE_MARKERS)
    ]
    agents = [
        pid
        for pid in os.listdir("/proc")
        if pid.isdigit() and read_file(f"/proc/{pid}/comm") == AGENT_COMM
    ]
    loose = [pid for pid in agents if not get_affinity(int(pid)) <= SYSTEM_CPUS]
    agent = "loose" if loose else "pinned" if agents else "off"
    state = (
        f"{cpu}; kernel {platform.release()}; boost {boost}; epp {epp};"
        f" available {available // 1024} MiB; ide {'on' if ide else 'off'};"
        f" claude {agent}"
    )
    if not args.check:
        print(state)
        return
    refusals = []
    if boost != "0":
        refusals.append("the boost is on: sudo examples/game/perf/perf-host.sh on")
    if ide:
        refusals.append("the IDE is running on the server: close it")
    for pid in loose:
        refusals.append(
            f"Claude Code runs on every CPU: close it or taskset -apc 0-1 {pid}"
        )
    if available < MIN_AVAILABLE_KIB:
        refusals.append(f"{available // 1024} MiB available, under 2 GiB")
    for refusal in refusals:
        print(f"refused: {refusal}", file=sys.stderr)
    sys.exit(1 if refusals else 0)


def summary(args: argparse.Namespace) -> None:
    """The median of the rounds of each point, by the role, side by side."""
    values: dict[tuple[str, int, str, str], list[float]] = {}
    void: set[tuple[str, int, str]] = set()
    with open(args.csv, newline="") as file:
        for row in csv.DictReader(file):
            if row["run"] != args.run:
                continue
            point = (row["scenario"], int(row["clients"]), row["role"])
            if row["metric"] == "void" and row["value"]:
                void.add(point)
            elif row["metric"] in SUMMARY_METRICS:
                key = (*point, row["metric"])
                values.setdefault(key, []).append(float(row["value"]))
    points = sorted({(s, c) for s, c, _, _ in values})
    print(f"run {args.run}: the median of the rounds, baseline -> candidate")
    for scenario, clients in points:
        cells = []
        for metric in SUMMARY_METRICS:
            pair = [
                statistics.median(values.get((scenario, clients, role, metric), [0]))
                for role in ("baseline", "candidate")
            ]
            change = (pair[1] / pair[0] - 1) * 100 if pair[0] else 0.0
            cells.append(f"{metric} {pair[0]:.1f} -> {pair[1]:.1f} ({change:+.1f}%)")
        marks = [r for r in ("baseline", "candidate") if (scenario, clients, r) in void]
        print(
            f"{scenario:15} {clients:>4}: "
            + ", ".join(cells)
            + (f" VOID in {', '.join(marks)}" if marks else "")
        )


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m perf")
    commands = parser.add_subparsers(dest="command", required=True)
    seed_parser = commands.add_parser("seed")
    seed_parser.add_argument("--targets", required=True)
    seed_parser.add_argument("--players", type=int, required=True)
    seed_parser.add_argument("--out", required=True)
    load_parser = commands.add_parser("load")
    load_parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    load_parser.add_argument("--targets", required=True)
    load_parser.add_argument("--clients", type=int, required=True)
    load_parser.add_argument("--offset", type=int, default=0)
    load_parser.add_argument("--players")
    load_parser.add_argument("--cgroups", default="")
    load_parser.add_argument("--warmup", type=float, default=10)
    load_parser.add_argument("--duration", type=float, default=30)
    load_parser.add_argument("--out", required=True)
    report_parser = commands.add_parser("report")
    report_parser.add_argument("parts", nargs="+")
    for name in (
        "out",
        "run",
        "round",
        "version",
        "role",
        "commit",
        "python",
        "servers",
        "host-state",
        "scenario",
    ):
        report_parser.add_argument(f"--{name}", required=True)
    report_parser.add_argument("--clients", type=int, required=True)
    report_parser.add_argument("--load-cpus", type=int, required=True)
    report_parser.add_argument("--swap-in-before", type=int, required=True)
    report_parser.add_argument("--swap-in-after", type=int, required=True)
    summary_parser = commands.add_parser("summary")
    summary_parser.add_argument("--csv", required=True)
    summary_parser.add_argument("--run", required=True)
    host_parser = commands.add_parser("host")
    host_parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.command == "seed":
        asyncio.run(seed(args.targets.split(","), args.players, pathlib.Path(args.out)))
    elif args.command == "load":
        players = (
            json.loads(pathlib.Path(args.players).read_text()) if args.players else []
        )
        result = asyncio.run(
            load(
                args.scenario,
                args.targets.split(","),
                args.clients,
                args.offset,
                players,
                args.warmup,
                args.duration,
                dict(item.split("=", 1) for item in args.cgroups.split(",") if item),
            )
        )
        pathlib.Path(args.out).write_text(json.dumps(result))
    elif args.command == "report":
        report(args)
    elif args.command == "summary":
        summary(args)
    else:
        host(args)


if __name__ == "__main__":
    main()
