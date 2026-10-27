# Maintainer workflow

For the organiser's review team. Entrants do not need this file.

## 1. On every pull request

CI (`.github/workflows/submission-check.yml`) runs:

1. `scripts/check_pr_paths.py --author <PR author>` — fails if anything outside `submissions/<author>/` changed.
2. `scripts/self_check_submission.py --no-write <each changed package>` — the twelve gates.

A failing PR is not reviewed. Ask the entrant to fix and push again; do not fix it for them.

## 2. Before merging

1. Check out the PR locally and re-run `python scripts/self_check_submission.py submissions/<login>/<slug> --no-write` in a clean environment (`pip install -r requirements.txt`). The result must match the committed `self_check.json`.
2. Content review — gate G9 and blocking conditions B1–B5 (`brief/evaluation.json`): no personal data, no claimed approvals, nothing harmful or off-topic.
3. Open `drawings/a3-booklet.pdf`. If the drawings contradict the statement, say so in review.
4. Merge. **Merging means the format and gates passed — nothing more.**

## 3. After merging

0. At the deadline, record each entry's `package_sha256` (from `self_check.json` on `main`): that is the version reviewed. Do not merge changes to submitted directories until results are announced.
1. Written review: add `submissions/<login>/<slug>/FEEDBACK.md` by a separate pull request — what holds, what does not, against D1–D7. Not a score.
2. Publication (only when the review team decides): add an entry to `gallery/gallery-publication.json`:

```json
{"path": "submissions/<login>/<slug>", "reviewed_package_sha256": "<package_sha256 from self_check.json>", "published_at": "YYYY-MM-DD", "featured": false}
```

3. Run `python scripts/generate_submissions_data.py <gh-pages checkout>` and commit `submissions-data.js` on the `gh-pages` branch. An entry shows as published only while its current fingerprint equals the reviewed one; if the entrant changes the package later, it drops back to unpublished until reviewed again.

## 4. Before any award

Reproduce the self-check of every shortlisted package under observation (`brief/evaluation.json`, process stage 5). A disclosure that does not match what happened disqualifies.

## 5. Changing the brief

Every change to `brief/`, `scripts/` or `templates/` gets a line in `CHANGELOG.md` and, if it affects entries, a GitHub Release so watchers are notified. Bump `SCRIPT_VERSION` in `scripts/xcity_common.py` when a script's output changes.

## Publishing maintainer changes

Two branches: `main` holds the competition (brief, site data, tools, submissions) and is what agents read; `gh-pages` holds the website only. Maintainer changes are prepared on the fork `jingyuanhuang-design/xcity-ai-competition`: its `publish` branch for `main`, its `gh-pages` branch for the website. The workflow `.github/workflows/publish-from-fork.yml` checks both every 15 minutes (or on demand: Actions → publish-from-fork → Run workflow, or after any push to `main` or `gh-pages`). It fast-forwards `main` when `main` is an ancestor of `publish` and the example scheme passes the twelve gates, fast-forwards `gh-pages` the same way, and then publishes the website: the `gh-pages` files with `main`'s `submissions/` copied next to them. It never overwrites a branch, and it cannot change files under `.github/workflows/`. To pause publishing, disable the workflow in the Actions tab.

## Automatic compliance versus design content review

`self_check.json.pass` and `automated_compliance_status` describe encoded checks only. `design_content_review.status = not_assessed` is intentional: the checker cannot approve a plan. G12 verifies evidence paths and node views, not planning adequacy. In the independent written review, explicitly assess settlement/centre hierarchy, five system locations and scales, primary movement, resource infrastructure, fixed-pilot connections and phasing. A coloured full-site diagram alone is insufficient; do not impose a construction-area minimum or one urban pattern. Record findings and the reviewed package fingerprint separately before publication. Fixed pilot structure-label conflicts are review notes, not a reason to silently rewrite an entrant's geometry.
