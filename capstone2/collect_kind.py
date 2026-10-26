"""Read-only receipts from the explicitly named local kind node; no default context."""
import datetime, json, subprocess, urllib.parse
from pathlib import Path
NODE = "capstone-rollback-lab-control-plane"
K = ["docker", "exec", NODE, "kubectl", "--request-timeout=15s"]
def read(args):
    return subprocess.check_output(K + args, text=True, timeout=30)
def query(service, port, path):
    return read(["get", "--raw", f"/api/v1/namespaces/observability/services/http:{service}:{port}/proxy" + path])
def main():
    nodes=json.loads(read(["get","nodes","-o","json"]))["items"]
    if [n["metadata"]["name"] for n in nodes] != [NODE]:
        raise SystemExit("Wrong local cluster")
    out=Path(__file__).resolve().parent / "evidence/runtime"
    for ns in ("robot-shop","observability"):
        pods=json.loads(read(["get","pods","-n",ns,"-o","json"]))["items"]
        receipt={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"pods":[{
            "name":p["metadata"]["name"],"phase":p["status"]["phase"],
            "containers":[{"name":c["name"],"ready":c["ready"],"restarts":c["restartCount"],"image":c["image"],"imageID":c.get("imageID")} for c in p["status"].get("containerStatuses",[])]} for p in pods]}
        (out/(ns+"-latest.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    for name,expr in {"prometheus-up":"up", "probe-success":"probe_success", "red-counters":"http_server_requests_total", "red-rates":"rate(http_server_requests_total[2m])", "red-latency-buckets":"http_server_request_duration_seconds_bucket"}.items():
        (out/(name+".json")).write_text(query("monitoring-prometheus",9090,"/api/v1/query?"+urllib.parse.urlencode({"query":expr}))+"\n")
    print("Saved sanitized local Pod and Prometheus receipts")
if __name__ == "__main__": main()
