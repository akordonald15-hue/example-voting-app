"""Read a nonsensitive PVC receipt; fail closed before/after the upgrade."""
import json
import sys

def identity(obj, expected_uid=None):
    metadata, spec, status = obj["metadata"], obj["spec"], obj["status"]
    if (metadata.get("namespace"), metadata.get("name")) != ("voting-app", "data-capstone-voting-app-postgres-0"):
        raise ValueError("STOP: unexpected claim")
    uid, volume = metadata.get("uid"), spec.get("volumeName")
    if not uid or not volume or metadata.get("deletionTimestamp") or status.get("phase") != "Bound":
        raise ValueError("STOP: claim is not safely Bound")
    if expected_uid is not None and uid != expected_uid:
        raise ValueError("STOP: target claim identity differs from approved environment")
    return {"uid": uid, "volumeName": volume, "storageClassName": spec.get("storageClassName"),
            "capacity": status.get("capacity"), "requested": spec.get("resources", {}).get("requests")}

if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as source:
        print(json.dumps(identity(json.load(source), sys.argv[2] if len(sys.argv) == 3 else None), sort_keys=True))
