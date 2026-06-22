# Francis Documentation: Rules of Procedure

Authoring guidance for Francis docs. This file lives in the docs repo as the source of truth — when Claude Code is editing pages in this repo, this file is loaded automatically as standing context.

---

## Working with this repo

- **Keep shell commands simple and readable.** Use the Read tool for known files, and plain `grep` or `find` for targeted lookups. Never use Python to read or inspect files. Avoid complex Python or Bash one-liners that would be hard for a non-technical team member to read or understand. If you need to understand the navigation structure, read `docs.json` directly.

---

## Purpose of the docs

The documentation exists to **improve user activation and enable users to solve problems themselves**. It serves two audiences in one artifact: self-serve users onboarding independently, and FP&A Advisory referencing specific pages during white-glove onboarding. Design for the self-serve user; the white-glove case is served by good anchor links and progressive disclosure.

---

## Audience

Write for a **Head of Finance or CFO at a lower-mid-market company**.

Assumptions about the reader:

- Has a business or finance degree
- Owns multiple finance areas (FP&A, accounting, controlling, treasury, reporting), so depth in any one area may have faded
- Is fluent in Excel and accounting fundamentals
- Has seen many financial systems — recognizes patterns, is impatient with bloat
- Reads English at a professional working level
- Wants to get something done, not learn the field

What this means in practice:

- **Don't re-explain accounting basics.** Skip "VAT is a liability that affects cash flow" or "the balance sheet must balance." Assume it.
- **Do refresh on adjacent specialist topics.** A CFO might not have set up a multi-currency consolidation in years. Brief refreshers on the *concept* are fair when leading into how Francis handles it.
- **Lead with what's specific to Francis.** That's the value of the docs — the reader doesn't need a finance textbook, they need to know how to do this in Francis.

---

## Voice and tone

**Francis docs sound like a senior FP&A colleague briefing a peer.** Direct, technically fluent, no fluff. We assume the reader knows accounting and finance. We earn our keep by being specific about Francis, opinionated on tradeoffs, and honest about edge cases.

### Voice attributes

- **Confident, not promotional.** "Use SUMIFS for this." Not "you can leverage the powerful SUMIFS function."
- **Opinionated where it helps.** When there's a clearly better path, say so. *"Forecast VAT as a percentage of revenue unless your business has unusual VAT exposure — the precision rarely pays off."*
- **Concrete over abstract.** *"A €2M ARR SaaS business with monthly billing"* beats *"your revenue forecast."*
- **Respects the reader's time.** Cut sentences that don't earn their place. If a paragraph can be deleted without loss, delete it. This targets filler, hedging, and restated basics, not substance. On feature pages a fact an AI agent would need always earns its place (see *The editorial principle*) — completeness wins there, so don't invoke this to thin out behavioral detail.
- **Plain English over jargon-as-decoration.** *"The model rolls up monthly to annual"* beats *"the model aggregates with hierarchical roll-up logic."*

### Avoid

- **Explaining accounting basics.** The reader is a CFO or Head of Finance.
- **Marketing-speak.** No *powerful*, *robust*, *seamless*, *intuitive*, *streamline*, *empower*, *unlock*.
- **Fake friendliness.** No *"Great question!"* or *"Don't worry — Francis makes this easy!"*
- **Hedging.** *"You may want to consider potentially…"* → *"Do this."* If a recommendation is genuinely conditional, name the condition.
- **Filler intros.** *"In this section, we'll explore…"* — delete and start with the content.

---

## Writing conventions

- **Second person ("you"), present tense.** *"When you import actuals"*, not *"users will import actuals"* or *"after importing actuals."*
- **Average sentence under 25 words.** Short by default. Long sentences are fine when they earn it.
- **No em dashes (—).** They read as AI-generated and weaken the voice. The right replacement depends on what the dash is doing:
    - **Parenthetical aside** (`X — Y — Z`): wrap with commas or parentheses. *"The three approaches (driver-based, statistical, and hardcoded), and when to use each."*
    - **Pivot or punchline** (`X — Y`): use a period and a new sentence, or rewrite. *"That's fine. Hardcoded values get reporting running quickly."*
    - If a period leaves a dangling fragment ("…and when to use each."), recast the whole sentence rather than keeping the broken half.
