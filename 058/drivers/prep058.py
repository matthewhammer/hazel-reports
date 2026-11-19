#!/usr/bin/env python3
"""^report(58): the facts behind the table, gathered 2026-11-19 from GitHub and a checkout of hazelgrove/hazel.

Reads the scratch gather (gh pr view --json for each open PR of Matthew Hammer's that is not livelits work), fetched PR heads
(refs/mt/N, from refs/pull/N/head) and origin/dev, and writes 058/data/prs.json: for each PR its size, draft state, base, head
commit and date, its checks at the head, its reviews, and a trial merge into dev (git merge-tree --write-tree) with the files
that conflict. Run from ~/hazel:  python3 ~/hazel-perf-report/058/drivers/prep058.py <gather.json> <owners.json>"""
import json, subprocess, sys
raw = json.load(open(sys.argv[1])); owners = json.load(open(sys.argv[2]))
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True)
dev = git("rev-parse", "origin/dev").stdout.strip()
out = {"dev": {"commit": dev[:10], "date": git("log", "-1", "--format=%cs", dev).stdout.strip(),
               "last_merge": git("log", "-1", "--format=%s", dev).stdout.strip()}, "prs": {}}
for n, p in sorted(raw.items(), key=lambda x: int(x[0])):
    ref = f"refs/mt/{n}"
    have = git("rev-parse", "--verify", "-q", ref).returncode == 0
    rec = {k: p[k] for k in ("title", "draft", "base", "head", "add", "del", "nfiles", "mergeable", "mstate", "decision", "requested", "created", "updated", "labels", "ncommits")}
    rec["sha"] = p["sha"][:10]
    rec["checks"] = p["checks"]
    rec["checks_green"] = all(v in ("SUCCESS", "SKIPPED", "NEUTRAL") for v in p["checks"].values())
    rec["reviews"] = [dict(by=a, state=s, on=d) for a, s, d in p["reviews"] if a != "matthewhammer"]
    rec["files"] = [f for f, _, _ in p["files"]]
    if have and p["base"] == "dev":
        rec["head_date"] = git("log", "-1", "--format=%cs", ref).stdout.strip()
        rec["behind_dev"] = int(git("rev-list", "--count", f"{ref}..{dev}").stdout)
        mt = git("merge-tree", "--write-tree", "--name-only", "--no-messages", dev, ref)
        rec["into_dev"] = "clean" if mt.returncode == 0 else "conflict"
        rec["conflicts"] = [] if mt.returncode == 0 else [x for x in mt.stdout.split("\n")[1:] if x]
    rec["recent_authors"] = owners.get(n, [])
    out["prs"][n] = rec
json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else "prs.json", "w"), indent=1)
print(len(out["prs"]), "PRs; dev", out["dev"])
