# SME Intelligence Hub HTML Prototype

## Required JSON files
Place these four files in the same folder as the HTML, CSS and JS files:
- `udx_run_summary.JSON`
- `sme_golden_records.JSON`
- `financing_potential_leads.JSON`
- `development_training_potential.JSON`

The names are fixed in `udx-app.js`. Future datasets can replace the current contents as long as the filenames and JSON structure remain the same.

## Run on Windows
Open Command Prompt in this folder and run:
`python -m http.server 8000`
Then browse to `http://localhost:8000`.

Do not open the HTML directly with `file://`; modern browsers usually block local JSON fetches in that mode. A Node.js alternative is `npx http-server -p 8000`.

## Pages
- `index.html`: JSON-only SME Intelligence Summary dashboard. KPI values and charts are derived from the four loaded JSON files; a metric displays NA when the required value or fields are unavailable. No illustrative business figures are hardcoded.
- `dataset_manager.html`: dedicated JSON upload/reload manager (also accessible from the bottom of the sidebar). Uploads are parsed and validated in-browser, with success/error feedback; supported array wrappers are listed in the upload validation messages.
- `sme_master_profile_v7.html`: Golden Record directory, search, state filter, pagination
- `sme_master_profile_detail_v2.html?id=MY-SB-EL6T8`: profile detail, contributing source records and provenance
- `financing_potential_lead_v2.html`: financing lead directory supporting the top-level JSON array format with `LEAD_RANK`, `SME_ID`, `SME_ID_MATCH_METHOD`, `COMPANY_NAME`, `LEAD_SOURCE`, `PROGRAMME`, `STATE`, `SECTOR`, `SME_CATEGORY`, `READINESS_SCORE`, `CONVERSION_PROPENSITY`, `FINAL_LEAD_SCORE`, `LEAD_PRIORITY`, and `RECOMMENDED_ACTION`. The page displays SME_ID instead of a generated Lead ID, includes the matching method, supports search, state/priority filters and rank/score sorting, and links to the SME Master Profile when an SME_ID is present.
- `training_potential_v2.html`: training candidate leads, filters and qualification criteria
- `udx-app.js`: shared JSON loading/rendering logic
- `udx-styles.css`: shared responsive theme

The prototype expects the four data JSON files to be copied into this folder separately; they are not embedded in the ZIP. Dashboard metrics with unavailable data display NA. Detail-page fields that are absent from source records display an em dash. Candidate leads are not approvals; follow each JSON disclaimer and validate eligibility, need, consent and current status before outreach/referral.


## Financing lead JSON format

The financing dataset may be a top-level JSON array containing `LEAD_RANK`, `SME_ID`, `SME_ID_MATCH_METHOD`, `LEAD_SOURCE`, `TRAINING_PARTICIPANT`, `PROGRAMME`, company/contact details, scoring fields, `LEAD_PRIORITY`, and `RECOMMENDED_ACTION`. The interface does not generate lead IDs or recalculate scores. `LEAD_RANK` is a ranking position; `SME_ID` is the existing Golden Record identifier.

## Main Dashboard AI Chatbot

The Main Dashboard includes a prototype chatbot that answers supported questions using the JSON datasets loaded in the browser. It does not connect to a live AI model; unknown or unavailable values are reported as NA.


## Financing Leads JSON format
The financing dataset may be a top-level JSON array (like the new lead-scoring output) or an object containing a recognised leads array. The financing page displays the new lead-scoring fields directly and does not recalculate supplied scores. `null` or missing values are displayed as an em dash; invalid placeholder sector values such as `0` and `0.00` are excluded from the sector chart.


## Large dataset storage (v11)

- JSON datasets are no longer saved to `localStorage`, avoiding the small browser quota that caused the Golden Records upload to fail.
- Loaded and uploaded datasets are stored in **IndexedDB** (`sme-intelligence-hub` database, `datasets` object store), which supports substantially larger structured data.
- On first use, the app loads the fixed JSON files beside the prototype and attempts to cache them in IndexedDB. Later page visits reuse the cached dataset.
- Dataset Manager uploads are validated before replacing the current dataset. If IndexedDB is unavailable, the dataset can still be used during the current page session; the manager displays a warning that it could not persist.
- “Clear / Refresh” clears the prototype's IndexedDB dataset cache and reloads the fixed JSON files. This does not delete or modify the source JSON files on disk.
- Run using `python -m http.server 8000` and open `http://localhost:8000`; do not use `file://`.


## v12 update
- The Main Dashboard's **SME by State** chart now displays only the top 8 states, ranked by record count (highest first). The underlying state aggregation and chatbot response remain unchanged.
