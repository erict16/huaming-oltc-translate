# 华明翻译助手

Huaming Translation Assistant

把华明有载、无载分接开关的说明书、技术函、图注和订货规范，在中文、英文、俄文、西语之间互译。用词跟对照表走，句子写成工程师说明书那样，不写宣传腔。交 Word 就按华明说明书的版式：页眉、勾选框、数据用真表。表里没有的词先问，不猜。不管选型，不出价格。

## 安装

放到当前助手的 skills 目录，例如 Grok：

```
git clone https://github.com/erict16/huaming-oltc-translate.git ~/.grok/skills/huaming-oltc-translate
```

对助手说「把这段说明书译成英文 / 俄文 / 西语」即可。有 Python 3.10+ 时可以本地查词：

```
python scripts/lookup.py --text "检查油室里的切换开关芯子"
python scripts/lookup.py --text "diverter switch insert"
python scripts/lookup.py --text "выемная часть контактора"
python tests/test_lookup.py
```

查词只读本包 `references/glossary.md`，不联网。

## 词表

- 中英主源：华明《开关专业术语中英对照表》（2026-01-30）和华明说明书
- 俄文、西语：华明俄文 / 西语说明书，以及 Reinhausen 公开说明书里的通用词
- 华明对外英文以锁死项为准，不用别家英文去改华明 OS
- 锁死项：`references/locks.md`
- 全文：`references/glossary.md`（ru / es 空着的表示还没有出处）
- Word 交稿：`references/word-layout.md`

## 发布形态

只发 **skillhub.cn**（`node scripts/stage-cn.mjs` 去掉 png、LICENSE、scripts、tests）。不要发讯飞 SkillHub。Grok 用本仓库根目录即可。CLI 发完后网页后台把分类改回「行业专业」、图标改回 HM。

版本号以 `SKILL.md` 的 `version` 为准，须与 `manifest.yaml` 相同。
