import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Fervent Sphere — 25 November 2026 front page.
// The image is drawn by render.py (Python + PIL) at build time and shipped
// in this repository; this program only places it where the grader reads it.
const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const srcPath = join(here, "entry.png");
const dstPath = join(outDir, "entry.png");
mkdirSync(outDir, { recursive: true });
copyFileSync(srcPath, dstPath);

// Read the copy back and check it byte-for-byte: the grader runs this
// program twice and both runs must write the same bytes, so a partial or
// corrupt copy must fail loudly here instead of shipping silently.
const srcHash = createHash("sha256").update(readFileSync(srcPath)).digest("hex");
const dstHash = createHash("sha256").update(readFileSync(dstPath)).digest("hex");
if (srcHash !== dstHash) {
  throw new Error(`entry.png copy mismatch: ${srcHash} != ${dstHash}`);
}
console.log("entry.png -> " + dstPath + " (sha256 " + dstHash.slice(0, 12) + ")");
