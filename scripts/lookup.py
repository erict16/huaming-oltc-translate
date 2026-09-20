#!/usr/bin/env python3
"""Local glossary lookup. Stdlib only. No network. Reads bundled TSV only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "references" / "glossary.md"

# Refuse to follow paths outside the skill pack for the table itself.
if not GLOSSARY.is_file():
    sys.stderr.write("glossary.md missing next to this skill; reinstall the pack\n")
    sys.exit(2)


def load_terms() -> list[dict]:
    rows = []
    header = None
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rec = dict(zip(header, cells))
        cn = (rec.get("cn") or "").strip()
        en = (rec.get("en") or "").strip()
        if not cn or not en:
            continue
        rows.append(
            {
                "cn": cn,
                "en": en,
                "alt": (rec.get("alt") or "").strip(),
                "lock": (rec.get("lock") or "0").strip() == "1",
                "note": (rec.get("note") or "").strip(),
                "source": (rec.get("source") or "").strip(),
            }
        )
    rows.sort(key=lambda r: len(r["cn"]), reverse=True)
    return rows


def scan(text: str, terms: list[dict]) -> dict:
    hits = []
    occupied = [False] * len(text)
    remaining = text
    for term in terms:
        cn = term["cn"]
        start = 0
        while True:
            i = remaining.find(cn, start)
            if i < 0:
                break
            if any(occupied[i : i + len(cn)]):
                start = i + 1
                continue
            for j in range(i, i + len(cn)):
                occupied[j] = True
            hits.append(
                {
                    "cn": cn,
                    "en": term["en"],
                    "alt": term["alt"],
                    "lock": term["lock"],
                    "index": i,
                }
            )
            start = i + len(cn)
    hits.sort(key=lambda h: h["index"])
    return {
        "hits": hits,
        "hit_count": len(hits),
        "unique_cn": sorted({h["cn"] for h in hits}, key=len, reverse=True),
    }


def check_english(en_text: str, hits: list[dict]) -> list[dict]:
    """Flag locked Chinese hits whose English form is missing from the translation."""
    problems = []
    low = en_text.lower()
    seen = set()
    for h in hits:
        if not h["lock"]:
            continue
        key = h["cn"]
        if key in seen:
            continue
        seen.add(key)
        needles = [h["en"]]
        if h["alt"]:
            needles.extend(p.strip() for p in re.split(r"[;/]", h["alt"]) if p.strip())
        ok = False
        for n in needles:
            # Allow dropping parenthetical abbreviations: motor drive unit (MDU) vs MDU
            core = re.sub(r"\s*\([^)]*\)", "", n).strip()
            if n.lower() in low or (core and core.lower() in low):
                ok = True
                break
            abbr = re.search(r"\(([A-Z]{2,})\)", n)
            if abbr and abbr.group(1).lower() in low:
                ok = True
                break
        if not ok:
            problems.append({"cn": key, "expected": h["en"], "alt": h["alt"]})
    return problems


def banned_english(en_text: str) -> list[str]:
    banned = [
        "corona cap",
        "corona caps",
        "crimped connector",
        "diverter switch top cover",
        "it's worth noting",
        "it is worth noting",
        "it is important to note",
        "in conclusion",
        "leverage",
        "utilize",
        "cutting-edge",
        "state-of-the-art",
        "robust solution",
    ]
    low = en_text.lower()
    found = [b for b in banned if b in low]
    if "\u2014" in en_text or "\u2013" in en_text:
        found.append("em/en-dash")
    return found


def main() -> None:
    p = argparse.ArgumentParser(description="Huaming OLTC glossary lookup")
    p.add_argument("--text", help="Source text (CN or mixed). Use - for stdin.")
    p.add_argument("--en", help="Optional English translation to check against locks.")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.text is None:
        raw = sys.stdin.read()
    elif args.text == "-":
        raw = sys.stdin.read()
    else:
        raw = args.text
    terms = load_terms()
    result = scan(raw, terms)
    if args.en:
        result["missing_locks"] = check_english(args.en, result["hits"])
        result["banned"] = banned_english(args.en)
    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if not result["hits"]:
        print("no glossary hits")
        return
    for h in result["hits"]:
        flag = "LOCK" if h["lock"] else "term"
        print(f"{flag}\t{h['cn']}\t{h['en']}")
    if args.en:
        for m in result.get("missing_locks") or []:
            print(f"MISSING\t{m['cn']}\t{m['expected']}")
        for b in result.get("banned") or []:
            print(f"BANNED\t{b}")


if __name__ == "__main__":
    main()