- **Oxford commas.** Lists of three or more get a comma before the final item.
- **Sentence case for headings.** *Forecasting approaches*, not *Forecasting Approaches*.
- **Imperative mood for instructions.** *"Click Save"* — not *"You can click Save"* or *"The user clicks Save."*
- **One idea per paragraph.** When a paragraph carries two ideas, split it.
- **No first-person plural ("we") in concept and reference pages.** *"We recommend X"* weakens the recommendation. Just say *"Use X."* "We" is fine in masterclass intros where a guiding voice is appropriate.
- **Lists for parallel, discrete items. Prose for flow.** Don't bullet-point what's actually a paragraph.
- **Numbered lists for ordered steps. Bulleted lists for unordered options.** Don't number something that isn't sequential.

### Formatting

- **Bold** — UI elements (buttons, fields, menu items). Only at the start of a label or combined with a link. Do not bold mid-sentence for emphasis — use italic sparingly instead.
- *Italic* — in-sentence emphasis, used sparingly
- `Inline code` — formulas, function names, file paths, keyboard shortcuts
- Code block — multi-line formulas or anything that benefits from monospace

### First mention of Francis concepts

Hyperlink the first mention of a Francis concept on each page to its concept page. Subsequent mentions are plain lowercase. *"Build your model from [components](/features/components). Each component is a row, calculation, group, section, or sheet."*

This replaces a capitalization convention — the link does the disambiguation work, lowercase keeps the prose clean.

### Formula syntax

- **Function names are lowercase.** Francis function names use lowercase everywhere — in code blocks, inline code, and prose references. *`if`, `avg_last`, `predict`, `sum_ytd`* — never *`IF`, `AVG_LAST`, `PREDICT`*. The exception is when explicitly referencing a function name from another tool (e.g. *"similar to IF in Excel"*), where the source tool's capitalization is preserved.
- **Spaces around binary operators.** Put a single space on each side of binary operators (`+`, `-`, `*`, `/`, `=`) when they sit between operands, including comparison `=` inside function arguments. *`"Revenue"[0] = 0`* and *`"Marketing"[-12] * (1 + 10%)`* — never *`"Revenue"[0]=0`* or *`(1+10%)`*. No space inside slice notation (*`[-3:0]`*).
- **"Formula" is the umbrella term for what a user writes into a cell.** A hardcoded value is the simplest formula — a constant that evaluates to itself. So "write a formula" includes typing a plain value, and you don't need to write "write a formula or input a hardcoded number" every time. This covers cell edits only, not values imported into actuals periods from the accounting system (those aren't formulas). The equivalence is defined once on the [Formulas](/features-new/using-francis/formulas) page; rely on it elsewhere. Only distinguish the two when the difference is the point (e.g. overriding a calculation by pasting a literal over it), and use *hardcoded value* (not *hardcoded number*) as the canonical term.

---

## Information architecture

### Three top-level tabs

1. **Features** — the reference layer. Two sub-categories: *Admin* (workspace management, billing, members) and *Using Francis* (everything from Components to Comments — flat, alphabetical-ish ordering).
2. **Masterclasses** — use-case-driven teaching. Four masterclasses: Consolidation, Budgeting & forecasting, Reporting, Business partnering.
3. **Integrations** — connector setup, kept separate because setup is a distinct user intent from usage.

### On the "Masterclasses" name

Masterclasses is a deliberate brand choice, not just a content label. It ties the docs to the Francis narrative of **mastering finance** and echoes the Mastery plan tier, creating vocabulary consistency across pricing, product, and education.

**Rules for the name:**

- The section label is *Masterclasses*.
- Individual pages in the sidebar use the short noun (*Consolidation*), not *Consolidation Masterclass*.
- Individual page H1s are outcome-framed (*Consolidate multi-entity financials*) — the word *Masterclass* does not appear in H1s.
- The Masterclasses landing page uses the word explicitly and earns it with a short philosophy statement — these teach you to do the work of senior FP&A, not just click buttons.

---

## The editorial principle (non-negotiable)

**Features is the deep source. Masterclasses are orchestration.**

Feature behavior is explained once, in Features. Masterclasses link *into* feature pages rather than re-explaining primitives from scratch. Masterclasses read as playbooks (*"do this, then use [components] to link it up"*), not textbooks.

