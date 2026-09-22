#!/usr/bin/env python3
"""Build references/glossary.tsv from the Huaming 20260130 workbook.

Runtime translation does not need this script. Re-run only when the
company workbook changes. Output is UTF-8 TSV, no OneDrive paths inside.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "references" / "glossary.md"

SKIP_CN = {
    "其它：",
    "其他：",
    "一类开关是指Y接中性点，其余都是二类开关",
}

# Obvious OCR / typing errors in the workbook English.
EN_FIX = {
    "circuilating current": "circulating current",
    "chopped wave lightening impulse (LIC)": "chopped-wave lightning impulse (LIC)",
    "full wave lightening impulse test (LI)": "full-wave lightning impulse test (LI)",
    "imurity filter core": "impurity filter core",
    "DGA disolved gas analysis": "DGA (dissolved gas analysis)",
    "the temperature rise above the surrouding liquid": "temperature rise above the surrounding liquid",
    "Board type Tie-in -ressistor": "board-type tie-in resistor",
    "Tie-in -ressistor": "tie-in resistor",
    "Changer-over selector position": "change-over selector position",
    "output端0": "take-off terminal",
}

# Locks win over the workbook. source=os-lock.
LOCKS: list[tuple[str, str, str, str]] = [
    # cn, en, alt, note
    ("均压罩", "terminal screen caps", "", "Huaming OS field for CM/CMD/CM2/SHZV. Not corona caps, not 均压环."),
    ("屏蔽帽", "screen cap", "stress cap", "Do not use corona cap as the outward translation."),
    ("均压环", "grading ring", "corona ring", "Workbook has both; outward default is grading ring."),
    ("有载开关保护", "OLTC protective relay", "", "Not a generic protective device."),
    ("有载分接开关保护继电器", "OLTC protective relay", "OLTC protection relay", "Nameplate / OS field."),
    ("有载开关顶盖", "OLTC head cover", "", "Not diverter switch top cover."),
    ("头盖", "head cover", "", "OLTC head cover when the subject is the tap-changer."),
    ("顶盖", "top cover", "head cover", "If the subject is the OLTC, use OLTC head cover."),
    ("冷压管", "crimp sleeve", "", "Not crimped connector."),
    ("选择触头双数层", "even-numbered contact layer of the tap selector", "", ""),
    ("选择触头单数层", "odd-numbered contact layer of the tap selector", "", ""),
    ("气体继电器", "Buchholz relay", "gas relay", "Not protective relay. Protective relay is ZXJY / OLTC protective relay."),
    ("布赫霍尔茨继电器", "Buchholz relay", "", ""),
    ("保护继电器", "protective relay", "OLTC protective relay", "ZXJY-class device on the OLTC head."),
    ("薄弱环节", "shear pin", "weak link", ""),
    ("剪切销", "shear pin", "", ""),
    ("组合式", "combined", "combined OLTC", "Diverter switch + tap selector: CM, CM2, SHZV, SDZV, CMD."),
    ("复合式", "compound", "compound OLTC", "Selector switch: CV, CV2, SV. No selector grade letter."),
    ("笼式", "cage type", "cage", "WSL / WDL."),
    ("笼型", "cage type", "cage", ""),
    ("鼓式", "drum type", "drum", "WSG."),
    ("鼓型", "drum type", "drum", ""),
    ("无载分接开关", "off-circuit tap-changer", "de-energized tap-changer (DETC); OCTC", "Commercial English on Huaming OCTC papers: DE-ENERGIZED TAP CHANGER."),
    ("无励磁分接开关", "de-energized tap-changer", "off-circuit tap-changer (OCTC)", "Same family as 无载分接开关."),
    ("过渡电阻", "transition resistor", "transition resistors", "The parts. 过渡阻抗 stays transition impedance."),
    ("软连接", "flexible lead", "braided contact lead; braided leads", "Workbook lists both; OS/letters use flexible lead."),
    ("电动机构", "motor drive unit (MDU)", "drive unit", ""),
    ("外挂式", "compartment type", "on-tank", "On-tank / compartment-type OLTC."),
    ("内置式", "in-tank type", "in-tank", ""),
    ("正反调", "reversing", "reversing regulation (W)", ""),
    ("粗细调", "coarse-fine", "coarse-fine regulation (G)", ""),
    ("星点", "star-point", "neutral point; star point", "Switch application, not transformer Dyn11."),
    ("线端", "line-end", "line end", ""),
    ("切换开关芯子", "diverter switch insert", "", ""),
    ("真空灭弧室", "vacuum interrupter", "vacuum interrupter chamber", "Workbook 真空泡 = vacuum interrupter (VI)."),
    ("分接开关驱动装置", "motor drive unit (MDU)", "regulator drive", "Nameplate field."),
    ("垂直传动轴", "vertical driving shaft", "", ""),
    ("水平传动轴", "horizontal driving shaft", "", ""),
    ("传动轴", "driving shaft", "", "Workbook title-case Driving shaft."),
    ("变压器油箱", "transformer tank", "", "Do not match 变压器油 inside this span."),
    ("油箱", "tank", "transformer tank", "Prefer transformer tank when the source is 变压器油箱."),
    ("油室", "oil compartment", "", "Not the transformer tank."),
    ("切换开关", "diverter switch", "", "Not change-over switch."),
    ("分接选择器", "tap selector", "", "Not the whole tap-changer."),
    ("转换选择器", "change-over selector", "", "Not the diverter switch."),
    ("选择开关", "selector switch", "", "Compound OLTC (CV/CV2/SV). Not tap selector."),
    ("选择开关位置", "selector switch position", "", "Not change-over selector position."),
    ("上海华明电力设备制造有限公司", "Shanghai Huaming Power Equipment Co., Ltd.", "", ""),
    ("有载分接开关", "on-load tap-changer (OLTC)", "tap-changer", "Hyphen: tap-changer. Not switch."),
    ("压力释放阀", "pressure relief valve", "pressure relief device", "Huaming OI writes valve. MR writes pressure relief device."),
]

# RU/ES harvested from Huaming ESP/RU OIs and MR public OI/TD.
# Empty string = do not guess; the skill must ask.
# Huaming EN locks still win; these columns are for the other two languages.
I18N: dict[str, tuple[str, str]] = {
    # cn: (ru, es)
    "有载分接开关": ("устройство РПН", "cambiador de tomas bajo carga"),
    "无载分接开关": ("устройство ПБВ", "cambiador de tomas sin tensión"),
    "无励磁分接开关": ("устройство ПБВ", "cambiador de tomas sin tensión"),
    "切换开关": ("контактор", "ruptor"),
    "切换开关芯子": ("выемная часть контактора", "cuerpo insertable del ruptor"),
    "分接选择器": ("избиратель", "selector"),
    "转换选择器": ("предызбиратель", "preselector"),
    "选择开关": ("", ""),
    "油室": ("масляный бак контактора", "recipiente de aceite"),
    "变压器油箱": ("бак трансформатора", "cuba del transformador"),
    "电动机构": ("моторный привод", "accionamiento a motor"),
    "分接开关驱动装置": ("моторный привод", "accionamiento a motor"),
    "垂直传动轴": ("вертикальный приводной вал", "árbol de accionamiento vertical"),
    "水平传动轴": ("горизонтальный приводной вал", "árbol de accionamiento horizontal"),
    "传动轴": ("приводной вал", "árbol de accionamiento"),
    "保护继电器": ("защитное реле", "relé de protección"),
    "有载开关保护": ("защитное реле РПН", "relé de protección del cambiador de tomas"),
    "有载分接开关保护继电器": ("защитное реле РПН", "relé de protección del cambiador de tomas"),
    "气体继电器": ("реле Бухгольца", "relé Buchholz"),
    "布赫霍尔茨继电器": ("реле Бухгольца", "relé Buchholz"),
    "过渡电阻": ("переходный резистор", "resistencia de transición"),
    "真空灭弧室": ("вакуумная камера", "cámara de vacío"),
    "压力释放阀": ("клапан сброса давления", "válvula de alivio de presión"),
    "有载开关顶盖": ("крышка головки устройства РПН", "tapa de la cabeza del cambiador de tomas"),
    "头盖": ("крышка головки", "tapa de la cabeza"),
    "顶盖": ("крышка", "tapa"),
    "分接开关头部": ("головка устройства РПН", "cabeza del cambiador de tomas"),
    "伞齿轮盒": ("угловой редуктор", "reenvío angular"),
}


def norm_cn(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    s = s.replace("（", "(").replace("）", ")")
    return s.strip()


def norm_en(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = EN_FIX.get(s, s)
    # Title-case drawing labels stay as given; do not force case.
    if s == "输出端0take-off terminal" or s.lower().startswith("输出端"):
        return "take-off terminal"
    return s


def is_skip_cn(cn: str) -> bool:
    if not cn or cn in SKIP_CN:
        return True
    if cn.startswith("注：") or cn.startswith("注:"):
        return True
    if "一类开关" in cn:
        return True
    if len(cn) > 40 and ("。" in cn or "，" in cn):
        return True
    return False


def load_xlsx(path: Path) -> list[tuple[str, str, str, str]]:
    wb = load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [str(c).strip() if c else "" for c in rows[0]]
    # 20260130: 中文, 词性, 英文, 法文, 用法说明, 来源
    # semantic: 中文术语, 英文翻译, 备注
    cn_i = 0
    en_i = 2 if "英文" in "".join(header) and "翻译" not in header[1] else 1
    if header[0] in ("中文术语",) or (len(header) >= 2 and "英文翻译" in header[1]):
        en_i = 1
    pos_i = 1 if en_i == 2 else None
    note_i = 4 if len(header) > 4 else (2 if en_i == 1 and len(header) > 2 else None)
    out = []
    for row in rows[1:]:
        cn = row[cn_i] if row and cn_i < len(row) else None
        en = row[en_i] if row and en_i < len(row) else None
        if not cn or not en:
            continue
        cn_s = str(cn).replace("\n", " ").strip()
        en_s = str(en).replace("\n", " ").strip()
        if is_skip_cn(cn_s):
            continue
        pos = ""
        note = ""
        if pos_i is not None and pos_i < len(row) and row[pos_i]:
            pos = str(row[pos_i]).replace("\n", " ").strip()
        if note_i is not None and note_i < len(row) and row[note_i]:
            note = str(row[note_i]).replace("\n", " ").strip()
        out.append((cn_s, norm_en(en_s), pos, note))
    return out


def merge(workbooks: list[Path]) -> list[dict]:
    by_cn: dict[str, dict] = {}

    def put(cn: str, en: str, alt: str, pos: str, note: str, source: str, locked: bool) -> None:
        key = norm_cn(cn)
        if not key or not en:
            return
        ru, es = I18N.get(key, ("", ""))
        cur = by_cn.get(key)
        if cur is None:
            by_cn[key] = {
                "cn": cn,
                "en": en,
                "ru": ru,
                "es": es,
                "alt": alt,
                "pos": pos,
                "note": note,
                "source": source,
                "lock": "1" if locked else "0",
            }
            return
        if ru and not cur.get("ru"):
            cur["ru"] = ru
        if es and not cur.get("es"):
            cur["es"] = es
        if locked:
            # Locks replace workbook English. Do not keep workbook alts
            # (they include false friends such as corona cap / protective relay).
            cur["en"] = en
            cur["alt"] = alt
            cur["note"] = note or cur["note"]
            cur["source"] = source
            cur["lock"] = "1"
            return
        if cur["lock"] == "1":
            if en.lower() != cur["en"].lower() and en not in cur["alt"]:
                cur["alt"] = (cur["alt"] + "; " + en).strip("; ")
            return
        # Prefer a later more-specific English if current looks like a dump of options
        if en.lower() != cur["en"].lower():
            if en not in cur["alt"]:
                cur["alt"] = (cur["alt"] + "; " + en).strip("; ")

    if not workbooks:
        raise SystemExit("usage: python scripts/build_glossary.py <workbook.xlsx> [semantic.xlsx]")
    for i, xlsx in enumerate(workbooks):
        if not xlsx.is_file():
            raise SystemExit(f"workbook not found: {xlsx}")
        tag = "glossary-20260130" if i == 0 else "semantic-glossary"
        print(f"source workbook: {xlsx.name} ({tag})", file=sys.stderr)
        for cn, en, pos, note in load_xlsx(xlsx):
            put(cn, en, "", pos, note, tag, False)

    for cn, en, alt, note in LOCKS:
        put(cn, en, alt, "", note, "os-lock", True)

    for cn, (ru, es) in I18N.items():
        key = norm_cn(cn)
        cur = by_cn.get(key)
        if cur is None:
            continue
        if ru:
            cur["ru"] = ru
        if es:
            cur["es"] = es

    rows = list(by_cn.values())
    rows.sort(key=lambda r: (-len(norm_cn(r["cn"])), r["cn"]))
    return rows


def main() -> None:
    rows = merge([Path(a) for a in sys.argv[1:]])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    def esc(s: str) -> str:
        return (s or "").replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Huaming OLTC glossary",
        "",
        "Source: Huaming switch terminology workbook (2026-01-30) plus OS locks.",
        "RU/ES: Huaming ESP/RU operating instructions and Maschinenfabrik Reinhausen public OI/TD.",
        "Lock=1 wins over the model. Empty ru/es means ask, do not guess.",
        "Huaming English locks win over MR English.",
        "",
        "| cn | en | ru | es | alt | lock | note |",
        "|----|----|----|----|-----|------|------|",
    ]
    for r in rows:
        lines.append(
            "| {cn} | {en} | {ru} | {es} | {alt} | {lock} | {note} |".format(
                cn=esc(r["cn"]),
                en=esc(r["en"]),
                ru=esc(r.get("ru") or ""),
                es=esc(r.get("es") or ""),
                alt=esc(r["alt"]),
                lock=esc(r["lock"]),
                note=esc(r["note"]),
            )
        )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    locked = sum(1 for r in rows if r["lock"] == "1")
    filled = sum(1 for r in rows if r.get("ru") or r.get("es"))
    print(f"wrote {len(rows)} terms ({locked} locks, {filled} with ru/es) -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
