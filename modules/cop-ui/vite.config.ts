import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { defineConfig, searchForWorkspaceRoot } from "vite";

const GATEWAY = "http://localhost:8000";
const outside = (rel: string) => fileURLToPath(new URL(rel, import.meta.url));

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/ws": { target: "ws://localhost:8000", ws: true },
      // contracts/API.md section 5 REST endpoints
      "^/(operation|plays|run|decisions|direct|injections)(/|\\?|$)": { target: GATEWAY },
    },
    // ?scene=s1..s6 reads contracts/examples and the editor's offline fallback reads demo/scenarios,
    // both outside this package.
    fs: { allow: [searchForWorkspaceRoot(process.cwd()), outside("../../contracts/examples"), outside("../../demo/scenarios")] },
  },
});
