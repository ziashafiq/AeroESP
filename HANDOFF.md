# AeroESP - Handoff

**Date:** 2026-09-08
**Branch:** `main` (deployed) — `phase7-research-review` is identical
**Test suite:** 336 tests, all passing
(`python manage.py test --settings=config.test_settings`)

> **Standing rule, effective 2026-09-08:** Liara does not run
> migrations on deploy - confirmed after the round-two push 500'd on a
> missing column. After every push to `main`: shell into the live app
> and run `python manage.py migrate --plan`, then `migrate --noinput`
> if it lists anything. See "Migrations - MUST be run manually" below
> for the full root cause.

---

## Deploy state

`main` was fast-forwarded from `df9c404` and pushed, which triggers the
Liara deploy. Everything below is now on `main`.

Before this push, production was running `df9c404` — which had **none**
of the Unfold admin theme, the Promote action, or the footer fix. That
single fact explains several of the reported bugs.

---

## Priority 1 — blockers

| # | Problem | Cause and fix | Commit |
|---|---------|---------------|--------|
| 1-a | Teacher profile showed the admin's name | **Not data corruption.** `teacher_pending.html` is the only page a logged-in user reaches that extends `public_base.html`, whose footer credits the developer in bold. It carried no name of the signed-in user, so the credit read as their own. Students never land on a `public_base` page while logged in — hence "Teachers only". The page now states who is signed in, above the credit. | `1eaea80` |
| 1-b | "Promote to expert reviewer" not found | **No code fault.** The action was written in `7ca4c29` and never pushed; production could not have had it. Also note the dropdown is hidden until a row is ticked (Unfold behaviour) — see click path below. | `7ca4c29` (now deployed) |
| 1-c | Mail sent from the personal Gmail | `DEFAULT_FROM_EMAIL` was already env-driven; the variable was simply unset, so it fell back to the authenticated mailbox. Added a boot warning for the silent-rewrite trap, plus tests that both user-facing mails use the configured sender. **Requires an env var — see below.** | `5010789` |
| 1-d | "Habib Ziashaiq" in the footer | Missing `f`, in both `base.html` and `public_base.html`. Database checked across every text field: no rows carried it. | `8d0de1d` |

## Priority 2 — functional

| # | Problem | Cause and fix | Commit |
|---|---------|---------------|--------|
| 2-a | Teacher "Overview" page | `accounts:teacher_dashboard` is a bare redirect to `learning:teacher_learning_dashboard` and sat directly above a link to it — two adjacent items, one page. Sidebar item removed; URL and view kept because the Account Center links to them. | `3ee4be4` |
| 2-b | Login with email | `EmailOrUsernameModelBackend` resolves an email to its account, then delegates to `ModelBackend`. Only consults email when the input contains `@`, which a generated username never does. **No enumeration:** unmatched input is passed to `super()` rather than returning early, preserving the dummy-hash timing defence; a test asserts the two responses are byte-identical once the address and CSRF token are normalised. Axes untouched and still first. | `bf53e59` |
| 2-c | Guide Hub empty | `seed_guide_resources` management command, idempotent (matches on title). Nine resources, every URL verified live before inclusion. A tenth candidate answered 403 and was dropped rather than shipped. **Must be run after deploy — see below.** | `16e2221` |

## Priority 3 — cosmetic

| # | Problem | Cause and fix | Commit |
|---|---------|---------------|--------|
| 3-a | `/admin/login/` unstyled | **No code fault.** No custom `admin/login.html` exists anywhere. Production simply had no Unfold. Verified by screenshot after deploy: centred form, full-width fields, brand-blue button, correct in both schemes. If it still looks wrong locally, it is the browser cache — see the note on `WHITENOISE_MAX_AGE` below. | — |
| 3-b | AI section layout broken | `.ai-feature-card` hardcoded a white gradient while inheriting themed text, so dark mode put light text on a near-white card. Now uses `var(--theme-surface)`. `.study-block` had the same defect and got dark-mode overrides. | `0740fe0` |
| 3-c | Theme broken in the Google app WebView | In in-app WebViews with site data blocked, `localStorage` **throws** rather than returning null. Every access was unguarded in both inline bootstraps and the theme engine, so the exception killed the script: no `data-theme` attribute, dead toggle buttons, no system-change listener. Chrome allows storage, hence "browser-specific". All accesses guarded with an in-memory fallback; `media.addEventListener` feature-detected against the legacy `addListener`. | `0740fe0` |
| — | Admin labels | Found in the screenshot review: `Research_Review`, `Ai interaction events`, `Learning progresss`. Fixed via `verbose_name`. Migrations are `AlterModelOptions` only — `sqlmigrate` reports `(no-op)`. | `8d8ea98` |

