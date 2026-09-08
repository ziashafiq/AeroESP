# AeroESP - Handoff

**Date:** 2026-09-08
**Branch:** `main` (deployed) — `phase7-research-review` is identical
**Test suite:** 247 tests, all passing
(`python manage.py test --settings=config.test_settings`)

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

### 2. Migrations

Two new migrations, both metadata-only:

```
intelligence/0018_alter_aievaluationdataset_options_and_more.py
learning/0011_alter_learningprogress_options.py
```

`deploy.sh` runs `migrate --noinput`, so if Liara uses that script they
apply themselves. **Worth verifying** — `liara.json` uses the django
platform and does not explicitly name `deploy.sh`. If in doubt:

```
python manage.py migrate --noinput
```

Safe either way: `sqlmigrate` reports `(no-op)` for both. No schema
change, no data change.

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