The duplication problem isn't caused by having feature docs — it's caused by depth living in multiple places. Single source of truth for each concept, with masterclasses as thin orchestration, is the resolution.

### Feature pages are written for the AI agent first

Because Features is the deep source, feature pages carry a second audience that outweighs the human skimmer: the AI agents (in-product, ChatGPT, Claude) that read this content via MCP, `llms-full.txt`, and `skill.md`. On feature pages, **optimize for completeness over brevity.** An agent answering a user's question can only work from what the prose states explicitly — it can't infer behavior from a screenshot, a video, or the UI.

This means: enrich the detail throughout the prose, not in a separate reference dump at the end. Cover the full behavior of the feature — every meaningful option and state, what each setting does, edge cases, limits, defaults, and how the feature interacts with other Francis features. Write it inline, as natural fuller prose, so the page reads as one continuous explanation rather than a thin narrative followed by an appendix.

The brevity instincts elsewhere in this file (cut what doesn't earn its place, short by default) still govern *quality* — no filler, no marketing-speak, no restating accounting basics. They do **not** license omitting behavioral detail an agent would need. On a feature page, a fact an agent needs always earns its place. This trade-off applies to feature pages specifically. Masterclasses stay human-first and lean on links into feature pages for depth.

---

## Content rule: BS forecasting pages
The BS fundamentals page establishes the core mental model: balance sheet forecasting is always a function of last period's value, additions, and detractions. Last period's value is included because balance sheet values accumulate over time. The additions and detractions — the net movement — are what flow through to the cash flow statement.
This framing belongs only on the BS fundamentals page. It's the deep source.
Every specific BS forecasting page (VAT, Tax, Trade receivables, Prepayments, CAPEX, Inventory, Loans) opens by referencing this framing and then making it concrete for that line item. Use this pattern:

Balance sheet forecasting is always a function of last period's value, additions, and detractions — see BS fundamentals. For [line item], this means [last period's value] + [additions for this line item] − [detractions for this line item].

Concrete examples:

Inventory: inventory last period + new inventory purchases − cost of goods sold in period
Trade receivables: trade receivables last period + new invoices issued − customer payments received
VAT: VAT payable last period + sales VAT in period - cost VAT in period − VAT paid to authorities
CAPEX: fixed asset value last period + new investments − depreciation
Loans: loan balance last period + new draws − repayments

Why this rule exists: it's the editorial principle in operation. BS fundamentals is the deep source for the conceptual model. The line-item pages are orchestration — they apply the model to a specific case rather than re-explaining it. A reader landing on the Inventory page first should still find the page complete, because the link to BS fundamentals is right there for the missing context. A reader who's already read BS fundamentals can skim the framing and jump to what's specific.
This pattern does not apply to BS validation — that page covers checks and failure modes, not forecasting mechanics.

---

## Page structure

### Universal pattern

1. **H1** — names the thing or outcome, not "Guide to X". Must fit on a single line at the default Mintlify content width — keep to roughly 6 words or fewer. If it wraps onto a second line, shorten it and push the detail into the `description` field.
2. **Video** — sub-three-minute walkthrough, embedded under the H1 (see *Visual elements* below)
3. **Lede paragraph, no header** — one or two sentences: what this is, who it's for, what they'll get. The lede *is* the overview; no "Overview" header.
4. **Descriptive H2s** — never *Basics*, *Introduction*, *Details*, *More info*. Each H2 names what's in the section.

Meta-headers describe the section's role rather than its content and fail both scanners and search. Descriptive headers become useful jump targets in the right sidebar and help a skimmer judge page relevance in seconds.

### Page-shape variants

**Feature page** (e.g. *Components*)

- H1 = the feature's name
- Lede defines it by what it enables, not by abstraction
- H2s cover: how it works, every meaningful option and state, key decisions, common patterns, gotchas, edge cases, limits, and interactions with other features
- **Optimize for completeness over brevity, inline.** This is the AI-first page type (see *The editorial principle*). Enrich the detail throughout the prose so an agent can answer from the page alone — don't strand the detail in a closing reference block, and don't lean on the video or screenshots to carry behavior. The prose must stand alone.
- State the full behavior explicitly: what each setting does, defaults, what happens at the boundaries, and what the feature can't do. If a behavior would surprise a careful reader, document it.
- Ends with links to relevant masterclasses