---

## Manual steps required after deploy

### 1. Environment variable (Liara panel)

One variable, for problem 1-c:

```
DJANGO_DEFAULT_FROM_EMAIL = AeroESP <support@aeroesp.com>
```

**This alone is not enough.** Gmail will not send as an address it does
not own. ImprovMX forwards mail *inbound* to `support@aeroesp.com`; it
grants no right to send *from* it. Without the step below, Gmail
silently rewrites the header back to the personal address and delivers
anyway — the failure is invisible.

In the Gmail account used for SMTP:
Settings → Accounts and Import → "Send mail as" → Add another address →
`support@aeroesp.com` → confirm the code that arrives via the ImprovMX
forward.

Only after that will the From address stick. The app now prints a
warning at boot when the two domains disagree.

Optional, same reasoning:
```
DJANGO_SERVER_EMAIL     = AeroESP <support@aeroesp.com>
AEROESP_SUPPORT_EMAIL   = support@aeroesp.com
```
`AEROESP_SUPPORT_EMAIL` is what the "Report a problem" footer link uses;
it currently shows the personal Gmail.

### 2. Migrations — MUST be run manually, confirmed 2026-09-08

**Liara does not run `manage.py migrate` automatically. This is now
confirmed, not a caveat.** The `color_palette` migration from the round-two
push was not applied on deploy, and `/accounts/account/` (any page
touching `CustomUser`) 500'd with `column accounts_customuser.color_palette
does not exist` until it was run by hand.

Root cause: `deploy.sh` — the script both previous HANDOFF versions
pointed to — is never invoked by Liara at all. Nothing in this repo
wires it in: no `Procfile`, no release-command key, no reference to it
anywhere outside this file. It matches the systemd/nginx VPS deploy kit
in `deployment/` in spirit, but even that kit's own unit file
(`deployment/aeroesp.service`) calls `gunicorn` directly and skips
`deploy.sh` too — so as far as this repo shows, `deploy.sh` has never
been executed by anything, ever.

Liara's own documented `liara.json` keys for the `django` platform are
`mirror`, `pythonVersion`, `timezone`, `collectStatic`, `compileMessages`,
`modifySettings`, `geospatial` — no `migrate`, no release command, no
start-command override. `collectStatic: true` is why static files *do*
show up correctly after a deploy; there is no equivalent flag for
migrations, and the platform's own docs do not mention running them.

**Standing process from now on — after every push to `main`:**

1. Open a shell on the running app (`liara shell <app-name>`, or the
   Liara panel's web shell).
2. `python manage.py migrate --plan` — read-only, shows exactly what
   would run without touching anything.
3. If it lists anything, `python manage.py migrate --noinput`.

Do this from inside the deployed container, not from a local checkout —
`AEROESP_DB_HOST` in the local `.env` is a bare Liara-internal service
name, so a local `migrate --plan` may silently check the wrong thing
(or fail to connect at all) rather than reporting on the database the
live site actually uses.

This round's two migrations, for reference — both metadata-only:

```
intelligence/0018_alter_aievaluationdataset_options_and_more.py
learning/0011_alter_learningprogress_options.py
```

`sqlmigrate` reports `(no-op)` for both, but that does not matter now:
*any* migration needs this same manual step, schema-changing or not,
since nothing applies it for you.

### 3. Seed the Guide Hub

Not automatic. Once, on production:

```
python manage.py seed_guide_resources
```

Add `--dry-run` first to see the list. Re-running updates in place
rather than duplicating.

### 4. Grant the first expert reviewer

Click path (the dropdown is **hidden until a row is ticked** — this is
why it seemed missing):

1. `/admin/` → **Accounts** → **Teacher profiles**
2. Tick the checkbox next to the teacher
3. The **Action** dropdown appears above the list
4. Choose **"Promote to expert reviewer"** → Go

The teacher must already be `APPROVED`; the action refuses otherwise and
says so. To withdraw: **"Revoke expert reviewer access"** on the same
screen, or the actions on Expert reviewer profiles. Revoking deactivates
and keeps the row, so `reviewer_code` and submitted reviews survive.

### 5. Browser cache

Hard-refresh (`Ctrl+Shift+R`) after deploy. `WHITENOISE_MAX_AGE` is one
year when `DJANGO_ENV=production`, so the pre-Unfold admin CSS is cached
aggressively. This is what made `/admin/login/` look broken locally
earlier.

---

## Known issues — reported, not fixed

Deliberately left for a decision:

1. **No logo on `/admin/login/`.** Unfold's unauthenticated layout
   renders `SITE_TITLE` as text and does not use `SITE_LOGO`. Adding it
   means overriding an Unfold template, which is more than a cosmetic
   tweak this close to a deadline.
2. **Sidebar scrolls at 900px viewport height.** All six groups and
   thirty links render; the lower groups need a scroll on a short
   window. Fixable by collapsing groups or trimming items.
3. **Sticky save bar overlaps tall textareas.** Unfold default on long
   change forms.
4. **`question_provenance` is 100% `AI_GENERATED` by backfill**, not by
   classification — migration `0005` set the default with no data
   migration. It cannot be cited as a deliberate label. Relevant to the
   `questions.csv` work.
5. **No prompt text is stored anywhere.** `AIPromptVersion` holds only a
   version label; `request_data` holds parameters, not the rendered
   prompt. Reproducibility for a paper's Methods section is limited to
   provider + model + protocol + source material.

## Research pipeline state

`export_question_pool` is written and dry-run verified but **has not
been run for real** — no `questions.csv` or manifest exists yet. Last
verified selection: 78 GOLD80 (two dropped as already assigned to the
R01 test account) + 22 seeded top-up = 100, balanced 12–13 per service.

The two source CSVs live in `Downloads`, not the repo, and are covered
by `.gitignore` patterns (`*GOLD80*`, `*ID_MAP*`,
`question_pool_manifest*.csv`) because they map each blinded question to
the model that produced it. Neither has ever been committed. Run the
command against those paths; `questions.csv` (blind_id only) is safe to
commit, the manifest is not.

The `R01 / expert_test` reviewer profile was set
`is_active_reviewer=False` on the local database only — **not on
production.** If that account exists there, deactivate it in the admin.

---

# Round two — optional improvements

Four features, four commits, on top of `eeb4d38`. All pushed to `main`.

| Commit | What |
|--------|------|
| `e99dbe0` | Installable as a PWA |
| `fb68b40` | User-selectable accent palettes |
| `9d66495` | Charts for evaluation results |
| `eecfd8b` | Choosable profile avatars |

## Migrations

Two, both additive with defaults — no backfill, no downtime:

```
accounts/0012_customuser_color_palette.py
accounts/0013_customuser_avatar.py
```

**This is what actually broke production on this push** — see the
"MUST be run manually" section above. `deploy.sh` does not run;
nothing does. Run `migrate --plan` then `migrate --noinput` from a
shell on the live app after every push to `main`, no exceptions.

## Environment variables

**None.** Everything here is either static or a user preference stored
in the database. `AEROESP_ENABLE_PWA=1` exists but is a local
development switch only — the service worker registers automatically
whenever `DEBUG` is off, and forcing it on in development would pin an
edited stylesheet to its cached copy.

## Manual steps

**Nothing required.** Both new preferences default to today's
behaviour: `color_palette` to the existing blue, and `avatar` to the
initial letter every account already showed.

Worth doing once after deploy: open the site on a phone in Chrome and
confirm the install prompt appears. Chrome's own installability audit
(`Page.getInstallabilityErrors`, persistent profile, running site)
reports zero errors, so this is a confirmation rather than a check.

## What the PWA caches, and what it refuses to

The worker stores `/static/` (content-hashed, so never stale) and the
four public pages — home, terms, and the help list and detail. Nothing
else, ever.

The rule lives on the server: `PublicPageCacheHeaderMiddleware` adds
`X-AeroESP-Cacheable: 1` only to anonymous GETs of those four views,
and the worker refuses to store any navigation without it. A service
worker cache is shared by everyone using the browser profile, so a
page stored while someone was signed in would be readable by whoever
opened the app next. Verified in a real browser: after visiting the
login page and the terms page, only `/` and `/terms/` were in the
cache.

Against staleness after deploy: cache names embed a build id derived
from the content-hashed precache URLs, `activate` deletes every cache
that is not current, `skipWaiting`/`clients.claim` hand over
immediately, and navigations are network-first — the cache is only
consulted when the network actually fails.

## Palettes

Five accents: Skyline (default, the existing blue, unchanged), Copper,
Indigo, Verdigris, Slate. A signed-in user's choice is a field on the
user and is rendered into `<html>` by the server, so it follows them
to any device with no flash of the default. Guests keep theirs in
`localStorage`.

Only six custom properties change per palette; everything else derives.
Contrast is solved numerically and asserted by parsing the shipped
stylesheet, so a palette added later with an eyeballed colour fails the
tests. `--theme-accent-strong` carries text and clears 4.5:1 in both
schemes; the gradient stops carry white labels and clear 4.5:1 against
white; `--theme-accent` is decorative only.

## The analysis page

New, at `/expert-review/analysis/`, **staff only**. Mean score across
the nine EVAL_V1 dimensions, and the Accept/Minor/Major/Reject split,
with the same numbers as a table underneath for the Methods section.

Reviewers are deliberately locked out: an aggregate mean and a decision
split are exactly the anchor that would pull their later judgements
toward the panel's. Nothing on the page touches provenance — it never
joins to `ResearchRun` or `ResearchExperiment`, and the tests assert
that across all three provenance values, over the view context, and
over the template source, since one `{{ ... .run.provider }}` would
undo the rest.

## Bugs found while building, all fixed

1. **`app.js` threw on every page load.** Two top-level IIFEs, and the
   sidebar handlers at the end of the second read `body`,
   `menuButton`, `sidebar` and `closeSidebar` from the first.
   `ReferenceError`, so Escape-to-close and the back/forward reset were
   dead. Invisible because the theme had already applied by then.
   Chrome confirmed it five times over; console is clean now.

2. **Multi-line `{# #}` is not a comment.** Django's lexer pattern is
   not DOTALL, so the text renders into the page. Two were live:
   approved teachers had a paragraph of explanatory prose in their
   sidebar, pending teachers another above "Signed in as". Both were
   mine, from round one, and the admin-only screenshot review never
   touched those pages.

3. **`collectstatic` was failing silently.** Chart.js ships a
   `sourceMappingURL` comment and the `.map` is not vendored;
   `ManifestStaticFilesStorage` treats that as a hard error. On a
   build/run split host that is a deploy where every stylesheet points
   at the previous build.

4. **The reviewer app never got the WebView fix.**
   `research_review/base.html` still carried the original unguarded
   theme bootstrap, so `0740fe0` never reached the reviewers. All
   three shells now share one include.

5. **A stylesheet link above the doctype** in `public_base.html`, which
   puts the document into quirks mode — worst for mobile layout.

6. **The AI comparison chart loaded Chart.js from an unpinned CDN.**
   Now self-hosted, and a test walks every template to keep it so.

7. **101 hardcoded accent literals** beyond the 64 found in the first
   pass. `#087eae` sat one character from the `#087fae` being searched
   for, inside a dark-mode `[class*="primary"]` catch-all with
   `!important`, and repainted every primary button blue whatever the
   palette was. The test is now a property, not a list.

## Still open

Everything in the previous "Known issues" section stands. Additionally:

- `CustomUser.profile_image` (an `ImageField`) exists on the model and
  is exposed nowhere — no form, no template, no admin. Avatar upload
  was deliberately not built; the dormant field is worth either using
  or removing.
- The palette picker is hidden in the topbar below 760px. The account
  centre carries the same controls at every width, which is the mobile
  path.
- Exam results (`exams/student/result.html`) still show a bare score
  and percentage. Charting them was not in scope.
