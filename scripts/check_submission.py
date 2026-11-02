"""Report verified local checks and explicit external submission gates."""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(run_tests=False):
    manifest = json.loads((ROOT / "submission/project.json").read_text(encoding="utf-8"))
    findings = []
    def add(name, passed, detail):
        findings.append({"check": name, "status": "PASS" if passed else "PENDING", "detail": detail})
    git = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True, text=True)
    add("local_git", git.returncode == 0, "Local history does not prove when pre-existing code was written.")
    ignore = ROOT / ".gitignore"
    add("secret_exclusion", ignore.exists() and ".env" in ignore.read_text(), "Keys and recordings must be excluded from source publication.")
    suspicious = []
    pattern = re.compile(r"(?:LLM_[A-Za-z0-9_=-]{24,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,})")
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(p in {".git", "artifacts", "__pycache__", ".venv", ".cache"} for p in path.relative_to(ROOT).parts):
            continue
        if path.name.startswith(".env") or path.suffix not in {".py", ".js", ".html", ".css", ".md", ".json", ".yml", ".txt"}:
            continue
        if pattern.search(path.read_text(encoding="utf-8-sig", errors="replace")):
            suspicious.append(str(path.relative_to(ROOT)))
    add("source_secret_pattern_scan", not suspicious, {"flagged_files": suspicious, "limit": "Pattern scan only, not a guarantee."})
    if run_tests:
        tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=ROOT, capture_output=True, text=True)
        add("offline_tests", tests.returncode == 0, (tests.stdout + tests.stderr)[-2500:])
    add("track", manifest.get("track") in {"Indie Developer", "Startup"}, "Builder must choose the appropriate track.")
    people = manifest.get("contributors") or []
    add("team_and_representative", 1 <= len(people) <= 4 and manifest.get("representative") in people, "List all contributors and one representative, maximum four people.")
    add("prior_work_eligibility", manifest.get("organizer_reuse_confirmation") is True, "Resolve adapted-code eligibility for the selected track with organizers.")
    add("source_and_data_rights", manifest.get("rights_confirmed") is True, "Builder must confirm rights and redistribution terms.")
    add("official_rules", manifest.get("official_rules_accepted") is True, "Participant must review/accept the official rules.")
    add("public_repository", bool(manifest.get("public_repository_url")) and manifest.get("repository_public_verified") is True and manifest.get("repository_source_published") is True, "Verify public visibility and actual source publication; an empty public repository is insufficient.")
    seconds = manifest.get("video_duration_seconds")
    add("three_minute_video", isinstance(seconds, (int, float)) and 0 < seconds <= 180, "Final recording must be at most three minutes and identify new contributions.")
    add("public_video", bool(manifest.get("video_url")) and manifest.get("video_public_verified") is True, "Check the final hosted video while signed out.")
    add("cv_submission", manifest.get("platform_submitted") is True, "Representative must submit once and list all contributors.")
    deadline = datetime.fromisoformat(manifest["deadline_pacific"])
    add("before_deadline", datetime.now(timezone.utc) < deadline, manifest["deadline_pacific"])
    return {"checked_at": datetime.now(timezone.utc).isoformat(), "ready": all(f["status"] == "PASS" for f in findings), "checks": findings}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-tests", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.run_tests)
    encoded = json.dumps(report, indent=2)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    raise SystemExit(0 if report["ready"] else 2)
