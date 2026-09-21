#!/usr/bin/env python3
"""Local glossary lookup. Stdlib only. No network. Reads bundled markdown only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "references" / "glossary.md"
LANGS = ("cn", "en", "ru", "es")
CJK_RE = re.compile(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
# Longest-first Russian adjective / noun endings. Stdlib only; no pymorphy.
RU_ENDINGS = (
    "ыми",
    "ими",
    "ого",
    "его",
    "ому",
    "ему",
    "ами",
    "ями",
    "ью",
    "ых",
    "их",
    "ые",
    "ие",
    "ая",
    "яя",
    "ую",
    "юю",
    "ое",
    "ее",
    "ый",
    "ий",
    "ой",
    "ей",
    "ом",
    "ем",
    "ов",
    "ев",
    "ам",
    "ям",
    "ах",
    "ях",
    "а",
    "я",
    "у",
    "ю",
    "е",
    "и",
    "о",
    "й",
    "ь",
)
RU_ENDING_RE = "(?:" + "|".join(RU_ENDINGS) + ")?"

# Refuse to follow paths outside the skill pack for the table itself.
if not GLOSSARY.is_file():
    sys.stderr.write("glossary.md missing next to this skill; reinstall the pack\n")
    sys.exit(2)


def _split_alts(s: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;/]", s) if p.strip()]


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
                "ru": (rec.get("ru") or "").strip(),
                "es": (rec.get("es") or "").strip(),
                "alt": (rec.get("alt") or "").strip(),
                "lock": (rec.get("lock") or "0").strip() == "1",
                "note": (rec.get("note") or "").strip(),
                "source": (rec.get("source") or "").strip(),
            }
        )
    return rows


def _surfaces(term: dict) -> list[tuple[str, str]]:
    """(surface, lang) pairs used for matching. Longest match is applied later."""
    out: list[tuple[str, str]] = []
    for lang in LANGS:
        val = (term.get(lang) or "").strip()
        if not val:
            continue
        out.append((val, lang))
        if lang == "en":
            core = re.sub(r"\s*\([^)]*\)", "", val).strip()
            if core and core != val:
                out.append((core, lang))
    for piece in _split_alts(term.get("alt") or ""):
        # Alt column is English (workbook / lock variants).
        out.append((piece, "en"))
        core = re.sub(r"\s*\([^)]*\)", "", piece).strip()
        if core and core != piece:
            out.append((core, "en"))
    # de-dupe keeping first lang tag
    seen = set()
    uniq = []
    for surface, lang in out:
        key = surface.casefold()
        if key in seen:
            continue
        seen.add(key)
        uniq.append((surface, lang))
    return uniq


def _is_cjk(s: str) -> bool:
    return bool(CJK_RE.search(s))


def _is_cyrillic(s: str) -> bool:
    return bool(CYRILLIC_RE.search(s))


def _fold_yo(s: str) -> str:
    return s.replace("ё", "е").replace("Ё", "Е")


def _ru_stem(word: str) -> str:
    w = _fold_yo(word).casefold()
    if w.endswith("ь") and len(w) > 4:
        return w[:-1]
    for end in RU_ENDINGS:
        if end and w.endswith(end) and len(w) - len(end) >= 3:
            return w[: -len(end)]
    return w


def _ru_pattern(surface: str) -> str:
    words = [w for w in _fold_yo(surface).split() if w]
    parts = [re.escape(_ru_stem(w)) + RU_ENDING_RE for w in words]
    body = r"\s+".join(parts)
    return r"(?<![\w-])" + body + r"(?![\w-])"


def _find_all(text: str, surface: str) -> list[tuple[int, int]]:
    """Return (start, end) spans in the original text."""
    if not surface:
        return []
    if _is_cjk(surface):
        hits = []
        start = 0
        while True:
            i = text.find(surface, start)
            if i < 0:
                break
            hits.append((i, i + len(surface)))
            start = i + len(surface)
        return hits
    if _is_cyrillic(surface):
        hay = _fold_yo(text)
        pat = _ru_pattern(surface)
        return [(m.start(), m.end()) for m in re.finditer(pat, hay, flags=re.IGNORECASE)]
    # Latin: case-insensitive, do not match inside a hyphenated token.
    pat = r"(?<![\w-])" + re.escape(surface) + r"(?![\w-])"
    return [(m.start(), m.end()) for m in re.finditer(pat, text, flags=re.IGNORECASE)]


def scan(text: str, terms: list[dict]) -> dict:
    # Same surface (e.g. Buchholz relay) can name more than one Chinese row.
    by_surface: dict[str, list[tuple[str, dict]]] = {}
    for term in terms:
        for surface, lang in _surfaces(term):
            by_surface.setdefault(surface, []).append((lang, term))
    ordered = sorted(by_surface.items(), key=lambda kv: len(kv[0]), reverse=True)

    occupied = [False] * len(text)
    hits = []
    for surface, owners in ordered:
        for i, end in _find_all(text, surface):
            if end > len(text) or i >= end:
                continue
            if any(occupied[i:end]):
                continue
            for j in range(i, end):
                occupied[j] = True
            seen_cn = set()
            for lang, term in owners:
                if term["cn"] in seen_cn:
                    continue
                seen_cn.add(term["cn"])
                hits.append(
                    {
                        "cn": term["cn"],
                        "en": term["en"],
                        "ru": term["ru"],
                        "es": term["es"],
                        "alt": term["alt"],
                        "lock": term["lock"],
                        "index": i,
                        "matched": text[i:end],
                        "matched_lang": lang,
                    }
                )
    hits.sort(key=lambda h: (h["index"], -len(h["cn"])))
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
            needles.extend(_split_alts(h["alt"]))
        ok = False
        for n in needles:
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


def _row_line(h: dict) -> str:
    flag = "LOCK" if h["lock"] else "term"
    ru = h.get("ru") or ""
    es = h.get("es") or ""
    extra = f"\t{ru}\t{es}" if (ru or es) else ""
    return f"{flag}\t{h['cn']}\t{h['en']}{extra}"


def main() -> None:
    p = argparse.ArgumentParser(description="Huaming OLTC glossary lookup")
    p.add_argument("--text", help="Source text (CN/EN/RU/ES or mixed). Use - for stdin.")
    p.add_argument("--en", help="Optional English translation to check against locks.")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.text is None:
        raw = sys.stdin.read()
    elif args.text == "-":
        raw = sys.stdin.read()
    else:
        raw = args.text
    if not (raw or "").strip():
        result = {"hits": [], "hit_count": 0, "unique_cn": [], "error": "empty input"}
        if args.json:
            json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return
        print("empty input")
        return
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
        print(_row_line(h))
    if args.en:
        for m in result.get("missing_locks") or []:
            print(f"MISSING\t{m['cn']}\t{m['expected']}")
        for b in result.get("banned") or []:
            print(f"BANNED\t{b}")


if __name__ == "__main__":
    main()
