"""Opt-in disposable LOCAL Docker regression; never contacts Kubernetes or AWS.

Uses exact image IDs (or legacy :stage5-local tags), a fresh private network/volume and generated
test-only credentials. Cleans up only resources it created in this invocation.
"""
import http.cookiejar
import http.client
import gzip
import argparse
import concurrent.futures
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, help="JSON mapping vote/result/worker to exact local image IDs")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--load-requests", type=int, default=200)
    args = parser.parse_args()
    prefix = "capstone-stage5-test-" + uuid.uuid4().hex[:10]
    network, volume = prefix + "-net", prefix + "-data"
    created, volumes, networks = [], [], []
    root = Path(__file__).resolve().parents[1]
    import yaml
    values = yaml.safe_load((root / "helm/voting-app/values.yaml").read_text())
    images = json.loads(args.images.read_text()) if args.images else {
        role: "example-voting-app-" + role + ":stage5-local" for role in ["vote", "result", "worker"]}
    if args.images:
        assert set(images) == {"vote", "result", "worker"}
        assert all(value.startswith("sha256:") and len(value) == 71 for value in images.values())
    evidence = {"images": images, "checks": [], "resultMemory": {}}
    backend = {role: c["image"]["repository"] + "@" + c["image"]["digest"]
               for role, c in values["components"].items() if role in ["redis", "postgres"]}

    def docker(*args, check=True):
        result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=90)
        if check and result.returncode:
            raise AssertionError("Docker operation failed: " + result.stderr[:500])
        return result.stdout.strip()

    def wait(check, seconds=90):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            try:
                if check():
                    return
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError,
                    TimeoutError, AssertionError, ValueError, KeyError):
                pass
            time.sleep(1)
        raise AssertionError("Timed out waiting for regression condition")

    def start(role, image, extra, command=()):
        name = prefix + "-" + role
        limit = values["components"][role]["resources"]["limits"]
        memory = limit["memory"].replace("Mi", "m").replace("Gi", "g")
        cpu = str(float(limit["cpu"][:-1]) / 1000) if limit["cpu"].endswith("m") else limit["cpu"]
        docker("run", "-d", "--name", name, "--network", network,
               "--label", "capstone.stage5.test=" + prefix,
               "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "--memory", memory, "--memory-swap", memory, "--cpus", cpu,
               *extra, image, *command)
        created.append(name)
        return name

    def port(name):
        return json.loads(docker("inspect", name))[0]["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(url, data=None):
        try:
            with opener.open(url, data=data, timeout=5) as response:
                return response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()

    try:
        docker("network", "create", network)
        networks.append(network)
        docker("volume", "create", volume)
        volumes.append(volume)
        # Only this newly created test volume: emulate kubelet fsGroup ownership.
        docker("run", "--rm", "--user", "0:0", "--mount", f"type=volume,src={volume},dst=/test-data",
               "--entrypoint", "sh", backend["postgres"], "-ec", "chown 70:70 /test-data")
        with tempfile.TemporaryDirectory(prefix=prefix) as temporary:
            env = Path(temporary) / "test.env"
            env.write_text("PGHOST=" + prefix + "-postgres\nPGPORT=5432\nPGUSER=capstone_user\n"
                           "PGDATABASE=capstone_votes\nPGPASSWORD=" + secrets.token_urlsafe(32) + ";:@/\n"
                           "REDIS_HOST=" + prefix + "-redis\nPORT=8080\n", encoding="utf-8")
            entries = dict(line.split("=", 1) for line in env.read_text().splitlines())
            pg_env = Path(temporary) / "postgres.env"
            pg_env.write_text("POSTGRES_USER=capstone_user\nPOSTGRES_DB=capstone_votes\nPOSTGRES_PASSWORD="
                              + entries["PGPASSWORD"] + "\nPGDATA=/var/lib/postgresql/data/pgdata\n", encoding="utf-8")
            pg = start("postgres", backend["postgres"], ["--user", "70:70", "--env-file", str(pg_env),
                       "--mount", f"type=volume,src={volume},dst=/var/lib/postgresql/data",
                       "--tmpfs", "/var/run/postgresql:rw,uid=70,gid=70,mode=0775",
                       "--tmpfs", "/tmp:rw,uid=70,gid=70,mode=1777"],
                       ["postgres", "-c", "max_connections=30", "-c", "shared_buffers=64MB"])
            redis = start("redis", backend["redis"], ["--user", "999:999", "--tmpfs", "/data:rw,uid=999,gid=999"],
                          ["redis-server", "--save", "", "--appendonly", "no", "--maxmemory", "64mb", "--maxmemory-policy", "noeviction"])
            wait(lambda: subprocess.run(["docker", "exec", pg, "pg_isready", "-h", "127.0.0.1", "-U", "capstone_user", "-d", "capstone_votes"], capture_output=True).returncode == 0)
            wait(lambda: docker("exec", redis, "redis-cli", "ping") == "PONG")
            # Keep DNS resolvable while making backends unavailable, as with Kubernetes Service DNS.
            docker("pause", pg)
            docker("pause", redis)
            common = ["--user", "1000:1000", "--env-file", str(env),
                      "--tmpfs", "/tmp:rw,uid=1000,gid=1000,mode=1777"]
            vote = start("vote", images["vote"],
                         [*common, "-p", "127.0.0.1::8080", "--entrypoint", "gunicorn"],
                         ["app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--worker-tmp-dir", "/tmp"])
            result = start("result", images["result"],
                           [*common, "-p", "127.0.0.1::8080"])
            vote_url, result_url = "http://127.0.0.1:" + port(vote), "http://127.0.0.1:" + port(result)
            for role, url in [("vote", vote_url), ("result", result_url)]:
                wait(lambda: request(url + "/health/live")[0] == 200)
                print("CHECK unavailable dependency readiness:", role, flush=True)
                assert request(url + "/health/ready")[0] == 503
            print("PASS independent liveness and dependency-sensitive readiness with paused backends", flush=True)
            evidence["checks"].append("liveness_200_readiness_503_with_unavailable_backends")
            docker("unpause", pg)
            docker("unpause", redis)
            worker = start("worker", images["worker"],
                           [*common, "-e", "WORKER_HEARTBEAT_PATH=/tmp/worker-heartbeat"])
            wait(lambda: request(vote_url + "/health/ready")[0] == 200)
            wait(lambda: request(result_url + "/health/ready")[0] == 200)
            wait(lambda: subprocess.run(["docker", "exec", worker, "test", "-s", "/tmp/worker-heartbeat"], capture_output=True, timeout=10).returncode == 0)
            assert request(vote_url + "/")[0] == request(result_url + "/")[0] == 200
            # CVE-2026-111181: a completed compressed body plus invalid trailing
            # bytes must not leave an unhandled decoder error that kills Result.
            malformed = gzip.compress(b"probe=local-regression") + b"invalid-trailing-frame"
            probe = urllib.request.Request(result_url + "/security-regression", data=malformed,
                headers={"Content-Type": "application/x-www-form-urlencoded", "Content-Encoding": "gzip"})
            try:
                with urllib.request.urlopen(probe, timeout=5) as response:
                    assert response.status in (400, 404)
            except urllib.error.HTTPError as error:
                assert error.code in (400, 404)
            time.sleep(1)
            assert request(result_url + "/health/ready")[0] == 200
            assert json.loads(docker("inspect", result))[0]["RestartCount"] == 0
            print("PASS compressed-body trailing-data regression: Result remains ready", flush=True)
            evidence["checks"].append("body_parser_trailing_compressed_data_no_process_crash")

            def sql(query):
                return docker("exec", pg, "sh", "-ec",
                              'PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -c "$1"',
                              "sh", query)

            assert request(vote_url + "/", urllib.parse.urlencode({"vote": "a"}).encode())[0] == 200
            wait(lambda: sql("SELECT count(*) FROM votes WHERE vote='a'") == "1")
            assert request(vote_url + "/", urllib.parse.urlencode({"vote": "b"}).encode())[0] == 200
            wait(lambda: sql("SELECT count(*) FROM votes WHERE vote='b'") == "1")
            assert sql("SELECT count(*) FROM votes") == "1", "Same browser must update its existing vote"
            # Exercise actual Socket.IO polling protocol, not just the static HTML response.
            status, handshake = request(result_url + "/socket.io/?EIO=4&transport=polling")
            assert status == 200 and handshake.startswith("0")
            sid = json.loads(handshake[1:])["sid"]
            poll = result_url + "/socket.io/?EIO=4&transport=polling&sid=" + sid
            assert request(poll, b"40")[0] == 200
            def updated_scores():
                for packet in request(poll)[1].split("\x1e"):
                    if packet.startswith("42"):
                        event = json.loads(packet[2:])
                        if event[0] == "scores" and json.loads(event[1]) == {"a": 0, "b": 1}:
                            return True
                return False

            wait(updated_scores)
            # Exercise the shipped browser client's WebSocket transport using Node's WebSocket API.
            client_test = """
                const io = require('/usr/local/app/views/socket.io.js');
                const timer = setTimeout(() => { console.error('WebSocket scores timeout'); process.exit(1); }, 15000);
                const socket = io(process.argv[1], {transports: ['websocket']});
                socket.on('connect_error', error => { console.error(error.message); process.exit(1); });
                socket.on('scores', payload => {
                    const scores = JSON.parse(payload);
                    if (scores.a === 0 && scores.b === 1) {
                        socket.disconnect(); clearTimeout(timer);
                        console.log('PASS shipped Socket.IO client over WebSocket'); process.exit(0);
                    }
                });
            """
            docker("run", "--rm", "--network", network, "--read-only", "--cap-drop", "ALL",
                   "--security-opt", "no-new-privileges", "--entrypoint", "node", images["result"],
                   "-e", client_test, "http://" + result + ":8080")
            print("PASS shipped Socket.IO browser client over WebSocket", flush=True)
            evidence["checks"].append("shipped_socketio_client_websocket_exact_scores")
            print("PASS custom DNS/database/user/password, vote processing, same-browser update and Socket.IO scores", flush=True)
            evidence["checks"].append("vote_database_cookie_update_exact_socketio_scores")
            # Concurrent HTTP/readiness traffic at the chart's actual resource limits.
            def load_request(index):
                url = result_url + ("/health/ready" if index % 4 == 0 else "/")
                with urllib.request.urlopen(url, timeout=10) as response:
                    return response.status
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                assert all(code == 200 for code in pool.map(load_request, range(args.load_requests)))
            state = json.loads(docker("inspect", result))[0]
            assert state["HostConfig"]["Memory"] == 192 * 1024 * 1024
            assert state["HostConfig"]["MemorySwap"] == state["HostConfig"]["Memory"]
            assert state["State"]["Running"] and not state["State"]["OOMKilled"] and state["RestartCount"] == 0
            peak = docker("exec", result, "sh", "-ec",
                          'if test -r /sys/fs/cgroup/memory.peak; then cat /sys/fs/cgroup/memory.peak; else cat /sys/fs/cgroup/memory/memory.max_usage_in_bytes; fi')
            evidence["resultMemory"] = {"limitBytes": state["HostConfig"]["Memory"], "peakBytes": int(peak),
                                        "oomKilled": False, "restarts": 0, "httpRequests": args.load_requests,
                                        "concurrency": 8, "nanoCpus": state["HostConfig"]["NanoCpus"]}
            print("PASS Result at 192Mi/no swap/500m:", json.dumps(evidence["resultMemory"]), flush=True)
            for name, uid in [(vote, "1000"), (result, "1000"), (worker, "1000"), (pg, "70"), (redis, "999")]:
                assert docker("exec", name, "id", "-u") == uid
                status = docker("exec", name, "cat", "/proc/1/status")
                process_uid = next(line.split()[1] for line in status.splitlines() if line.startswith("Uid:"))
                assert process_uid == uid, "PID 1 must also be non-root"
                inspected = json.loads(docker("inspect", name))[0]
                assert inspected["HostConfig"]["ReadonlyRootfs"] and inspected["HostConfig"]["CapDrop"] == ["ALL"]
                if name in [vote, result, worker]:
                    role = {vote: "vote", result: "result", worker: "worker"}[name]
                    assert inspected["Config"]["Image"] == images[role]
            print("PASS actual non-root UIDs and read-only root filesystems", flush=True)
            evidence["checks"].append("exact_image_ids_runtime_uids_readonly_capabilities")
            docker("restart", pg)
            wait(lambda: sql("SELECT count(*) FROM votes WHERE vote='b'") == "1")
            wait(lambda: request(result_url + "/health/ready")[0] == 200)
            assert request(vote_url + "/", urllib.parse.urlencode({"vote": "a"}).encode())[0] == 200
            wait(lambda: sql("SELECT count(*) FROM votes WHERE vote='a'") == "1")
            assert sql("SELECT count(*) FROM votes") == "1"
            recovered_client = client_test.replace("scores.a === 0 && scores.b === 1", "scores.a === 1 && scores.b === 0")
            docker("run", "--rm", "--network", network, "--read-only", "--cap-drop", "ALL",
                   "--security-opt", "no-new-privileges", "--entrypoint", "node", images["result"],
                   "-e", recovered_client, "http://" + result + ":8080")
            for name in [vote, result, worker]:
                assert json.loads(docker("inspect", name))[0]["State"]["Running"]
            evidence["checks"].append("end_to_end_vote_and_socketio_after_database_restart")
            print("PASS persistence and full vote/Socket.IO recovery after database restart", flush=True)
            evidence["checks"].append("persistent_database_after_restart")
            evidence["shutdown"] = {}
            for role, name in [("vote", vote), ("result", result), ("worker", worker)]:
                docker("stop", "--time", "15", name)
                stopped = json.loads(docker("inspect", name))[0]["State"]
                assert not stopped["Running"] and not stopped["OOMKilled"] and stopped["ExitCode"] == 0
                evidence["shutdown"][role] = {"exitCode": stopped["ExitCode"], "oomKilled": stopped["OOMKilled"]}
            print("PASS bounded application shutdown without SIGKILL/OOM", flush=True)
            evidence["checks"].append("bounded_shutdown_without_sigkill_oom")
            evidence["status"] = "PASS"
    except Exception as error:
        evidence["status"] = "FAIL"
        evidence["failureType"] = type(error).__name__
        evidence["containerStatesAtFailure"] = {}
        for name in created:
            inspected = json.loads(docker("inspect", name))[0]
            evidence["containerStatesAtFailure"][name] = {
                "state": inspected["State"], "restartCount": inspected["RestartCount"],
                "memoryLimit": inspected["HostConfig"]["Memory"]}
        raise
    finally:
        if args.report:
            args.report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        # Never enumerate/delete other project resources; only invocation-owned IDs/names.
        for name in reversed(created):
            docker("rm", "-f", name, check=False)
        for name in volumes:
            docker("volume", "rm", name, check=False)
        for name in networks:
            docker("network", "rm", name, check=False)


if __name__ == "__main__":
    main()
