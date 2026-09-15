"""Turn the newest study log into two things a human can read:

  1. a headline table printed to the terminal (per condition: channel use,
     mean divergence, stance distribution, judge parse rate)
  2. transcripts.md: every sample with system prompt, user message, reply,
     notes, and the judges' reasoning, grouped by scenario so the three
     conditions sit next to each other.

Run:  python study/unmonitored/analysis.py [path/to/log.eval]
"""
import glob
import os
import sys
from collections import Counter
from pathlib import Path

from inspect_ai.log import read_eval_log

HERE = Path(__file__).resolve().parent
LOG_DIR = HERE.parents[1] / "logs" / "study"


def newest_log() -> str:
    logs = glob.glob(str(LOG_DIR / "*.eval"))
    if not logs:
        sys.exit(f"no logs in {LOG_DIR}")
    return max(logs, key=os.path.getmtime)


def rows(log) -> list[dict]:
    """One flat dict per sample. This is the samples_df idea by hand, so you
    can see what is in a log before trusting a dataframe helper."""
    out = []
    for s in log.samples:
        sc = s.scores or {}
        div = sc.get("divergence")
        st = sc.get("stance")
        ch = sc.get("channel")
        parts = (ch.metadata if ch else {}) or {}
        out.append(dict(
            id=s.id,
            epoch=s.epoch,
            scenario=s.metadata["scenario_id"],
            pressure=s.metadata["pressure"],
            condition=s.metadata["condition"],
            system=s.metadata["system"],
            user=s.input if isinstance(s.input, str) else s.input[-1].text,
            reply=parts.get("reply", s.output.completion),
            notes=parts.get("notes", ""),
            used_channel=bool(ch and ch.value == 1.0),
            divergence=div.value if div else None,
            divergence_reasoning=div.explanation if div else "",
            div_parsed=(div.metadata or {}).get("judge_parsed", True) if div else True,
            stance_user=(st.value or {}).get("user") if st else None,
            stance_monitor=(st.value or {}).get("monitor") if st else None,
            stance_reasoning=st.explanation if st else "",
        ))
    return out


def headline(rs: list[dict]) -> str:
    lines = []
    conds = ["none", "unmonitored", "monitored"]
    lines.append(f"{'condition':<12}{'n':>4}{'used ch.':>10}{'mean div':>10}{'parse ok':>10}  stance(user) / stance(monitor)")
    for c in conds:
        sub = [r for r in rs if r["condition"] == c]
        if not sub:
            continue
        n = len(sub)
        used = sum(r["used_channel"] for r in sub) / n
        judged = [r for r in sub if r["used_channel"]]
        mean_div = (sum(r["divergence"] for r in judged) / len(judged)) if judged else float("nan")
        parsed = sum(r["div_parsed"] for r in judged) / len(judged) if judged else float("nan")
        su = Counter(r["stance_user"] for r in judged)
        sm = Counter(r["stance_monitor"] for r in judged)
        fmt = lambda cnt: ", ".join(f"{k}={v}" for k, v in cnt.most_common()) or "-"
        lines.append(f"{c:<12}{n:>4}{used:>10.2f}{mean_div:>10.2f}{parsed:>10.2f}  {fmt(su)} / {fmt(sm)}")
    lines.append("")
    lines.append("by pressure (mean divergence, unmonitored vs monitored):")
    for p in sorted({r["pressure"] for r in rs}):
        cells = []
        for c in ("unmonitored", "monitored"):
            sub = [r["divergence"] for r in rs if r["pressure"] == p and r["condition"] == c and r["used_channel"]]
            cells.append(f"{sum(sub)/len(sub):.2f}" if sub else "  -  ")
        lines.append(f"  {p:<16}{cells[0]:>6}{cells[1]:>8}")
    return "\n".join(lines)


def transcripts(rs: list[dict], path: Path) -> None:
    by_scn = {}
    for r in rs:
        by_scn.setdefault(r["scenario"], []).append(r)
    md = ["# Transcripts\n", "Grouped by scenario. Read the three conditions of one scenario together.\n"]
    for scn, group in sorted(by_scn.items()):
        g0 = group[0]
        md.append(f"\n## {scn}  ({g0['pressure']})\n")
        md.append(f"**User:** {g0['user'].strip()}\n")
        for r in sorted(group, key=lambda r: (["none", "unmonitored", "monitored"].index(r["condition"]), r["epoch"])):
            md.append(f"\n### {r['condition']}  (epoch {r['epoch']})\n")
            md.append(f"<details><summary>system prompt</summary>\n\n```\n{r['system'].strip()}\n```\n</details>\n")
            md.append(f"**Reply:**\n\n{r['reply'].strip()}\n")
            if r["notes"]:
                md.append(f"**Notes:**\n\n> {r['notes'].strip().replace(chr(10), chr(10) + '> ')}\n")
                md.append(f"**Divergence {r['divergence']}**, stance user=`{r['stance_user']}` monitor=`{r['stance_monitor']}`\n")
                md.append(f"<details><summary>judge reasoning</summary>\n\n{r['divergence_reasoning'].strip()}\n\n---\n\n{r['stance_reasoning'].strip()}\n</details>\n")
            else:
                md.append("*(no notes channel)*\n")
    path.write_text("\n".join(md))


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else newest_log()
    log = read_eval_log(log_path)
    rs = rows(log)
    print(log_path, log.status, f"{len(rs)} samples\n")
    print(headline(rs))
    out = HERE / "transcripts.md"
    transcripts(rs, out)
    print(f"\nwrote {out}")
