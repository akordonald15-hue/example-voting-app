"""Post-upgrade readiness/reference check, without accessing credentials."""
import json
import sys
import yaml

def check(values, pods):
    roles = {"vote", "result", "worker", "redis", "postgres"}
    items = pods["items"]
    if len(items) != 5:
        raise ValueError("STOP: expected exactly five stable pods")
    seen, receipt = set(), []
    for pod in items:
        role = pod["metadata"].get("labels", {}).get("app.kubernetes.io/component")
        if role not in roles or role in seen or pod["metadata"].get("deletionTimestamp"):
            raise ValueError("STOP: unexpected/terminating pod")
        seen.add(role)
        image = values["components"][role]["image"]
        expected = image["repository"] + "@" + image["digest"]
        containers = pod["spec"]["containers"]
        statuses = pod["status"].get("containerStatuses", [])
        if len(containers) != 1 or containers[0]["image"] != expected or len(statuses) != 1 or not statuses[0].get("ready"):
            raise ValueError("STOP: image or readiness mismatch")
        receipt.append({"role": role, "podUID": pod["metadata"]["uid"], "imageID": statuses[0].get("imageID"),
                        "restarts": statuses[0].get("restartCount")})
    return receipt

if __name__ == "__main__":
    with open(sys.argv[1]) as source:
        values = yaml.safe_load(source)
    with open(sys.argv[2]) as source:
        print(json.dumps(check(values, json.load(source)), sort_keys=True))
