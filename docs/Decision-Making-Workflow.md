<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# This is the current Decision-Making Workflow of the team:

Filter tenders by institution (e.g., Caja) and date range
Review budget size to determine if opportunity is worth pursuing
Check supplier participation requirements (all vs. pre-qualified only)
If pre-qualified only and not qualified, eliminate from consideration
Evaluate if there's time to manufacture (even without registration)
Review quantity and pricing
Contact manufacturer via WhatsApp or email with product specifications
Assess business opportunity and profit margin
Request technical documentation and verify manufacturer can meet specifications
Manufacturer provides complete dossier (typically 15-22 days) including bioequivalence studies, stability studies, analytical methods, manufacturing certifications, etc.
Submit to registration department to begin formal registration process
Review historical participation data to assess competition

//

it's not slow and we must extract all information we can.
///
Product description
Type of procedure (major need vs. special)
Total estimated budget
Clarifications received
Supplier participation requirements (critical for determining eligibility)
Delivery schedule and quantities
Technical documentation and attachments
Supplier Participation \& Pre-qualification
Pre-qualified suppliers are restricted on certain tenders, while others allow all suppliers to participate
Pre-qualification requires submitting physical product samples beyond just registration papers
The laboratory checks product quality, packaging (primary, secondary, tertiary), and verifies alignment with documentation
Currently 191 products classified as "difficult to acquire" with no pre-qualified supplier available

Bioequivalence
Bioequivalence certification demonstrates that a product is chemically similar to the original formula and achieves approximately 90% of the original's effectiveness
Requires manufacturer studies costing \$120,000 per product
Mexican laboratories typically have bioequivalence certification for all their products
Products with bioequivalence certification provide a significant competitive advantage even when not required
Historical Price Analysis
Historical data available from approximately 2000 through October 2024
Source data originally came from PDF files published by the box system, which stopped being published after 2025
Data includes: product name, box code, price, quantity, supplier, country of origin, and currency (standardized to dollars)
Historical analysis helps determine if suppliers can reach competitive prices and if order quantities are feasible for manufacturers
Product Code Systems
Multiple classification systems exist: box code, CCOC classifier code
Available lists include: acquisition buildings list, products with therapeutic equivalence, complete box list (approximately 840 codes), and difficult-to-acquire medications
Box code can be used to locate technical files in the CAF system

This is the real product definition right here. The workflow you just described isn't a feature list — it's a **decision tree with 12 nodes**, and each node has a data dependency. Let me map it directly:

***

## What the workflow actually needs, node by node

**Node 1 — Filter by institution + date range**
Already solved. ETL running, `instnm` + `biddocstartdt` indexed. Ship it.

**Node 2 — Review budget size**
Partially solved. `montocolones` exists but has `parse_confidence` issues. The field that actually matters here is **total estimated budget from the cartel itself**, not the adjudicated amount — those are different numbers. The cartel publishes a presupuesto estimado before adjudication. That's in a field you haven't mapped yet. This is a gap.

**Node 3 — Supplier participation requirements**
This is the most critical node and the most underserved by the current schema. "All suppliers" vs "pre-qualified only" is a binary that eliminates the opportunity entirely if wrong. This lives in the cartel documents, not the list API. You need the detail endpoint.

**Node 4 — Eliminate if pre-qualified and not qualified**
Depends on node 3 + a user profile table. User says "I am qualified for codes X, Y, Z" — the app auto-filters. This is a product feature, not ETL.

**Node 5 — Time to manufacture**
`biddocenddt` (offer deadline) minus today. Simple derived field. But "time to manufacture" is supplier-specific — this is a user input, not a SICOP field. The app shows the deadline, the supplier judges the gap.

**Node 6 — Quantity and pricing**
Quantity lives in the line items (partidas). Not in the list API. This is the same unmapped detail endpoint as node 3. Unit price from `montocolones` / quantity — only possible once you have both.

**Node 7 — Contact manufacturer via WhatsApp**
This is an action, not a data need. But it implies the product needs a **spec sheet export** — a formatted PDF or card with all the tender details that a supplier can forward to a manufacturer directly from the app. High value, low complexity.

**Node 8-9 — Assess margin, request dossier**
These happen outside your system. But if you capture the outcome ("we're pursuing this") you get a CRM hook — saved opportunities, status tracking. Medium-term feature.

**Node 10 — Manufacturer dossier (15-22 days)**
Timeline is fixed by regulation. The app can set a deadline reminder: "You have 18 days before offer deadline. Dossier typically takes 15-22 days. ⚠️ Risk."

**Node 11 — Submit to registration**
Entirely external. But you can link to the formal registration pathway.

**Node 12 — Review historical participation**
This is the `precioshistoricos` table + your datos abiertos source. You have data from 2000-Oct 2024. **This is a paid feature.** "3 suppliers have bid on this product code in the last 4 years, average price \$X, lowest bid \$Y from MX manufacturer Z."

***

## The two gaps that block this workflow today

**Gap A — Detail endpoint (nodes 3 + 6)**
Participation requirements and quantities live in the cartel detail, not the list. You need to map:

```
POST /bid/api/v1/public/epCartel/getDetail   (or equivalent)
```

Navigate to any CCSS cartel in the SPA, watch DevTools, find the call that loads the full cartel body. That's the endpoint. One DevTools session.

**Gap B — Historical price table (node 12)**
You have the datos abiertos source. The historical data from 2000-Oct 2024 with product name, caja code, price, quantity, supplier, country, currency (USD normalized) is exactly what you need. The question is: is it downloadable as structured data or only as PDFs? If the latter, you have a parsing project. If the former, it's a one-time import.

***

## What to build first given this workflow

Not the full `/licitaciones` browse page. That's a nice-to-have.

**The thing that creates value immediately is a tender detail page** — one URL per `instcartelno` that shows everything the team needs to make the node 2-6 decisions in one place, without switching tabs. If you can cut the "open 6 SICOP screens + download PDF + open WhatsApp" workflow down to "open one page, tap Export Spec Sheet," that's the product.

That page needs:

- `cartelnm` — full title
- `instnm` — institution
- Participation type — pre-qualified vs open ← requires detail endpoint
- `biddocenddt` — deadline with countdown
- `montocolones` — estimated budget
- Quantities per partida ← requires detail endpoint
- Historical prices for same product code ← requires precioshistoricos
- Manufacturer contact button (pre-filled WhatsApp message with spec)
- "We're pursuing this" toggle → saves to pipeline

Build the page with the data you have, show greyed-out placeholders for the two gaps, and the gaps become obvious to anyone you demo it to. That's also your sales tool.