**Masterclass page** (e.g. *Consolidate multi-entity financials*)

- H1 = outcome-oriented
- Lede states what the user will accomplish and who it's for
- H2s: *Before you start* (prerequisites, required integrations), then each step named descriptively (*Map your entity accounts*, not *Step 1*), then *Common patterns* / *Advanced scenarios* for progressive disclosure, then *FAQ* scoped to this masterclass

**Reference page** (e.g. *Functions*, *Shortcuts*)

- H1 = the reference category
- One-paragraph lede on conventions (syntax style, argument types)
- No prose between entries — alphabetical list, each item as a collapsible H2 or H3 with syntax, one-line description, arguments, one example

**Accounting integration page** (e.g. *Business Central*, *Xero*)

Applies to each supported accounting system page under `integrations/accounting/` and `integrations-new/accounting/`, and to the *Non-supported ERP* / *other-erp* page (with one extra section, noted below). Does **not** apply to the *Overview* page — it follows its own structure.

- H1 = the accounting system's name
- Lede states what connecting enables and where the chart of accounts surfaces in Francis
- H2s, in this exact order:
    1. *Connect [system]* — auth flow and any connection variants
    2. *What Francis sources* — the data Francis pulls (journal entries, dimensions, GL accounts, etc.)
    3. *Adjustments* — automatic transformations Francis applies on import (typically a `<Tabs>` block)
    4. *Settings to enable adjustments* — user-configurable settings the adjustments depend on
    5. *Status checks* — automated checks Francis runs on imported data, usually an `<AccordionGroup>`
- If a section has no content for a given integration, keep the heading and write a one-line placeholder (*"No automated status checks for this integration yet."*) so the structure stays consistent across pages
- Anything that doesn't fit one of the five sections goes at the bottom under its own descriptive H2

**Non-supported ERP page exception:** because data arrives via a Google Sheet the user fills in by hand rather than via an API, this page adds a *Required data format* section between *What Francis sources* and *Adjustments*. It covers the sign convention and delta-value rules the user must follow when entering data. The other five sections stay in the same order. Here *Connect [system]* is *Connect Google Sheets* (Google Sheets is the bridge).

---

## FAQs

FAQs live **at the bottom of the page they belong to**, not in a separate Support section.

The questions that accumulate are mostly use-case-scoped modeling and capability questions, not cross-cutting troubleshooting. Each one only makes sense inside a specific page, and surfacing them in a separate tab would require the user to already know it's a question worth searching for. At the bottom of the relevant page, they're a natural next scroll.

**Rules for FAQs:**

- **H1-style phrasing in user voice.** Match how a stuck user would phrase the question, not an internal tidy-up of it. *"I have an asset account that I want to display as a liability account"* beats *"Reclassifying accounts by type"* because it matches what a user would search for.
- **FP&A Advisory deep-links directly.** Anchor each FAQ so advisors can link to the specific question rather than the top of the FAQ section.
- **Link back to features, don't re-teach primitives.** If an FAQ touches Components or Formulas, it references the feature page rather than re-explaining.
- **A Support section may be added later** if genuinely cross-cutting troubleshooting content accumulates (login issues, permission errors, import failures). Don't build it speculatively.

---

## Sidebar titles vs. H1s (Mintlify `sidebarTitle`)

For **masterclasses only**, decouple the sidebar label from the H1:

- **Sidebar:** short noun matching website vocabulary (*Consolidation*)
- **H1:** outcome-oriented (*Consolidate multi-entity financials*)
- **URL slug:** matches the sidebar (`/masterclasses/consolidation`)

Sidebars are scanned as categories — short nouns win. H1s frame the page for a user deciding if they're in the right place — outcomes win. Search results show the H1, so the outcome framing also works for users arriving via search or AI answers.

**Constraint:** the sidebar noun must appear inside the H1 so the two surfaces feel continuous. *Consolidation → Consolidate multi-entity financials* ✓. *Consolidation → Close the books across legal entities* ✗.

Feature pages, reference pages, and admin pages don't need the split — their names are already short.

---

## Onboarding flow

