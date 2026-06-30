# AI agents

Design material for the AI agents that operate inside Francis (Claude via the Messages API). This folder is **internal design reference**, not part of the published Mintlify docs site — files here are not in `docs.json` navigation and won't render on the docs website.

## Contents

- **`francis-agent-taxonomy.html`** — the capability tool taxonomy for Francis agents. A standalone HTML page (open it directly in a browser). It covers:
  - The seven design principles the taxonomy follows.
  - A reference exhibit: a representative large-client model structure.
  - The 18 tools across 5 families (Retrieval, Analytical & diagnostic engine, Suggestion authoring, Direct edits, Collaboration), each tagged read/suggest/write, engine/LLM, bounded, and active/planned.
  - Each of the 20 user prompts mapped to the tool calls it fires.
  - Gaps (net-new capabilities), the structural pending-state engineering requirement, the git-model review loop, and a closing **Design considerations** section recording the rationale behind the choices.

## How it was built and how to update it

The page was authored as a Claude artifact and published to claude.ai. The copy here is the durable, browser-openable snapshot. It is the source of truth for the design as of this snapshot.

It is **not** a Mintlify `.mdx` page, and its descriptions are written for humans — the runtime tool schemas the agent actually reads are a separate, derived artifact (see the doc's "This is a design reference" consideration).
