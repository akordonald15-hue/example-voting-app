import importlib.util
import json
from pathlib import Path
import unittest

def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

release, pvc = load("ci-release-values"), load("ci-check-pvc")
running = load("ci-check-running")

class ReleaseTests(unittest.TestCase):
    def test_exact_sha_and_digest(self):
        def inspect(args, **kwargs):
            return json.dumps([args[-1].rsplit(":", 1)[0] + "@sha256:" + "b" * 64])
        result = release.release_values("a" * 40, inspect)
        self.assertEqual(len(result["components"]), 3)
        self.assertEqual(result["components"]["vote"]["image"]["tag"], "a" * 40)

    def test_no_or_ambiguous_digest_rejected(self):
        for refs in (None, [], ["wrong@sha256:" + "b" * 64]):
            with self.assertRaises(ValueError):
                release.release_values("a" * 40, lambda *a, **kw: json.dumps(refs))

    def test_invalid_sha_rejected(self):
        with self.assertRaises(ValueError):
            release.release_values("latest")

    def test_complete_values_preserve_backend(self):
        base = {"database": {"existingSecret": "voting-app-db"}, "components": {"postgres": {"image": "unchanged"}}}
        def inspect(args, **kwargs):
            return json.dumps([args[-1].rsplit(":", 1)[0] + "@sha256:" + "b" * 64])
        result = release.release_values("a" * 40, inspect, base)
        self.assertEqual(result["database"], base["database"])
        self.assertEqual(result["components"]["postgres"], base["components"]["postgres"])
        self.assertNotIn("vote", base["components"])

    def test_missing_pvc_uid_rejected(self):
        obj = {"metadata": {"name": "data-capstone-voting-app-postgres-0", "namespace": "voting-app"},
               "spec": {"volumeName": "pv"}, "status": {"phase": "Bound"}}
        with self.assertRaises(ValueError):
            pvc.identity(obj)

    def test_runtime_images_and_readiness(self):
        values, pods = {"components": {}}, {"items": []}
        for role in ("vote", "result", "worker", "redis", "postgres"):
            values["components"][role] = {"image": {"repository": role, "digest": "sha256:" + "a" * 64}}
            pods["items"].append({"metadata": {"uid": role, "labels": {"app.kubernetes.io/component": role}},
                "spec": {"containers": [{"image": role + "@sha256:" + "a" * 64}]},
                "status": {"containerStatuses": [{"ready": True}]}})
        self.assertEqual(len(running.check(values, pods)), 5)
        pods["items"][0]["status"]["containerStatuses"][0]["ready"] = False
        with self.assertRaises(ValueError):
            running.check(values, pods)

    def test_other_environment_claim_rejected(self):
        obj = {"metadata": {"name": "data-capstone-voting-app-postgres-0", "namespace": "voting-app", "uid": "replacement"},
               "spec": {"volumeName": "pv"}, "status": {"phase": "Bound"}}
        with self.assertRaises(ValueError):
            pvc.identity(obj, "approved-current-uid")

if __name__ == "__main__":
    unittest.main()
