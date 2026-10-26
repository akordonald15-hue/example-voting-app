"""Offline tests: only application images may change during the gated deployment."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
import yaml

spec = importlib.util.spec_from_file_location("guard", Path(__file__).with_name("ci-check-render.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

class RenderGuardTests(unittest.TestCase):
    def setUp(self):
        self.docs = [{"kind": "Deployment", "metadata": {"name": "capstone-voting-app-" + role},
                      "spec": {"template": {"spec": {"containers": [{"name": role, "image":
                      "ghcr.io/akordonald15-hue/example-voting-app-" + role + "@sha256:" + "a" * 64}]}}}}
                     for role in ("vote", "result", "worker")]
        self.docs += [{"kind": "ConfigMap", "metadata": {"name": "fixture-" + str(n)}, "data": {"setting": "original"}} for n in range(14)]

    def normalize(self, docs, candidate=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "objects.yaml"
            path.write_text(yaml.safe_dump_all(docs), encoding="utf-8")
            return guard.normalized(path, candidate)

    def test_only_application_images_change(self):
        changed = copy.deepcopy(self.docs)
        changed[0]["spec"]["template"]["spec"]["containers"][0]["image"] = "ghcr.io/akordonald15-hue/example-voting-app-vote@sha256:" + "b" * 64
        self.assertEqual(self.normalize(self.docs), self.normalize(changed, True))

    def test_non_image_drift_remains_visible(self):
        changed = copy.deepcopy(self.docs)
        changed[3]["data"]["setting"] = "unexpected"
        self.assertNotEqual(self.normalize(self.docs), self.normalize(changed, True))

    def test_wrong_image_repository_rejected(self):
        self.docs[0]["spec"]["template"]["spec"]["containers"][0]["image"] = "upstream:latest"
        with self.assertRaises(AssertionError):
            self.normalize(self.docs, True)

    def test_missing_resource_rejected(self):
        with self.assertRaises(AssertionError):
            self.normalize(self.docs[:-1], True)

if __name__ == "__main__":
    unittest.main()
