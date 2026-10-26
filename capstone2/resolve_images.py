"""Resolve public image metadata locally; never pull, push or deploy an image."""
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parent
values = yaml.safe_load((ROOT / "observability/values.yaml").read_text())
pins = {"components": {}}
for name, image in list(values["components"].items()) + [("fluentbit", values["fluentbit"])]:
    data = json.loads(subprocess.check_output(["docker", "buildx", "imagetools", "inspect",
        image["repository"] + ":" + str(image["version"]), "--format", "{{json .Manifest}}"], text=True, timeout=90))
    digest = data["digest"]
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise ValueError("STOP: invalid digest")
    if name == "fluentbit":
        pins[name] = {"digest": digest}
    else:
        pins["components"][name] = {"digest": digest}
# Write only after every metadata lookup succeeds. Pins require scan/runtime approval.
(ROOT / "images.resolved.yaml").write_text(yaml.safe_dump(pins, sort_keys=True))
print("RESOLVED METADATA ONLY; not scanned or deployment-approved")
