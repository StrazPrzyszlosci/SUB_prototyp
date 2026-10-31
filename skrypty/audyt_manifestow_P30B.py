"""Read-only provenance audit of immutable main commit; no simulation replay.

Checks file-hash mappings and Git blob entries. Run with Python stdlib only.
The comparison target is intentionally a commit, not a changing worktree.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "4d79871616ca1fd37a4b12c07de2c3febdb8e054"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)

def main():
    tree = git("ls-tree", "-r", "--name-only", BASE).decode().splitlines()
    paths = set(tree)
    cache = {}
    def data(path):
        if path not in cache:
            cache[path] = git("show", f"{BASE}:{path}")
        return cache[path]
    records = []
    def record(manifest, field, path, expected, algorithm):
        actual = None
        if path in paths:
            b = data(path)
            actual = (hashlib.sha256(b).hexdigest() if algorithm == "sha256"
                      else hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest())
        records.append(dict(manifest=manifest, field=field, path=path,
                            algorithm=algorithm, expected=expected, actual=actual,
                            status="missing" if actual is None else "match" if actual == expected else "different"))
    def visit(manifest, obj, pointer=""):
        if isinstance(obj, dict):
            if isinstance(obj.get("path"), str) and re.fullmatch(r"[0-9a-f]{40}", str(obj.get("sha", ""))):
                record(manifest, pointer, obj["path"], obj["sha"], "git_blob_sha1")
            for key, val in obj.items():
                if re.fullmatch(r"[0-9a-f]{64}", str(val)) and ("/" in key or key.endswith((".md", ".txt", ".json"))):
                    record(manifest, pointer + "/" + key, key, val, "sha256")
                elif isinstance(val, (list, dict)):
                    visit(manifest, val, pointer + "/" + key)
        elif isinstance(obj, list):
            for i, val in enumerate(obj):
                visit(manifest, val, pointer + "/" + str(i))
    manifests = [p for p in tree if p.startswith("wyniki/manifest") and p.endswith(".json")]
    for manifest in manifests:
        visit(manifest, json.loads(data(manifest)))
    tree_controls = []
    for path in ["brief_system_audio_DIY_v0.6.md", "wyniki/p29c_podsumowanie.json", "skrypty/wrazliwosc_P29C.py"]:
        b = data(path)
        calculated = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
        tree_reference = git("rev-parse", f"{BASE}:{path}").decode().strip()
        assert calculated == tree_reference
        tree_controls.append(dict(path=path, calculated=calculated, git_tree_reference=tree_reference, passed=True))
    summary = dict(base_commit=BASE, method="git show immutable commit; stdlib SHA256 and Git blob SHA1",
                   scope="Provenance only; neither numerical rerun nor scientific validation",
                   manifest_count=len(manifests), hash_references=len(records),
                   distinct_paths=len({r['path'] for r in records}),
                   counts=dict(collections.Counter(r["status"] for r in records)),
                   by_manifest={m: dict(collections.Counter(r["status"] for r in records if r["manifest"] == m)) for m in manifests},
                   differences=[r for r in records if r["status"] != "match"],
                   different_distinct_paths=len({r["path"] for r in records if r["status"] == "different"}),
                   independent_git_tree_controls=tree_controls,
                   brief_sha256=hashlib.sha256(data("brief_system_audio_DIY_v0.6.md")).hexdigest(),
                   interpretation="Historical hashes may legitimately differ after later documented updates; no automatic correction or inference of corruption.")
    (ROOT / "wyniki/p30_audyt_manifestow.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "wyniki/p30_audyt_referencje.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ["base_commit", "manifest_count", "hash_references", "distinct_paths", "counts"]}, indent=2))

if __name__ == "__main__":
    main()
