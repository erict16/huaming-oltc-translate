# 华明分接开关资料翻译

把华明有载 / 无载分接开关的说明书、技术函、外形图注和订货规范译成英文。用词跟公司术语对照表走，句子按工程师说明书写。

不管选型，不出价格。

## 安装

放到当前助手的 skills 目录，例如 Grok：

```
git clone https://github.com/erict16/huaming-oltc-translate.git ~/.grok/skills/huaming-oltc-translate
```

对助手说「把这段说明书译成英文」即可。有 Python 3.10+ 时可以本地查词：

```
python scripts/lookup.py --text "检查油室里的切换开关芯子"
python tests/test_lookup.py
```

查词只读本包 `references/glossary.md`，不联网。

## 词表

- 主源：华明《开关专业术语中英对照表》（2026-01-30）
- 锁死项：`references/locks.md`（OS 字段和假朋友，压过表里的两可译法）
- 全文：`references/glossary.md`

## 发布形态

- 讯飞 SkillHub / Grok：本仓库根目录（可带 `assets/icon.png`）
- skillhub.cn：`node scripts/stage-cn.mjs` 去掉 png、LICENSE、scripts、tests（他们白名单拒这些），图标在网页后台传

版本号以 `SKILL.md` 的 `version` 为准，须与 `manifest.yaml` 相同。
