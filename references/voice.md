# Voice: Huaming operating-instruction English

Write like the English CM / CM2 / SHZV operating instructions, not like a brochure and not like a chatbot.

## Who is speaking

A factory engineer explaining a tap-changer to another engineer. Short complete sentences. Imperative for steps. Indicative for facts.

## Do

- Keep the source structure: headings, numbered steps, figure captions, table cells.
- One action per sentence in procedures: "Drain the oil from the oil compartment." not "It is recommended that oil drainage be performed."
- Do not copy Chinese sentence length. A Chinese step often stacks several actions with commas. Split them in English. Keep the step number and the cell. Keep numbers, form codes, and locked terms.
- Keep numbers, units, type strings, and drawing codes exact.
- Use the same English term for the same Chinese term in the whole document.
- First mention of OLTC / MDU / DGA may keep the abbreviation in parentheses; after that use one form.

## Do not

- Em-dash (U+2014) or en-dash (U+2013). Use a comma, period, or hyphen-minus in compounds (`on-load`, `in-tank`).
- Throat-clearing: "It is important to note", "Please be aware that", "In conclusion".
- Marketing: "robust", "cutting-edge", "state-of-the-art", "leverage", "utilize", "comprehensive solution".
- Negative parallelism: "This is not X. It is Y."
- Invented labels: "the arcing paradox", "the selector trap".
- Emoji.
- Adding facts the source does not state (IEC clause numbers, test values, "usually 80 ms").
- Turning a Chinese 我/本公司 into English "you should" advice.
- Mapping one Chinese comma-chain onto one English sentence. If you cannot read a step aloud in one breath, split it.
- Legal stacking such as "hereinafter the test unit".

## Sentence models (from Huaming OI)

Source (CM OI):

> 在使用分接开关之前，请仔细阅读本手册，以备参考。

Target:

> Please read this manual carefully before using the tap-changer and save it for reference.

Source:

> 切换开关芯子从油室吊出后，检查过渡电阻和主通断触头。

Target:

> After lifting the diverter switch insert out of the oil compartment, inspect the transition resistors and the main switching contacts.

If the Chinese is a caption or table cell, keep it a caption or cell. Do not pad it into a paragraph. A stacked 步骤 cell is split in `examples.md` §4.
