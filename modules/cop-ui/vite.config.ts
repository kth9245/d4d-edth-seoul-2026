import react from "@vitejs/plugin-react";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, searchForWorkspaceRoot } from "vite";

const GATEWAY = process.env.KDTH_GATEWAY ?? "http://localhost:8000"; // a worktree can test against its own gateway
const outside = (rel: string) => fileURLToPath(new URL(rel, import.meta.url));

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/ws": { target: GATEWAY.replace(/^http/, "ws"), ws: true },
      // contracts/API.md section 5 REST endpoints
      "^/(operation|roles|vehicles|enemies|ontology|graph|mavlink|run|decisions|direct|injections|scenarios|routes|watch_points)(/|\\?|$)": { target: GATEWAY },
    },
    // ?scene=s1..s6 reads contracts/examples and the AI draft box reads demo/draft_sentences.json,
    // both outside this package. In a worktree node_modules links to the main checkout, so the bundled
    // font files live outside this package too.
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd()), outside("../../contracts/examples"),
        outside("../../demo/draft_sentences.json"),
        realpathSync(outside("./node_modules"))],
    },
  },
});
