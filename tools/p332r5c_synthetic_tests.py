#!/usr/bin/env python3
"""P3.32R5C: isolated synthetic tests; no repository writes or network calls."""
import copy
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

DAY = "2026-10-16"
SLOTS = ["10:00", "16:00", "19:00"]
SERIES = {
    "history": ["Tal Día Como Hoy", "El detalle que casi nadie ve", "¿Sabías esto de España?"],
    "dogs": ["Tu perro feliz", "Buenos modales", "¿Sabías esto de tu perro?"],
}
FILES = ["tools/p332r5_editorial_content_preflight.py",
         "tools/daily_editorial_evidence_gate.py",
         "scripts/p3_2_prepare_daily_content.py",
         "tools/p332r6_evidence_alignment.py"]

def run_case(repo, brand, case):
    with tempfile.TemporaryDirectory(prefix="p332r5c_") as tmp:
        root = pathlib.Path(tmp)
        for name in FILES:
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo / name, dest)
        (root / "content").mkdir()
        evidence_path = root / "evidence" / "approved" / (DAY + "-three-dossiers.json")
        evidence_path.parent.mkdir(parents=True)
        draft_path = root / "synthetic-draft.json"
        dossiers = []
        items = []
        for i, slot in enumerate(SLOTS):
            sources = [
                {"organization": "SyntheticOrgA", "name": "Synthetic A",
                 "url": "https://example.org/a", "facts": ["synthetic fact A"]},
                {"organization": "SyntheticOrgB", "name": "Synthetic B",
                 "url": "https://example.com/b", "facts": ["synthetic fact B"]},
            ]
            dossiers.append({"date": DAY, "slot": slot, "topic": "Synthetic topic " + str(i),
                             "sources": sources, "evidence_review_approved": True,
                             "publication_approved": False})
            items.append({"date": DAY, "slot": slot, "series": SERIES[brand][i],
                          "title": "Synthetic title " + str(i),\n                          "evidence_topic": "Synthetic topic " + str(i),
                          "hook": "Synthetic hook", "narration": "synthetic " * 185,
                          "caption": "Synthetic caption", "cta": "Synthetic CTA",
                          "hashtags": ["#synthetic"], "media": ["synthetic-placeholder"],
                          "duration_target": "65-75s",
                          "sources": [{"name": "Synthetic A", "url": "https://example.org/a"}]})
        evidence = {"date": DAY, "dossiers": dossiers}
        draft = {"date": DAY, "items": items}
        if case == "wrong_date":
            draft["date"] = "2026-10-15"
        elif case == "unapproved":
            evidence["dossiers"][0]["evidence_review_approved"] = False
        elif case == "same_org":
            evidence["dossiers"][0]["sources"][1]["organization"] = "SyntheticOrgA"
        elif case == "wrong_topic":\n            draft["items"][0]["evidence_topic"] = "Unrelated topic"\n        elif case == "unmatched_source":\n            draft["items"][0]["sources"][0]["url"] = "https://example.net/other"\n        elif case == "short_narration":
            draft["items"][0]["narration"] = "too short"
        elif case == "missing_dossier":
            pass
        elif case != "valid":
            raise ValueError(case)
        draft_path.write_text(json.dumps(draft), encoding="utf-8")
        if case != "missing_dossier":
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        cmd = [sys.executable, "-B", str(root / FILES[0]),
               "--brand", brand, "--repo-dir", str(root), "--date", DAY,
               "--draft", str(draft_path), "--dossiers", str(evidence_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
        output = result.stdout + result.stderr
        expected = case == "valid"
        success = (result.returncode == 0 and "P332R5_RESULT=PASS_DRY_RUN_ONLY" in output) if expected else (result.returncode != 0 and "BLOCKED" in output)
        no_content = not any((root / "content").iterdir())
        status = "PASS" if success and no_content else "FAIL"
        print("CASE=" + case + " STATUS=" + status + " EXIT=" + str(result.returncode))
        if status != "PASS":
            print(output[:1500])
        return status == "PASS"

def main():
    repo = pathlib.Path(__file__).resolve().parent.parent
    brand = sys.argv[1] if len(sys.argv) == 2 else ""
    if brand not in SERIES:
        print("USAGE: python -B tools/p332r5c_synthetic_tests.py history|dogs")
        return 2
    if any(not (repo / f).is_file() for f in FILES):
        print("BLOCKED_MISSING_REPOSITORY_FILES")
        return 2
    cases = ("valid", "missing_dossier", "wrong_date", "unapproved", "same_org", "short_narration", "wrong_topic", "unmatched_source")
    passed = sum(run_case(repo, brand, case) for case in cases)
    print("P332R5C_BRAND=" + brand + " PASS=" + str(passed) + "/" + str(len(cases)))
    print("REPOSITORY_WRITES=0 MODEL_CALLS=0 PUBLICATIONS=0")
    return 0 if passed == len(cases) else 1

if __name__ == "__main__":
    sys.exit(main())
