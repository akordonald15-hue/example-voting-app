"""Prevent filtered vulnerability reports or fail-open runtime-image scans."""
from pathlib import Path
import unittest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/capstone.yaml"


class SecurityWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.verify = yaml.safe_load(WORKFLOW.read_text())["jobs"]["verify"]
        self.steps = self.verify["steps"]

    def test_all_runtime_images_have_complete_fail_closed_reports(self):
        scans = [s for s in self.steps if s.get("uses", "").startswith("aquasecurity/trivy-action@")]
        self.assertEqual(len(scans), 3)
        self.assertFalse(self.verify.get("continue-on-error", False))
        self.assertEqual({s["with"]["image-ref"] for s in scans},
                         {"capstone-" + r + ":test" for r in ("vote", "result", "worker")})
        for scan in scans:
            settings = scan["with"]
            self.assertEqual(set(settings["severity"].split(",")),
                             {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"})
            self.assertEqual(str(settings["exit-code"]), "1")
            self.assertIs(settings["ignore-unfixed"], False)
            self.assertEqual(settings["scanners"], "vuln")
            self.assertEqual(settings["format"], "json")
            self.assertFalse(scan.get("continue-on-error", False))

    def test_scans_follow_final_target_build_and_reports_survive_failure(self):
        build = next(s for s in self.steps if s.get("name") == "Build final runtime targets")
        self.assertIn("--target final", build["run"])
        self.assertIn("--tag capstone-$role:test", build["run"])
        self.assertIn("for role in vote result worker", build["run"])
        scans = [s for s in self.steps if s.get("uses", "").startswith("aquasecurity/trivy-action@")]
        for scan in scans:
            self.assertLess(self.steps.index(build), self.steps.index(scan))
            role = scan["with"]["image-ref"].removeprefix("capstone-").removesuffix(":test")
            self.assertEqual(scan["with"]["output"], "trivy-" + role + ".json")
        upload = next(s for s in self.steps if s.get("with", {}).get("name") == "acceptance")
        self.assertEqual(upload["if"], "always()")
        self.assertIn("trivy-*.json", upload["with"]["path"].splitlines())


if __name__ == "__main__":
    unittest.main()
