"""Permit only three application image changes; reject storage/security/backend drift."""
import copy
import re
import sys
import yaml

def normalized(path, candidate=False):
    with open(path, encoding="utf-8") as source:
        docs = list(yaml.safe_load_all(source))
    assert len(docs) == 17
    result = {}
    count = 0
    for original in docs:
        obj = copy.deepcopy(original)
        key = (obj["kind"], obj["metadata"]["name"])
        assert key not in result
        if key[0] == "Deployment" and key[1] in {
            "capstone-voting-app-" + role for role in ("vote", "result", "worker")
        }:
            containers = obj["spec"]["template"]["spec"]["containers"]
            assert len(containers) == 1
            if candidate:
                role = key[1].removeprefix("capstone-voting-app-")
                assert re.fullmatch("ghcr.io/akordonald15-hue/example-voting-app-" + role + r"@sha256:[0-9a-f]{64}", containers[0]["image"])
            containers[0]["image"] = "REVIEWED_APPLICATION_IMAGE"
            count += 1
        result[key] = obj
    assert count == 3
    return result

if __name__ == "__main__":
    assert normalized(sys.argv[1]) == normalized(sys.argv[2], True), "STOP: change outside three application images"
    print("PASS only application image fields may differ")
