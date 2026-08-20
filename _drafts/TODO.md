# Docs: first-release deferrals

Things stubbed out or hidden for the first release. Revisit these as content is ready.

## Drafted pages (moved out of nav)

These `.mdx` files live under `_drafts/` mirroring their original path. To publish: move back to the original location and re-add to `docs.json` nav.

- `masterclasses/budgeting-forecasting/pnl-forecasting/subscription-revenue.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/project-revenue.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/product-revenue.mdx`
- `masterclasses/budgeting-forecasting/budget-and-forecast-versions.mdx`
- `masterclasses/reporting/department-dashboards.mdx`

## Links removed (restore when the target pages are published)

- `features/using-francis/version-control.mdx` — "See in action" linked to **Budget and forecast versions**. Restore the link (and revert "masterclass" back to "masterclasses") once that page is live.
- `features/using-francis/dashboards.mdx` — "See in action" linked to **department dashboards**. Restore the link once that page is live.

## Videos

All page video embeds are commented out (`{/* <video ... /> */}`) across the `-new` folders. Uncomment when the video files exist.

## Empty FAQs commented out

FAQ sections with only placeholder answers (TODO or "coming soon") were wrapped in `{/* ... */}`. Fill in real answers and uncomment. Affected pages:

- `features/using-francis/data-mappings.mdx`
- `masterclasses/consolidation/department-pnls.mdx`
- `masterclasses/consolidation/consolidation.mdx`
- `masterclasses/business-partnering/gathering-budget-input.mdx`
- `masterclasses/budgeting-forecasting/forecasting-approaches.mdx`
- `masterclasses/budgeting-forecasting/cf-forecasting/cf-fundamentals.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/pnl-fundamentals.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/headcount.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/cogs.mdx`
- `masterclasses/budgeting-forecasting/pnl-forecasting/opex.mdx`
- `masterclasses/budgeting-forecasting/bs-forecasting/vat.mdx`
- `masterclasses/budgeting-forecasting/bs-forecasting/receivables.mdx`
- `masterclasses/budgeting-forecasting/bs-forecasting/bs-fundamentals.mdx`

## Status checks commented out (integrations)

Status check sections wrapped in `{/* ... */}` for launch. Uncomment when the checks are ready to surface. Note: CLAUDE.md's accounting-integration page structure lists *Status checks* as a required section, so these are a temporary deferral.

- `integrations/accounting/e-conomic.mdx` (1 check: missing FX rate on draft entries)
- `integrations/accounting/business-central.mdx` (3 checks: missing account categories, missing journal entries, deleted dimension values)
- `integrations/accounting/quickbooks.mdx` (placeholder line)
- `integrations/accounting/xero.mdx` (placeholder line)
- `integrations/accounting/netsuite.mdx` (placeholder line)

## Feature mentions commented out

- `masterclasses/budgeting-forecasting/forecasting-approaches.mdx` — the `predict()` function mention (Statistical section) is commented out. Uncomment when ready to surface it.

## Management report

- Settings detail per primitive (metric boxes, charts, tables) still to be added from config screenshots, once the walkthrough design is finalized.
