# SME Intelligence Hub — Static HTML Prototype (Version 1.7)

Pure HTML, CSS and JavaScript. No Node.js, Express, database, localStorage or IndexedDB.

## Add the UDX data files

Copy these four real output files into `input/`, preserving the exact filenames and uppercase `.JSON` extension:

- `udx_run_summary.JSON`
- `sme_golden_records.JSON`
- `intervention_potential_leads.JSON`
- `financing_potential_leads.JSON`

Expected data fields:

| File | Declared count | Array |
|---|---|---|
| `sme_golden_records.JSON` | `RECORD_COUNT` | `GOLDEN_RECORDS` |
| `financing_potential_leads.JSON` | `LEAD_COUNT` | `FINANCING_POTENTIAL_LEADS` |
| `intervention_potential_leads.JSON` | `LEAD_COUNT` | `INTERVENTION_POTENTIAL_LEADS` |
| `udx_run_summary.JSON` | `OUTPUT_COUNTS` | — |

The summary should include `GENERATED_AT`, `SOURCE_SUMMARY`, `OUTPUT_COUNTS`, `MATCHING_STATISTICS`, `DATA_QUALITY`, `PROCESSING_TIMINGS_SECONDS` and `IDENTITY_STATISTICS`.

## Run

Browsers restrict `fetch()` from `file://`. Use any static HTTP server (this is not an application backend). Easiest option, with Python installed:

```bash
python -m http.server 8000
```

Run that command from this folder and open `http://localhost:8000/`. Stop with Ctrl+C. Alternatively, copy the folder to an existing Apache/Nginx static website directory.

## Refresh workflow

1. Replace all four JSON files in `input/` using outputs from the same UDX run.
2. Open **Admin / Dataset** and click **Validate & Reload Data**.
3. The loader fetches all four files with `cache: no-store`.
4. It validates JSON syntax, required fields, array types, declared counts and consistency with summary output counts.
5. Differences in `GENERATED_AT` are warnings, not fatal errors. The provided run had Golden Records at 10:56:04 and other outputs at 10:56:05.
6. Any missing file, invalid JSON, missing required field or count mismatch rejects the new dataset. The dashboard will not adopt a partially loaded set.

A static browser app cannot guarantee atomic replacement of four separate files while another process is copying them. Replace the files as one controlled operation, then validate. For stronger atomic publishing, have the upstream UDX process stage a complete versioned set and publish it together.

## Pages

- Main — KPI cards, intervention breakdown and Engagement Touchpoints.
- Master Profile — searchable, paginated Golden Records.
- Financing Leads — searchable, paginated financing leads and tier filter.
- Intervention Potential — searchable, paginated intervention leads with type and tier filters.
- Data Information — matching, data quality and processing details.
- Admin / Dataset — validation and refresh.

No external chart library is required. Tables render 15 rows per page. The prototype avoids displaying contact PII on the executive dashboard.


## Record detail drill-down

Click an SME ID in **Master Profile**, or a Lead ID in **Financing Leads** or **Intervention Potential**, to open a detail panel. The panel shows the matching Master Profile, the selected lead where relevant, and other financing/intervention records associated with that SME ID. Related leads can be opened directly from the panel. Fields are rendered dynamically from the JSON record, so additional fields can appear without changing the page layout. Data is read from the already-loaded in-memory dataset and is not persisted in browser storage.


## SME and lead record details

Click an SME ID in Master Profile or a Lead ID in Financing Leads / Intervention Potential to open a detail modal. It displays the corresponding Golden Record, the selected lead when applicable, and all related financing and intervention records linked by SME_ID. Related leads can be opened from the modal. Record fields are rendered dynamically from JSON.


## Version history

- **Version 1.1** — Fixed company-name field compatibility. The dashboard now displays `COMPANY_NAME` when present and falls back to `BUSINESS_NAME`. This applies to Master Profile, Financing Leads, Intervention Potential, their search filters, and the SME detail modal. The source JSON files do not need to be renamed or modified.

- **Version 1.2** — Financing Leads and Beyond Financing Leads now use SME ID as the visible/clickable record identifier; Lead ID is removed from those tables and their search. Clicking SME ID opens an SME-centric detail view with a prominent Company Name, City, State, Sector, SME ID, Revenue (RM), ELSA Stage (when supplied), and Financing Lead follow-up status. All associated financing and intervention records are grouped by SME ID.

- **Version 1.3** — Added distinct icons beside the Unique SMEs, Financing Leads and Open Interventions KPI counts. Increased KPI count typography while keeping the count larger than its icon; responsive sizing is included for smaller screens.

- **Version 1.4** — KPI labels remain above the count values. Count values are enlarged to 48px on desktop and 40px on mobile; icons sit beside the numbers and remain smaller than the counts.

- **Version 1.7** — Moved KPI icons to the left of the text block. Each icon is vertically centered alongside the label, large count and supporting description, visually spanning the full KPI content height. KPI count remains the dominant element.


Version 1.7: Removed the em-dash placeholders from the three Main Dashboard KPI count fields. KPI values now display without a trailing placeholder dash.


## Version 1.8 visual theme
A restrained blended corporate palette inspired by SME Bank and Bank Pembangunan:
- SME Bank red: `#BD2426`
- BPMB blue: `#005FAA`
- BPMB navy: `#142238`
- BPMB yellow accent: `#F4C542`

The palette is applied to navigation, KPI icon backgrounds, charts, tables, buttons and interaction states. Existing layout and static JSON loading are retained. The decorative dash beneath each KPI card has been removed.


## Version 1.9
- Increased typography across dashboard, tables, navigation and detail views.
- Added left-side icons to navigation items.
- Added illustrative Year, Region and Sector dashboard filters (visual prototype controls).
- Moved Data Information below Admin / Dataset in the sidebar.
- Set table pagination defaults to 10 records per page while retaining existing pagination controls.
- Added explanations for score calculation, tiers and Review Required status.


## Version 1.9 changes
- Increased typography throughout the dashboard, data tables, navigation and SME detail profile.
- Added consistent icons to all left navigation items.
- Added Year, Region and Sector prototype filters on Main Dashboard; these are visual controls and are not connected to data filtering.
- Moved Data Information below Admin / Dataset.
- Changed table pagination to 10 records per page, retaining Previous and Next controls.
- Added score, tier and Review Required explanations beneath Financing Leads and Intervention Potential tables.


## Version 1.10 — Detail Profile refinements
- Applied a consistent corporate sans-serif typography stack to the detail modal and its content, using Roboto with local fallbacks (no external font download required).
- Removed source-field provenance properties from Master Profile detail rendering.
- Financing Leads detail sections now show REASONS only.
- Beyond Financing Leads detail sections now show INTERVENTION_TYPE and REASONS only.


## Version 1.11
- Removed the global “Understanding Scores, Tiers & Review Status” guidance section so it no longer appears on the Master Profile page.
- Retained and expanded the Financing Leads scoring guidance.
- Documented the Raw Data Score components and maximum points: Financing Demand (35), Growth Potential (25), Financial Readiness (25), and Sustainability (15).
- Explained lifecycle adjustment factors: Take-off/Maturity (1.0), Pre-Take-off (0.6), Renewal (0.5), and Stagnation (0.3).
- Explained High (80–100) and Medium (60–79) tiers; Emerging and Low remain subject to the active UDX configuration.
- Changed the flagged review label in Financing Leads and Intervention Potential tables from “Review” to “Need to review”.
