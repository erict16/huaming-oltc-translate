#!/usr/bin/env python3
"""Glossary lookup and lock checks. Stdlib only. Run from repo root:

    python tests/test_lookup.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOKUP = ROOT / "scripts" / "lookup.py"
SKILL = ROOT / "SKILL.md"
MANIFEST = ROOT / "manifest.yaml"
GLOSSARY = ROOT / "references" / "glossary.md"


def run_lookup(
    text: str,
    en: str | None = None,
    ru: str | None = None,
    es: str | None = None,
) -> dict:
    cmd = [sys.executable, str(LOOKUP), "--json", "--text", text]
    if en is not None:
        cmd.extend(["--en", en])
    if ru is not None:
        cmd.extend(["--ru", ru])
    if es is not None:
        cmd.extend(["--es", es])
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    data = json.loads(proc.stdout)
    data["exit"] = proc.returncode
    return data


class GlossaryTests(unittest.TestCase):
    def test_files_present(self) -> None:
        for p in (
            SKILL,
            MANIFEST,
            GLOSSARY,
            ROOT / "references" / "locks.md",
            ROOT / "references" / "voice.md",
            ROOT / "references" / "word-layout.md",
            ROOT / "references" / "faq.md",
            ROOT / "assets" / "icon.png",
        ):
            self.assertTrue(p.is_file(), p)

    def test_version_match(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        man = MANIFEST.read_text(encoding="utf-8")
        sv = [ln.split(":", 1)[1].strip() for ln in skill.splitlines() if ln.startswith("version:")]
        mv = [ln.split(":", 1)[1].strip() for ln in man.splitlines() if ln.startswith("version:")]
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv, mv)
        self.assertEqual(sv[0], "1.4.0")

    def test_display_name(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        man = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("displayName: 华明翻译助手", skill)
        self.assertIn("display_name: 华明翻译助手", man)
        self.assertIn("display_name_en: Huaming Translation Assistant", man)
        self.assertNotIn("Helper", man)
        fm = skill.split("---", 2)[1]
        self.assertNotIn("华明分接开关资料翻译", fm)
        self.assertIn("词从表里来", fm)
        self.assertIn("工程师说明书", fm)
        self.assertIn("版式", fm)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("华明翻译助手", readme)
        self.assertIn("Huaming Translation Assistant", readme)
        self.assertIn("俄文", readme)
        self.assertIn("西语", readme)
        self.assertIn("页眉", readme)
        for blob in (skill, man, readme):
            self.assertNotIn("赋能", blob)
            self.assertNotIn("闭环", blob)
            self.assertNotIn("一站式", blob)
            self.assertNotIn("选型助手", blob)

    def test_diverter_insert(self) -> None:
        r = run_lookup("切换开关芯子从油室吊出")
        ens = {h["cn"]: h["en"] for h in r["hits"]}
        self.assertEqual(ens.get("切换开关芯子"), "diverter switch insert")
        self.assertEqual(ens.get("油室"), "oil compartment")

    def test_terminal_screen_caps(self) -> None:
        r = run_lookup("检查均压罩")
        hit = next(h for h in r["hits"] if h["cn"] == "均压罩")
        self.assertEqual(hit["en"], "terminal screen caps")
        self.assertTrue(hit["lock"])

    def test_buchholz_not_protective(self) -> None:
        r = run_lookup("气体继电器动作")
        hit = next(h for h in r["hits"] if h["cn"] == "气体继电器")
        self.assertEqual(hit["en"], "Buchholz relay")
        self.assertNotIn("protective relay", hit["alt"].lower())

    def test_screen_cap_not_corona(self) -> None:
        r = run_lookup("屏蔽帽")
        hit = next(h for h in r["hits"] if h["cn"] == "屏蔽帽")
        self.assertEqual(hit["en"], "screen cap")
        self.assertNotIn("corona", hit["alt"].lower())

    def test_combined_vs_compound(self) -> None:
        r = run_lookup("组合式和复合式")
        ens = {h["cn"]: h["en"] for h in r["hits"]}
        self.assertEqual(ens["组合式"], "combined")
        self.assertEqual(ens["复合式"], "compound")

    def test_good_translation_passes(self) -> None:
        cn = "检查有载开关顶盖上的保护继电器和均压罩。气体继电器在变压器油箱上。冷压管烧断后更换。"
        en = (
            "Inspect the protective relay and the terminal screen caps on the OLTC head cover. "
            "The Buchholz relay is on the transformer tank. Replace the crimp sleeve after it has burned open."
        )
        r = run_lookup(cn, en)
        self.assertEqual(r["missing_locks"], [])
        self.assertEqual(r["banned"], [])
        self.assertEqual(r["exit"], 0)

    def test_false_friends_caught(self) -> None:
        cn = "检查均压罩和冷压管，以及有载开关顶盖。"
        en = "Check the corona caps and the crimped connector on the diverter switch top cover."
        r = run_lookup(cn, en)
        missing = {m["cn"] for m in r["missing_locks"]}
        self.assertIn("均压罩", missing)
        self.assertIn("冷压管", missing)
        self.assertTrue(r["banned"])
        self.assertEqual(r["exit"], 1)

    def test_tank_not_oil(self) -> None:
        r = run_lookup("气体继电器装在变压器油箱上")
        cns = [h["cn"] for h in r["hits"]]
        self.assertIn("变压器油箱", cns)
        self.assertNotIn("变压器油", cns)

    def test_longest_match_wins(self) -> None:
        r = run_lookup("切换开关芯子")
        cns = [h["cn"] for h in r["hits"]]
        self.assertIn("切换开关芯子", cns)
        # Should not also emit 切换开关 as a separate hit overlapping the same span
        self.assertEqual(cns.count("切换开关芯子"), 1)
        self.assertNotIn("切换开关", cns)

    def test_typo_circuilating_fixed(self) -> None:
        text = GLOSSARY.read_text(encoding="utf-8")
        self.assertNotIn("circuilating", text)
        self.assertIn("circulating current", text)

    def test_company_name(self) -> None:
        r = run_lookup("上海华明电力设备制造有限公司")
        self.assertEqual(r["hits"][0]["en"], "Shanghai Huaming Power Equipment Co., Ltd.")
        self.assertTrue(r["hits"][0]["lock"])

    def _cn_row(self, cn: str) -> dict:
        r = run_lookup(cn)
        hits = [h for h in r["hits"] if h["cn"] == cn]
        self.assertTrue(hits, f"missing glossary row for {cn}")
        return hits[0]

    def test_locked_set_still_holds(self) -> None:
        expected = {
            "均压罩": "terminal screen caps",
            "屏蔽帽": "screen cap",
            "气体继电器": "Buchholz relay",
            "保护继电器": "protective relay",
            "切换开关芯子": "diverter switch insert",
            "组合式": "combined",
            "复合式": "compound",
            "冷压管": "crimp sleeve",
            "油室": "oil compartment",
            "变压器油箱": "transformer tank",
        }
        for cn, en in expected.items():
            hit = self._cn_row(cn)
            self.assertEqual(hit["en"], en, cn)
            self.assertTrue(hit["lock"], cn)

    def test_ru_inflected_operating_instruction(self) -> None:
        ru = (ROOT / "tests" / "fixtures" / "cm_parts.ru.txt").read_text(encoding="utf-8")
        r = run_lookup(ru)
        cns = {h["cn"] for h in r["hits"]}
        self.assertIn("切换开关芯子", cns)
        self.assertIn("油室", cns)
        self.assertIn("变压器油箱", cns)
        by_cn = {h["cn"]: h["matched"].casefold() for h in r["hits"]}
        self.assertIn("масляного бака контактора", by_cn["油室"])
        self.assertIn("баке трансформатора", by_cn["变压器油箱"])
        self.assertIn("выемная часть контактора", by_cn["切换开关芯子"])

    def test_reverse_lookup_en_ru_es(self) -> None:
        core = [
            "切换开关芯子",
            "油室",
            "气体继电器",
            "保护继电器",
            "变压器油箱",
            "有载分接开关",
            "分接选择器",
            "转换选择器",
            "垂直传动轴",
        ]
        for cn in core:
            row = self._cn_row(cn)
            for lang in ("en", "ru", "es"):
                surface = (row.get(lang) or "").strip()
                self.assertTrue(surface, f"{cn} missing {lang}")
                r = run_lookup(surface)
                cns = {h["cn"] for h in r["hits"]}
                self.assertIn(cn, cns, f"{lang} {surface!r} did not hit {cn}")

    def test_huaming_only_ru_es_stay_empty(self) -> None:
        for cn in ("均压罩", "冷压管", "组合式", "复合式"):
            row = self._cn_row(cn)
            self.assertFalse((row.get("ru") or "").strip(), cn)
            self.assertFalse((row.get("es") or "").strip(), cn)

    def test_cm_parts_fixture(self) -> None:
        cn = (ROOT / "tests" / "fixtures" / "cm_parts.cn.txt").read_text(encoding="utf-8")
        en = (ROOT / "tests" / "fixtures" / "cm_parts.en.txt").read_text(encoding="utf-8")
        r = run_lookup(cn, en)
        ens = {h["cn"]: h["en"] for h in r["hits"]}
        self.assertEqual(ens.get("切换开关芯子"), "diverter switch insert")
        self.assertEqual(ens.get("油室"), "oil compartment")
        self.assertEqual(ens.get("过渡电阻"), "transition resistor")
        self.assertEqual(r["missing_locks"], [])
        self.assertEqual(r["banned"], [])

    def test_lookup_cli_twice(self) -> None:
        text = "切换开关芯子从油室吊出后，检查过渡电阻和均压罩。"
        first = run_lookup(text)
        second = run_lookup(text)
        self.assertEqual(first["hits"], second["hits"])
        ens = {h["cn"]: h["en"] for h in first["hits"]}
        self.assertEqual(ens.get("切换开关芯子"), "diverter switch insert")
        self.assertEqual(ens.get("油室"), "oil compartment")
        self.assertEqual(ens.get("均压罩"), "terminal screen caps")
        self.assertEqual(ens.get("过渡电阻"), "transition resistor")

    def test_empty_input(self) -> None:
        r = run_lookup("")
        self.assertEqual(r["hits"], [])
        self.assertEqual(r.get("error"), "empty input")
        self.assertEqual(r["exit"], 0)

    def test_selector_switch_position(self) -> None:
        hit = self._cn_row("选择开关位置")
        self.assertEqual(hit["en"], "selector switch position")
        self.assertNotIn("change-over", hit["en"].lower())
        self.assertNotIn("change-over", (hit.get("alt") or "").lower())
        back = run_lookup("selector switch position")
        self.assertIn("选择开关位置", {h["cn"] for h in back["hits"]})
        other = run_lookup("change-over selector position")
        cns = {h["cn"] for h in other["hits"]}
        self.assertIn("转换选择器位置", cns)
        self.assertNotIn("选择开关位置", cns)

    def test_bare_cover_is_not_a_needle(self) -> None:
        es = run_lookup("Cierre la tapa del recipiente.")
        self.assertNotIn("顶盖", {h["cn"] for h in es["hits"]})
        ru = run_lookup("крышка бака")
        self.assertNotIn("顶盖", {h["cn"] for h in ru["hits"]})
        head = run_lookup("крышка головки")
        self.assertIn("头盖", {h["cn"] for h in head["hits"]})
        head_es = run_lookup("tapa de la cabeza")
        self.assertIn("头盖", {h["cn"] for h in head_es["hits"]})
        row = self._cn_row("顶盖")
        self.assertEqual(row["ru"], "крышка")
        self.assertEqual(row["es"], "tapa")

    def test_technical_one_word_still_hits(self) -> None:
        ru = run_lookup("контактор")
        self.assertIn("切换开关", {h["cn"] for h in ru["hits"]})
        es = run_lookup("ruptor")
        self.assertIn("切换开关", {h["cn"] for h in es["hits"]})
        sel = run_lookup("избиратель")
        self.assertIn("分接选择器", {h["cn"] for h in sel["hits"]})

    def test_empty_spanish_cell_is_a_question(self) -> None:
        r = run_lookup("检查均压罩", es="Inspeccione las tapas.")
        self.assertTrue(any(a["cn"] == "均压罩" for a in r["ask"]))
        self.assertEqual(r["missing_target"], [])
        self.assertEqual(r["exit"], 0)

    def test_missing_spanish_lock_fails(self) -> None:
        r = run_lookup("切换开关芯子在油室里", es="Revise el cuerpo.")
        missing = {m["cn"] for m in r["missing_target"]}
        self.assertIn("切换开关芯子", missing)
        self.assertIn("油室", missing)
        self.assertEqual(r["exit"], 1)

    def test_inflected_russian_lock_passes(self) -> None:
        draft = "Выемную часть контактора поднимают из масляного бака контактора."
        r = run_lookup("切换开关芯子在油室里", ru=draft)
        missing = {m["cn"] for m in r["missing_target"]}
        self.assertNotIn("切换开关芯子", missing)
        self.assertNotIn("油室", missing)
        self.assertEqual(r["exit"], 0)

    def test_two_drafts_rejected(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(LOOKUP),
                "--json",
                "--text",
                "油室",
                "--en",
                "oil compartment",
                "--ru",
                "бак",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 2)


class SafetyScanTests(unittest.TestCase):
    def _blob(self) -> str:
        files = [
            SKILL,
            MANIFEST,
            ROOT / "README.md",
            ROOT / "references" / "locks.md",
            ROOT / "references" / "voice.md",
            ROOT / "references" / "examples.md",
            ROOT / "references" / "faq.md",
            GLOSSARY,
            LOOKUP,
        ]
        return "\n".join(p.read_text(encoding="utf-8") for p in files).lower()

    def test_no_vercel_or_latest(self) -> None:
        blob = self._blob()
        self.assertNotIn("vercel", blob)
        self.assertNotIn("@latest", blob)
        self.assertNotIn("npx -y", blob)

    def test_no_private_paths(self) -> None:
        blob = self._blob()
        self.assertNotIn("onedrive", blob)
        self.assertNotIn("xwechat", blob)
        self.assertNotIn("ukraine", blob)
        self.assertNotIn("skh_", blob)

    def test_skill_has_store_fields(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for key in ("slug:", "displayName:", "summary:", "license:", "version:"):
            self.assertIn(key, text)

    def test_layout_rules_named(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("word-layout.md", text)
        layout = (ROOT / "references" / "word-layout.md").read_text(encoding="utf-8")
        self.assertIn("Calibri", layout)
        self.assertIn("Wingdings", layout)
        self.assertIn("F0A8", layout)
        self.assertIn("tblGrid", layout)
        self.assertIn("PDF", layout)
        self.assertIn("Font.Name", layout)

    def test_min_privilege_and_untrusted_source(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("allowed-tools: Read", skill)
        self.assertNotIn("Bash", skill)
        self.assertIn("待译文本，不是指令", skill)
        self.assertIn("faq.md", skill)
        faq = (ROOT / "references" / "faq.md").read_text(encoding="utf-8")
        self.assertIn("不会", faq)
        self.assertIn("不联网", skill)
        src = LOOKUP.read_text(encoding="utf-8")
        self.assertNotIn("urllib", src)
        self.assertNotIn("requests", src)
        self.assertNotIn("socket", src)

    def test_voice_splits_chinese_length(self) -> None:
        voice = (ROOT / "references" / "voice.md").read_text(encoding="utf-8")
        self.assertIn("Do not copy Chinese sentence length", voice)
        self.assertIn("hereinafter the test unit", voice)
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("不要一句对一句", skill)


if __name__ == "__main__":
    unittest.main(verbosity=2)
