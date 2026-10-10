import type { OntologyView } from "../../contracts.gen";

type Fetch = (url: string) => Promise<Response>;

// GET /ontology (decision 0038). A failure carries the server's detail, e.g. an operation with no ontology
// says so in words instead of "404" (decision 0051).
export async function fetchOntology(f: Fetch = (url) => fetch(url)): Promise<OntologyView> {
  const r = await f("/ontology");
  if (!r.ok) {
    const body = await r.json().catch(() => ({}));
    throw new Error(body.detail ?? `/ontology answered ${r.status}`);
  }
  return (await r.json()) as OntologyView;
}
