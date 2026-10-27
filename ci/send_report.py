"""junit.xml se JSON report banata hai aur receiver ko POST karta hai."""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

JUNIT = "junit.xml"
RECEIVER_URL = os.environ.get("RECEIVER_URL", "http://localhost:8000/report")


def parse_tests(path):
    tests = []
    if not os.path.exists(path):
        return tests
    for tc in ET.parse(path).getroot().iter("testcase"):
        bad = tc.find("failure")
        if bad is None:
            bad = tc.find("error")
        if bad is not None:
            tests.append({
                "name": tc.get("name"),
                "result": "failed",
                "failure_message": (bad.get("message") or bad.text or "").strip(),
            })
        elif tc.find("skipped") is not None:
            tests.append({"name": tc.get("name"), "result": "skipped"})
        else:
            tests.append({"name": tc.get("name"), "result": "passed"})
    return tests


def main():
    tests = parse_tests(JUNIT)
    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)

    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "overall_status": "passed" if tests and failed == 0 else "failed",
    }

    req = urllib.request.Request(
        RECEIVER_URL,
        data=json.dumps(report).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Receiver replied:", resp.status)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Could not deliver report:", exc)
        sys.exit(1)