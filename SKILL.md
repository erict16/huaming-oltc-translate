---
name: huaming-oltc-translate
slug: huaming-oltc-translate
displayName: 华明分接开关资料翻译
summary: 把华明有载/无载分接开关说明书、技术函、外形图注和订货规范译成对得上公司对照表的英文。词从表里来，句子按工程师说明书写。
license: MIT
description: >
  华明分接开关资料翻译：把华明说明书、技术函、外形图注、OS 字段译成与公司术语对照表一致的英文（也可英译中）。
  触发：翻译说明书、技术函英译、OS 英文、分接开关翻译、OLTC translation、tap-changer English、
  华明英文、对照表、diverter switch、tap selector、change-over selector、均压罩、油室、电动机构。
  不触发：选型、跑 oltc、报价、价格、发邮件、报关单据、低压开关柜。
allowed-tools: Read, Bash
version: 1.1.1
---

# 华明分接开关资料翻译

把华明有载 / 无载分接开关的说明书、技术函、外形图注和订货规范译成英文。用词跟公司《开关专业术语中英对照表》走，句子按工程师说明书写，不写宣传腔。

输入：

> 组合式有载分接开关由切换开关、分接选择器和转换选择器组成。切换开关芯子从油室吊出后，检查过渡电阻和均压罩。

输出：

> The combined on-load tap-changer consists of a diverter switch, a tap selector and a change-over selector. After lifting the diverter switch insert out of the oil compartment, inspect the transition resistors and the terminal screen caps.

覆盖华明 OLTC / OCTC 及配套电动机构、保护继电器。不管选型、报价、低压断路器柜，也不用别家样本的词去改华明对外英文。

---

_以下是为 AI 助手准备的执行说明。_

## 必须遵守

1. 动手前读 `references/locks.md`。锁死项压过模型习惯译法。
2. 再读 `references/voice.md`、`references/examples.md` 和 `references/word-layout.md`。
3. 对照 `references/glossary.md`（中英对照，约 380 条）。有 Python 时在本 skill 目录跑 `python scripts/lookup.py --json --text "<中文>"`；没有脚本的安装包就直接读 glossary.md。禁止联网查词，禁止另装翻译包。
4. 表里没有的词：保留中文，用一句问用户，不要猜。IEC 条款、试验数值、时间（例如 80 ms）原文没有就不要补。
5. 全文同一中文只用一个英文。型号、图号、电流、弯管字母 R/S/Q/E1/E2/W 原样保留。
6. 英文禁止破折号（U+2014 / U+2013）。禁止 corona caps、crimped connector、diverter switch top cover 这类锁死反例。
7. 不跑选型、不出价格、不发邮件、不改用户磁盘上的原件，除非用户点名要写某个文件。
8. 译完用 lookup 的 `--en` 自检；缺锁死词或命中禁词就改，不要交出去。
9. 交 Word / PDF 前按 `references/word-layout.md` 做完：页眉两格表（公司名不溢出）、勾选格两行 `□ Yes` / `□ No`、正文 Calibri 10.5 pt，图里的中文表要重画。首页页眉不得压标题行。页面上还能看见中文就还没完。

## 怎么译

1. 看清方向：默认中 → 英。用户要英 → 中时用同一张表反过来查。
2. 看清文体：步骤用祈使句；原理用陈述句；图注和表单元格保持短，不要扩成段落。
3. 先扫术语，再写句子。长词优先（「切换开关芯子」整段吃掉，不要拆成「切换」+「开关」+「芯子」）。
4. 组合式 / 复合式 / 笼式 / 鼓式 按 locks 译成 combined / compound / cage type / drum type。不要把复合式写成 combined。
5. 气体继电器是 Buchholz relay，保护继电器是 protective relay，两套东西。
6. 无励磁 / 无载分接开关对外可以写 de-energized tap-changer 或 off-circuit tap-changer；商业文件标题常用 DE-ENERGIZED TAP CHANGER。不要写成 on-load。
7. 交稿只给译文。用户要对照表时再附「中文 → 英文」命中清单。不要写翻译过程小结。

## 不要做

- 用 Reinhausen / MR 词表覆盖华明 OS（例如把华明的 pressure relief valve 改成他们的习惯叫法，除非用户在译 MR 文件）。
- 把 Dyn11 当成星点接线。星点 / 线端是开关装在哪。
- 把均压罩译成 corona caps 或均压环。
- 补充原文没有的安全警告或免责声明。

## 自检

- [ ] locks.md 里出现过的中文，英文里都在
- [ ] 无 em-dash / en-dash
- [ ] 无 corona cap、crimped connector、diverter switch top cover
- [ ] 型号与数字未改
- [ ] 句子能单独读完，不是词对词堆砌
- [ ] 每个 media 图都看过：没有中文表、没有中文图注
- [ ] 页眉两格表，公司名+Test Centre 左、文号右；首页页眉不压标题行
- [ ] 勾选格两行居中 `□ Yes` / `□ No`（9 pt）；不是 `□ Yes  □` 下一行 `No`；Yes 没有变蓝下划线
- [ ] 正文拉丁字 Calibri 10.5 pt（sz 21），不是宋体、不是 Times