- **Docs landing page acts as a router by intent:** *I'm new* → Quickstart · *I'm trying to do X* → pick a masterclass · *I need to connect something* → Integrations.
- **Universal Quickstart** is a short orientation ("this is Francis"), not a full onboarding — the real onboarding happens inside the masterclass the customer bought for.
- **Each masterclass has its own onboarding-flavored intro** (the *Before you start* H2) so new users arriving directly from marketing aren't stranded.

---

## Progressive disclosure

Every masterclass is written for the self-serve user but structured so FP&A Advisory can use it too:

- Intro → step-by-step → advanced patterns → FAQ
- Anchor links at every H2 so FP&A Advisory can deep-link (`.../consolidation#eliminations`, `.../consolidation#faq-inter-company`)
- Advanced content lives further down the page or in FAQ, not gated into separate pages

---

## Visual elements

| Element | When to use |
|---|---|
| **Note** callout | Important context that isn't part of the main flow |
| **Tip** callout | Optional advice that improves the result but isn't required |
| **Warning** callout | Something that can go wrong, cause data loss, or be hard to undo |
| **Check** callout | Confirming a successful state ("If you see X, you've configured this correctly") |
| **Tabs** | When content branches by user context (SaaS vs. services, single-currency vs. multi-currency) |
| **Accordions** | FAQs at the bottom of pages |
| **Code blocks** | Formulas, function syntax, anything with syntax that benefits from monospace |
| **Inline code** | Single function names, keyboard shortcuts, file paths, formula snippets within prose |
| **Bold** | UI elements (buttons, fields, menu items). Only at the start of a label or combined with a link. Not mid-sentence for emphasis. |
| **Italic** | Light in-sentence emphasis only; rare |
| **Screenshots** | Sparingly. Use when the UI is genuinely complex enough that prose can't describe it efficiently — typically the first encounter with a new screen, not every step |

### Video and screenshots together

Each page has a **sub-three-minute video walkthrough** embedded directly below the H1, above the lede. Video is the best medium for many human readers; text is the source of truth for AI agents (in-product, ChatGPT, Claude) reading via MCP and skill.md.

Video embed standard
Every page video uses this exact embed pattern, placed directly below the H1:
jsx<video controls className="w-full aspect-video rounded-xl" src="/videos/[page-slug].mp4" />
Conventions:

Videos live in /videos/ at the repo root
Filename matches the page slug (e.g. videos/components.mp4 for the Components page, videos/bs-fundamentals.mp4 for BS fundamentals)
Always include controls — without it, users can't pause, scrub, or adjust volume
Always include className="w-full aspect-video rounded-xl" — full width, correct aspect ratio, rounded corners to match Mintlify's visual style
Self-closing tag (/>), not a closing </video>
Don't use autoPlay, loop, or muted on content videos — those are for decorative background videos, not page walkthroughs

When adding a new video: drop the .mp4 file in /videos/ named to match the page slug, then insert the embed at the top of the page (just below the H1, above the lede).

**Implication:** don't let video do the heavy lifting at the expense of prose. The text must stand alone and answer the user's question completely. Video supplements, never replaces.

This is also why screenshots are used sparingly: with video doing the rich visual job, screenshots earn their place only when they aid comprehension at the precise moment a reader is on that page, in text. A screenshot that exists "for completeness" is just maintenance debt.

### Don't use

- The **Info** callout — overlaps with Note. Pick one (Note) and stick to it.
- Heavy emoji or decorative iconography in body content
- Center-aligned text or unusual layouts — Mintlify defaults are clean; don't fight them

---

## Examples

Use a single fictional company as the running example across all docs.

**`[CompanyName]`** is a consumer-facing brand with:

- **Legal entities** in Denmark (parent), the UK, and the US — exercises multi-entity consolidation and FX
- **Channels**: retail, wholesale, e-commerce — exercises dimensions and channel-level reporting
- **Functional departments**: typical org structure (sales, marketing, ops, product, G&A) — exercises business partnering and headcount/OPEX planning

This single example exercises consolidation, dimensions, multi-channel reporting, business partnering, and most forecasting patterns we cover. Readers build fluency with the example as they move through the docs — when a guide says *"`[CompanyName]`'s UK retail channel"*, they already know what that means.

**Conventions for examples:**

