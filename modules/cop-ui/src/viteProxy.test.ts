import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import config from "../vite.config";

// Every REST path in contracts/API.md section 5 must go through the dev server proxy to the gateway.
// A missing one answers with index.html in dev (npm run dev / scripts/dev.sh) and the page breaks on JSON parsing.
function contractPaths(): string[] {
  const md = readFileSync(new URL("../../../contracts/API.md", import.meta.url), "utf-8");
  const section = md.split(/^## 5\./m)[1].split(/^## /m)[0];
  const paths = [...section.matchAll(/`(?:GET|POST) (\/[^`?\s]*)/g)].map((m) => m[1].replace(/\{[^}]+\}/g, "x"));
  return [...new Set(paths)];
}

describe("vite dev proxy", () => {
  it("forwards every REST path of the contract to the gateway", () => {
    const keys = Object.keys(config.server?.proxy ?? {});
    const forwarded = (p: string) => keys.some((k) => (k.startsWith("^") ? new RegExp(k).test(p) : p.startsWith(k)));
    const paths = contractPaths();
    expect(paths).toContain("/enemies");
    expect(paths.filter((p) => !forwarded(p))).toEqual([]);
  });
});
