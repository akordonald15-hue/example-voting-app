"""Record pushed digests. No registry password or application Secret is exported."""
import json
import os
import re
import subprocess
import copy
from pathlib import Path

def release_values(sha, inspect=subprocess.check_output, base=None):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("STOP: invalid source SHA")
    components = {}
    for role in ("vote", "result", "worker"):
        repository = "ghcr.io/akordonald15-hue/example-voting-app-" + role
        refs = json.loads(inspect(
            ["docker", "image", "inspect", "--format", "{{json .RepoDigests}}", repository + ":" + sha], text=True))
        if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
            raise ValueError("STOP: missing registry digest")
        digests = {ref.split("@", 1)[1] for ref in refs if ref.startswith(repository + "@")}
        if len(digests) != 1:
            raise ValueError("STOP: ambiguous registry digest")
        digest = digests.pop()
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError("STOP: malformed registry digest")
        components[role] = {"image": {"repository": repository, "tag": sha, "digest": digest}}
    result = copy.deepcopy(base) if base is not None else {"components": {}}
    for role, value in components.items():
        result["components"].setdefault(role, {}).setdefault("image", {}).update(value["image"])
    return result

if __name__ == "__main__":
    # JSON is valid YAML. Emit only after every image validates; never a partial release.
    base = json.loads((Path(__file__).resolve().parents[1] / "releases/ci-base-values.json").read_text())
    print(json.dumps(release_values(os.environ["GITHUB_SHA"], base=base), indent=2))
