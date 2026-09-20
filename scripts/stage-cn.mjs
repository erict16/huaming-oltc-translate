// Stage a skillhub.cn-compatible copy: no png, no scripts/, no tests/.
// skillhub.cn rejects png ("不允许的文件类型"). Icon lives in their web console.
import { cpSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

const out = mkdtempSync(path.join(os.tmpdir(), "skillhub-cn-"));
const dir = path.join(out, "huaming-oltc-translate");
cpSync(root, dir, {
  recursive: true,
  filter: (src) => {
    const rel = path.relative(root, src).replaceAll("\\", "/");
    if (!rel) return true;
    const top = rel.split("/")[0];
    if ([".git", "assets", "scripts", "tests", "node_modules"].includes(top)) {
      return false;
    }
    const base = path.basename(src);
    if ([".gitignore", ".gitattributes", "LICENSE"].includes(base)) return false;
    if (base.endsWith(".pyc") || base === "__pycache__") return false;
    if (base.endsWith(".tsv") || base.endsWith(".xlsx")) return false;
    return true;
  },
});
rmSync(path.join(dir, "assets"), { recursive: true, force: true });
rmSync(path.join(dir, "scripts"), { recursive: true, force: true });
rmSync(path.join(dir, "tests"), { recursive: true, force: true });

const skillPath = path.join(dir, "SKILL.md");
const text = readFileSync(skillPath, "utf8");
const version = text.match(/^version: (.+)$/m)?.[1]?.trim() ?? "";
for (const key of ["slug:", "displayName:", "summary:", "license:", "version:"]) {
  if (!text.includes(`\n${key} `) && !text.startsWith(key)) {
    throw new Error(`SKILL.md frontmatter missing ${key}`);
  }
}
if (!/^1\.\d+\.\d+/.test(version)) {
  throw new Error(`bad version: ${version}`);
}

console.log(`staged: ${dir}`);
console.log(`version: ${version}`);
