# Bulgaria Euro Monitor

A simple, dependency-free dashboard about Bulgaria after euro adoption on 1 January 2026.

## Content

- Eight official indicators covering inflation, GDP, wages, employment and trade.
- Five automatically retrieved Eurostat series, with charts and exact observations.
- A dated interpretation of evidence about the changeover and separate Commission forecasts.
- Source links, release periods, estimate flags and retrieval timestamps.

The editorial snapshot was researched on 6 September 2026. It is deliberately not relabelled as current when only an API feed refreshes. Edit `dist/snapshot.json` and the dated narrative in `dist/index.html` when reviewing new releases. Do not infer the euro's causal effect from before-and-after observations alone.

## Publish on GitHub Pages

1. Create a **public** repository named `bulgaria-euro-monitor`, with default branch `main`.
2. Upload this project's contents, including `.github/workflows/pages.yml`.
3. Under **Settings → Pages → Build and deployment**, select **GitHub Actions**.
4. Run **Actions → Refresh data and publish Pages → Run workflow** if a run is not already underway.

For account `palebridge`, the expected URL is `https://palebridge.github.io/bulgaria-euro-monitor/`. This is an expected address, not confirmation of publication.

Publishing is handled by the included GitHub Actions workflow. Enable GitHub Actions as the Pages source in repository settings before the first deployment.

## Local use

Requires Python 3.10+; no Python packages are required.

```sh
python scripts/refresh.py
python scripts/validate.py
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. The page uses local JSON fetches and should be served over HTTP rather than opened via `file://`.

## Updates

The Pages workflow retrieves data daily at 06:20 UTC and on pushes or manual runs, then publishes the generated `dist` folder. Updates are deployment artifacts, not automatic commits. A GitHub Actions cache retains prior observations when a feed fails; the initial committed snapshot is a fallback. All failed retrievals are visible. If every feed is empty, publication stops. Public-repository schedules can be disabled after 60 days without repository activity, and runs may be delayed.

HICP uses `prc_hicp_minr`, the new ECOICOP 2018 dataset (`coicop18=TOTAL`), not the archived `prc_hicp_manr`. Euro-area inflation uses fixed EA21 composition, including Bulgaria throughout the displayed history. GDP uses `CLV_PCH_SM` and `SCA`. Monthly unemployment uses `age=TOTAL` and `SA`; do not equate it with the quarterly NSI survey in the research cards.

Eurostat flags are preserved, missing observations are omitted, and the decoder rejects unintended multidimensional or empty results. The page shows the last successfully retrieved period, not an assertion that that period is the newest available release.

No API keys, personal information, cookies or analytics are included.
