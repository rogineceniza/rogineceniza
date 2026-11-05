# Rainy profile upkeep

The profile uses the existing `assets/rainy-desk.gif` and animated cat meme. No Pac-Man or retro animations are used. The older debugging meme asset is retained, but is no longer featured.

## Account visuals

`scripts/update_profile.py` generates four SVG images for **rogineceniza** using Python's standard library:

- `github-stats.svg`: public repository counts and stars; contributions from the publicly visible GitHub calendar, with the displayed date range.
- `top-languages.svg`: GitHub language bytes across all public, owned, non-fork repositories. This is not time spent coding or a proficiency rating. Only the five largest languages are displayed, with percentages of all language bytes.
- `rainy-city.svg`: an isometric view of the public contribution calendar. One building per day; height increases logarithmically with the actual contribution count. Muted slate, sage, and warm cream fit the rainy theme. This represents contributions, not lines of code.
- `code-activity.svg`: weekly additions/deletions for the last 12 weeks, from GitHub's code-frequency endpoint. Includes **all contributors** on default branches of public, owned, non-fork repositories. Coverage is shown. Repositories with pending or unavailable statistics are excluded, never invented. GitHub may return HTTP 202 until statistics are computed; the next refresh retries. The chart uses a labeled logarithmic bar scale so large imports do not hide smaller changes. It is not a personal productivity measure.

The `Refresh rainy profile` workflow runs daily at 22:23 UTC (6:23 AM Philippine time), when its code changes, or manually through **Actions → Refresh rainy profile → Run workflow**. Scheduled execution times can vary. Generated images are committed back to this repository; there is no third-party stats-card hosting dependency.

The workflow requests repository contents write permission. If an organization policy blocks it, an administrator must allow workflow writes. No personal access token is needed. Public data is used; private project details are not collected.

If GitHub changes the public contribution-calendar HTML or an essential API fails, generation fails rather than fabricating activity. Existing committed images remain available, showing their last update date. Code-frequency and optional WakaTime failures do not prevent the other visuals from updating.

## Optional WakaTime

1. Connect your editor to WakaTime using its editor extension.
2. Obtain a WakaTime **OAuth token with permission to read your stats**. The editor's write-only API key cannot read statistics.
3. In this repository's **Settings → Secrets and variables → Actions**, add the secret `WAKATIME_TOKEN` containing that OAuth token.
4. Add the repository variable `ENABLE_WAKATIME` with value `true`.
5. Run **Refresh rainy profile**. It updates only the content between the existing `waka` markers in `README.md` with language/time statistics from the last seven days.

WakaTime stays disabled until both settings are supplied. No token is stored in the README or generated images. Project names and editor details are not published.

## Projects

Baby Cry Recognition links to `cry-code`; Baby Cry Recorder Mobile App links to `Android-App-Baby-Cry`. The other two cards intentionally have no repository links until their exact URLs are supplied. No unverified frameworks, deployment status, or feature lists are claimed.

Add more project rows inside the existing table in `README.md`. Keep local asset paths relative to the repository root and preserve the WakaTime markers.