- Use `[CompanyName]` as a placeholder until the real name is decided. Single replace-all pass updates everything.
- Numbers should be plausible for a lower-mid-market consumer brand — multi-million revenue, not Fortune 500 numbers, not garage startup numbers.
- Use the entity's natural currency in examples. DKK for the parent, GBP for UK operations, USD for US operations. Reporting currency depends on the masterclass context.
- A separate dataset (real Francis model with `[CompanyName]` data) will support these examples at the end of the rebuild process. Examples in prose should match what a reader would see if they opened that model.
- Don't anonymize so heavily it loses meaning. The whole point of a running example is recognizability.

---

## Linking conventions

Links cost the reader something. Every hyperlink is a visual interruption and a "should I click?" decision. Use them when the destination materially helps the reader, not by default.

### When to link

- **Cross-tab navigation** that isn't obvious from the sidebar — e.g. a masterclass linking to the relevant Integrations page when setup is a prerequisite
- **Related masterclass pages** within the same use case — e.g. Eliminations linking to Currency conversion when they interact
- **External references** when genuinely useful — e.g. an accounting standard, a regulatory page — used sparingly and never as the primary source for a concept

### When not to link

- **Don't link to Features pages from masterclasses or FAQs.** Features are reference material the reader can find via the sidebar. Linking to *components*, *formulas*, *charts* etc. on every mention adds visual noise without earning the click. Trust the reader to navigate the docs.
- **Don't link UI element mentions.** *"Click **Save**"* doesn't need a link to the Save button.
- **Don't link the same destination twice in the same paragraph.** Distracting.

### Patterns

**Inline links** — for genuine cross-references inside running prose. *"Set up your [accounting integration](/integrations/economic) before you start."* Used sparingly, on first meaningful mention per page only.

**Callout-style links** — for prerequisite or "go read this first" pointers. As a Note callout at the top of a guide: *"This guide assumes you've connected your [accounting integration](/integrations/economic)."* Used at the start of masterclass pages when there's a hard prerequisite.

**End-of-page Related section** — bullet list of 2–4 related pages with one-line descriptions. Used at the bottom of masterclass pages to point to the next logical destination, not to dump every related concept.

### Rules

- **Link the noun, not "click here" or "this page."**
- **Link on first meaningful mention per page, then stop.**
- **Don't link to a Feature page just because a Feature is mentioned** — that's the editorial principle inverted into noise.

---

## AI-readability

The docs are read by AI agents as well as humans — Mintlify auto-generates `llms.txt`, `llms-full.txt`, MCP endpoints, and `skill.md` from the published content. Francis's own in-product agents (planned) will query this same content.

This shapes a few things:

- **Text is the source of truth.** Video and screenshots help humans but are invisible to AI. Anything important must be in prose.
- **Feature pages favor completeness over brevity.** They are the deep source and the primary surface agents query, so document the full behavior of each feature inline (see *The editorial principle* and the *Feature page* variant). This is the one place the default brevity bias yields to thoroughness.
- **Each paragraph stands alone.** Avoid implicit context that only makes sense after reading the previous three paragraphs. AI retrieval often surfaces single chunks.
- **Consistent terminology.** Same concept, same word, every time. *"Sub-sheet"* throughout, not *"sub-sheet"* in some pages and *"subsheet"* in others. (See the glossary for canonical forms.)
- **Frontmatter matters.** Every page's `title` and `description` should be searchable, descriptive, and self-contained.
- **The skill.md file is curated.** Mintlify auto-generates one. A custom version overrides it — write that custom version once the docs are in good shape, capturing the operating rules an agent needs to use Francis.

---

## Maintenance and ownership

To be defined as the docs reach steady state. The pattern likely to emerge:

- **William** — owns the editorial standard, voice, IA decisions
- **FP&A Advisory (CS)** — owns FAQ growth based on real ticket patterns; can edit any page
- **Product team** — proposes doc updates when shipping features (via Linear ticket → PR)
- **Monthly review** — mine the in-docs AI assistant logs and FP&A Advisory tickets for recurring questions; promote to FAQ entries

---

## Glossary

A separate file (`GLOSSARY.md`) holds the canonical definitions of Francis-specific terms and finance terms as Francis uses them. The glossary doubles as SEO content for the website.

When in doubt about how to refer to a term — check the glossary. If the term isn't there, add it.