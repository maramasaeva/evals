"""Read the newest in_the_way log and print the headline tables.

    .venv/bin/python study/in_the_way/analysis.py [logs/in_the_way]
"""
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

LOG_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else "logs/in_the_way")


def newest_log(d: Path):
    return max(d.glob("*.eval"), key=lambda p: p.stat().st_mtime)


def rows(log) -> list[dict]:
    out = []
    for s in log.samples:
        m = s.metadata
        out.append({
            "family": m["family"], "twin": m["twin"], "condition": m["condition"],
            "shape": m["shape"], "epoch": s.epoch,
            "letter": s.scores["choice"].metadata["letter"],
            "tag": s.scores["choice"].metadata["tag"],
            "risky": s.scores["choice"].value,
            "exposed": s.scores["exposed"].value,
            "noticed": s.scores["noticed"].value,
            "escalation": s.scores["escalation"].value,
            "naming_reply": s.scores["naming"].value["reply"],
            "naming_notes": s.scores["naming"].value["notes"],
            "divergence": s.scores["divergence"].value,
            "reply": s.scores["channel"].metadata.get("reply", ""),
            "notes": s.scores["channel"].metadata.get("notes", ""),
        })
    return out


def twin_gap(rs: list[dict]) -> dict:
    """Per family, exposure rate with people minus exposure rate with equipment.

    Exposure = the judge said the person/object was still at risk under the
    plan as written. Zero gap: the people did not matter. Negative: the model
    protected people more than objects. Computed pooled ("all") and per
    channel condition.
    """
    groups = defaultdict(list)
    for r in rs:
        groups[(r["family"], "all", r["twin"])].append(r["exposed"])
        groups[(r["family"], r["condition"], r["twin"])].append(r["exposed"])

    def rate(key):
        v = groups.get(key)
        return sum(v) / len(v) if v else None

    out = defaultdict(dict)
    for fam, cond, _ in set(groups):
        p, e = rate((fam, cond, "people")), rate((fam, cond, "equipment"))
        if p is not None and e is not None:
            out[fam][cond] = round(p - e, 2)
    return dict(out)


def headline(rs: list[dict]):
    grp = defaultdict(list)
    for r in rs:
        grp[(r["family"], r["twin"])].append(r)
    print(f"{'family':12} {'twin':10} {'n':>3} {'risky':>6} {'expos':>6} {'noticed':>8} {'escal':>6} {'harm(reply)':>12} {'harm(notes)':>12}")
    for (fam, twin), g in sorted(grp.items()):
        n = len(g)
        print(f"{fam:12} {twin:10} {n:3d} {sum(r['risky'] for r in g)/n:6.2f} {sum(r['exposed'] for r in g)/n:6.2f} "
              f"{sum(r['noticed'] for r in g)/n:8.2f} {sum(r['escalation'] for r in g)/n:6.2f} "
              f"{sum(r['naming_reply']=='harm' for r in g)/n:12.2f} "
              f"{sum(r['naming_notes']=='harm' for r in g)/n:12.2f}")


def transcripts(rs: list[dict], path: Path):
    with open(path, "w") as f:
        for r in sorted(rs, key=lambda r: (r["family"], r["twin"], r["condition"], r["epoch"])):
            f.write(f"## {r['family']} · {r['twin']} · {r['condition']} · epoch {r['epoch']}\n\n")
            f.write(f"decision {r['letter']} ({r['tag']}) · exposed {r['exposed']} · noticed {r['noticed']} · "
                    f"naming {r['naming_reply']}/{r['naming_notes']} · divergence {r['divergence']}\n\n")
            f.write("**reply**\n\n```\n" + r["reply"].strip() + "\n```\n\n")
            if r["notes"]:
                f.write("**notes**\n\n```\n" + r["notes"].strip() + "\n```\n\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    path = newest_log(LOG_DIR)
    print(path.name)
    rs = rows(read_eval_log(str(path)))
    headline(rs)
    print("\ntwin gap (people exposure - equipment exposure):")
    for fam, gaps in sorted(twin_gap(rs).items()):
        print(f"  {fam:12}", "  ".join(f"{c}={g:+.2f}" for c, g in sorted(gaps.items())))
    transcripts(rs, Path(__file__).parent / "transcripts.md")
