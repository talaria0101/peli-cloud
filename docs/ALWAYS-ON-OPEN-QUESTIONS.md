# Open questions in the always-on free compute census

Each item is something the census could **not** settle. Each carries the route
that would close it and the date it was last checked. Nothing here is a settled
fact, and nothing here is a reason to lower the bar.

Opened 2026-10-06. Re-verified against the data at 940fb87 on 2026-10-07.

## RESOLVED in the third pass -- kept here so the reasoning is not lost

### hashbang (#!) -- two real errors found and corrected

An earlier revision of this census said "no idle kill, no account-purge cron"
and "NO published RAM/CPU/disk quota". **Both were wrong.** The operator's own
deployed config, read directly from GitHub raw:

- `/etc/cron.daily/clean-lurkers` runs daily and, for any user with no SSH
  login in **30 days**, runs `loginctl terminate-user` -- unless
  `/home/<user>/.keep-account` exists. It kills **processes**, not the account.
- `ansible/tasks/security/main.yml` applies `MemoryLimit=512M`, `CPUQuota=50%`,
  nproc 150/200 to every UID >= 1000 at login.

The purge is in `cron.daily/`, **not** the root `crontab`. A reader checking
only `/etc/crontab` gets a false negative -- which is exactly what happened
here. Row moved T1 -> **T2** with `.keep-account` as the keepalive.

### Ctrl-C.club -- signups are CLOSED

`signup.ctrl-c.club` says verbatim: *"Signups are closed for now! ... You can
still submit a signup to get on a waitlist."* The apex page still carries a
stale 2023 "Signups are open!" banner, but the live MOTD is dated 2026-10-06
and points at the current rules. So its T1 describes an **existing member's**
box, not a new user's. It also publishes a **5-year** inactivity archive -- the
most generous policy in the census -- and forbids Eggdrop bots and duplicate
services. That 5-year archive is why the row is now T2, not T1 (see the table
below).

### ModelScope -- the "~5 free instances" figure is WITHDRAWN

Three research passes searched every first-party surface (official skills repo,
all Studio docs, `deploy_schema.json`, the i18n bundle) and found **no
per-account count anywhere**. A cap demonstrably exists; its value is never
published. Do not quote "5" from this project. Item 3 below carries the
current state of that gap.

Also found: **modelscope.cn and modelscope.ai serve different free tiers** --
`2v-cpu-8g-mem` vs `2v-cpu-16g-mem`, both `resource_type=free`, both stable
across three runs. ModelScope's own docs and skills repo still hardcode 16g, so
the `.cn` endpoint may under-report what you actually receive.

### tilde.green -- strengthened, quota found

The ToS lives on the **`wiki.tilde.green`** subdomain, which the first two
passes never probed. It publishes hard limits the census had recorded as
unpublished: 50 processes, nice 10, 40 login limit, 1 GB soft / 1.5 GB hard
storage. And the operator's promise is the only positive no-idle-kill statement
in the tildeverse: *"we don't mind if you register and stay idle."*

## What the last pass changed, and what it left measured

Seven rows were re-tiered by `experiments/97-always-on-review-corrections.py`.
The counted total moved 22 -> 19.

| row | was | now | why |
| --- | --- | --- | --- |
| `azure-appservice-f1` | T2 | **UNVERIFIED** | its whole T2 claim was a 20-minute idle timeout its own `verified_by` said was absent from its own cited page |
| `neon-free` | T2 | **DEAD** | its own cited page prices an always-on database at ~182.5 CU-hours/month against a 100 CU-hour allowance |
| `sdf-free-shell` | T1 | **T2** | carries a 2-year login expiry and a keepalive, and T1 is defined as "no expiry" |
| `ctrl-c-club` | T1 | **T2** | archives accounts idle 5 years or more, which is an expiry |
| `hf-spaces-zerogpu` | T3 | **UNVERIFIED** | its own spec says 5 minutes of GPU per day, and a quota is not defeated by any relay |
| `pythonanywhere` | UNVERIFIED | **DEAD** | the vendor's own free-plan config sets `max_always_on_tasks` to 0 and `daily_cpu_limit_seconds` to 100 |

The last two were found by a deep review that attacked the guard rather than
reading the data: widening the quota-unit pattern to the per-day form it had
missed made two rows fail on their own text, and both failures were true.

Counts after the correction, from `python3 tools/check-always-on-free.py`
(exit 0): 40 rows, 19 counted, `DEAD=19 T1=5 T2=8 T3=6 UNVERIFIED=2`.

**How many rows carry no capture.** The census has 13 rows whose `verified_by`
quotes a byte count, in 15 byte-counted `(row, page)` pairs, and 23 rows
labelled `read` against 17 labelled `carried`. (Three further rows mention
"bytes" in prose without quoting a count, so a grep for the word gives 16 rather
than 13.) The two numbers below are both correct and it matters which one you
mean:

**16 rows are `carried` with no capture on disk.** That is what
`python3 tools/check-always-on-free-extended.py --mutate` reports as "16
honestly-carried rows checked for false failures, 0 failed one".

**13 of those 16 appear in a plain check run.** The other 4
(`pythonanywhere`, `cloudflare-containers`, `github-actions`,
`inference-apis`) carry no quote at all, so there is nothing to check. The 13:
`alwaysdata-free`, `aws-free-tier`, `azure-free-account`, `browser-linux`,
`fly-io`, `hf-dev-mode`, `killercoda`, `modal-sandbox`, `play-with-docker`,
`railway-free-vm`, `replit-free`, `sdf-free-shell`, `tilde-guru`. Four of those
hold 16 notes between them, which is why a check run prints 16 notes covering
13 distinct rows.

These rows are reported and exit 0 by design. Failing them would be
indistinguishable from failing a fabricated quote, and the one thing the guard
must not do is train a reader to ignore it.

## Still open

### 1. `azure-appservice-f1`: the 20-minute idle timeout has no first-party page

The row is UNVERIFIED and not counted. The part that is confirmed is the F1
resource line, read from the fetch at
`verify/pages/azure_appservice_linux.html`: `F1 Free Shared (60 CPU minutes /
day) 1 GB 1.00 GB $-`, HTTP 200, 826190 bytes. That correction stands and is
the one that matters: the 512 MB / 5 GB F1 figures repeated in every older guide
are obsolete, and the current vendor table says 1 GB RAM / 1.00 GB storage.

What is NOT settled is the idle timeout. **The 20-minute figure is currently
unattributed.** The census attributes it to "Microsoft's WebJobs docs per a
research pass" and I could not confirm it on any page:

- The cited F1 pricing capture contains **zero** occurrences of "Always On",
  "idle" or "20 min", so the figure is not on the page the row cites. That is
  what the row itself now says.
- `azure-functions/functions-scale` (HTTP 200, 86409 bytes) mentions an idle
  timeout once and it is Azure Load Balancer's, not a 20-minute App Service
  limit.
- Every other App Service documentation URL I tried returned HTTP 404.

**Route:** find the Microsoft page that carries the 20-minute figure, capture it
under `verify/fetch.py`, and read the number off those bytes. If it says F1
sleeps in 20 minutes the row returns to T2 with a captured citation. **Do not**
promote it back on the strength of this document: the number has to come off a
page, not off a note saying it exists somewhere.

**Unknown:** which Microsoft page carries the figure. I am not naming one
because I did not find it, and an invented URL is worse than a recorded gap.
**Re-check by 2026-11-07.**

### 2. Byte counts in `verified_by` drift, so what is the right cadence?

Every row that quotes a byte count is making a claim a reader can check by
re-fetching. I re-fetched all 15 byte-counted pages from this host on
2026-10-07, three runs each. The counts are not stable:

- **5 pages return different lengths on different runs of the same URL**:
  `oracle_alwaysfree` (53761 / 53867), `northflank_pricing` (193710 / 193712),
  `render_free` (388426 / 388469 / 388512), `azure_appservice_linux` (826176 /
  826190), `google_cloud_shell` (139429 / 139433).
- **4 pages never reproduce the recorded number**, stably, across runs:
  `gcp_free` (recorded 181337, live 181341), `northflank_docs_billing` (346968
  vs 346329), `hf_spaces_overview` (222896 vs 222975), `hf_spaces_gpus` (221818
  vs 221897).
- **5 on-disk captures do not match the number written next to them**:
  `northflank_docs_billing`, `render_free`, `hf_spaces_overview`,
  `hf_spaces_gpus`, `google_cloud_shell`.

The last group is a defect rather than drift: a capture on disk whose size
disagrees with the recorded figure means the figure was typed from a different
fetch than the file that shipped. The others are vendor-side noise and are not
evidence that the quote is wrong.

**What this does not establish:** none of these measurements say any quote
changed. Quote fidelity is a separate check and it passes --
`python3 tools/check-always-on-free.py` and
`python3 tools/check-always-on-free-extended.py` both exit 0, the latter tracing
all 33 captured quotes verbatim, by table reconstruction, by elision or
whitespace-folded.

**Route:** settle the cadence, then make it a clause rather than prose. The
option this file recommends is a guard check comparing each `verified_by` byte
count against its capture on disk, so a typed figure that disagrees with the
shipped file fails instead of waiting for a human to notice.

**Unknown:** the right interval. The 90-day cadence at the bottom of this file
is a guess about vendor content, and I have no measurement of how often these
figures are *wrong* as opposed to merely noisy, because one re-fetch cannot
separate the two. **Re-check by 2026-11-07.**

### 3. ModelScope: the per-account Studio cap is still unpublished

The "~5 free instances" figure is withdrawn as unsourced. That withdrawal
stands.

I re-fetched both unauthenticated hardware APIs on 2026-10-07 and the cap is
still not there. Each response is a `hardware` list and nothing else:
`modelscope.cn` returns `{"success":true,"request_id":...,"data":{"hardware":
[{"name":"platform/2v-cpu-8g-mem","resource_type":"free",...}]}}` (HTTP 200, 210
bytes) and `modelscope.ai` the same shape with `platform/2v-cpu-16g-mem`
(HTTP 200, 211 bytes). The top-level keys are `success`, `request_id`, `data`,
and `data` has exactly one key, `hardware`. **There is no quota field to read.**

**What is established:** a free Studio exists and some cap exists. **What is
not:** its value.

**Route:** the cap would have to come from an authenticated endpoint or a page
that does not exist yet. Three passes searched the official skills repo, all
Studio docs, `deploy_schema.json` and the i18n bundle. **Unknown:** whether
ModelScope will publish it at all, so this carries no re-check date and is a
standing gap rather than a scheduled one. If an authenticated response ever
shows a quota field, capture that response and record the field name.

### 4. Blinkenshell: the table was cited to the wrong page, and the guard cannot catch that

The deepest item here, because the fix that shipped does not prevent a third
occurrence.

**What happened.** The row claimed it had "parsed the wiki's feature-comparison
TABLE CELL BY CELL". It had not. The wiki root carries **zero** `<table>`
elements (`verify/pages/blinkenshell_wiki.html`, 61651 bytes), and the quoted
text `Disk Quota 100 MB (x4~) | Memory limit 128 MB | ...` appears in **no**
capture in `verify/pages/`. The Free/Supporter table is on
`/docs/resource-limits/`, the one page with a `<table>` in it.

**How many revisions carried it.** The wrong attribution to
`https://blinkenshell.org/wiki/` is present in `fb3aa27`, `8543d14` and
`d83f415`, and corrected in `940fb87`. `fb3aa27` and `8543d14` are on branch
`pr1` and are **not** ancestors of `HEAD`, so this was fixed once on the merged
branch and a stale copy of the wrong row still exists on `pr1`.

**Why it survived, measured.** I tested the current guard against the exact
defect:

- Put the historical uncaptured quote back and cite the wiki root: **caught**.
  `tools/check-always-on-free-extended.py` fails it with `blinkenshell.quote:
  quote is not traceable to any capture in verify/pages/ (checked 33 captures:
  verbatim, ' | ' table reconstruction, ' ... ' elision, whitespace-folded)`.
- Keep a quote that genuinely is in a capture but re-point the row's `source`
  and `verified_by` at the **wrong** page: **not caught**, zero failures.

That second result is the open question. The guard asks "is this quote in
*some* capture?" and never asks "is it in the capture **this row names**?". A
mis-citation between two pages that both have captures is invisible to it, and
that is the shape of the error that ran for two revisions. The corrected row
escapes only because a human re-read the pages.

**Route:** add a clause resolving each quote against the capture its own
`verified_by` names, not against the union. That is the structural fix; a
reviewer reading carefully is the current mitigation and it has already failed
twice. **Unknown:** whether any other row mis-cites between pages that both
have captures. I did not audit all 40 rows for it and the guard cannot answer
it. **Re-check by 2026-11-07.**

### 5. Northflank free-tier shape (not the card question)

**Settled:** a payment method is required for all users regardless of plan, per
Northflank's own billing docs, contradicting their pricing page and the launch
base.

**Open:** the two pages disagree on the free-tier contents.

- pricing page -- "2x free services / 1x free database / 2x free cron jobs"
- docs page -- "2 services, 2 jobs, 1 addon, Up to 1 BYOC cluster"

Only matters if you want the database or the cron allowance. **Route:** sign up,
or ask support. **Re-open if older than 60 days.**

### 6. Ctrl-C.club daemon policy scope

The Eggdrop/duplicate-service ban is verified. Whether a *generic*
non-duplicate background daemon is permitted is **not stated** on any reachable
page (`/rules` and `/about` both 404; the real rules are at
`system_notice_long.html`). Signups are **closed**, waitlist only, so this is an
existing member's question. **Route:** ask admin@ctrl-c.club.
**Re-check by 2026-11-07.**

### 7. Blinkenshell is filtered, not down, and still unprovisionable

Measured from a residential host on 2026-10-06: ports 80 and 443 open, HTTPS
returns 200; ports 22, 2222 and 6697 all **silently time out**. The host is
alive and selectively filtered. **Route:** try from a different network or a
relay. The free tier still forbids listening ports (Supporter-only), so even a
successful connection gives a tmux bot host, not an endpoint host.

### 8. No keepalive has actually been run

Every T2 keepalive is a mechanism read from vendor documentation. The closest
thing to measured evidence is the operator's own Tailscale deployment inside a
ModelScope Studio, which proves the transport works but not the 30-day
threshold.

The load-bearing unknown is **Oracle**: the 7-day reclaim is defeated by >20%
sustained CPU or network, and nobody has confirmed a light cron survives it.

**Route:** stand up one Oracle A1 with a cron keepalive, leave it 14 days, check
whether the console ever reclaimed it. **Re-check by 2026-11-07.**

### 9. Ingress was never completed

The probe read a **banner** from 9 endpoints, which is 9 hostnames but 8
distinct operators: `sdf.org` and `freeshell.org` are the same host under two
names. No login was attempted, because no account exists. A banner proves the host speaks SSH; it does not prove
credentials work, that signup is open, or that a free tier exists.

**Route:** create one T1 account and one T3 account, dial both from here.

### 10. tilde.zone is live but unattributed

The probe read `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4` -- the **identical**
build string as tilde.town. Not counted as a free shell: a banner is not
evidence of a free tier, and no operator page was found. **Route:** find the
operator, or a signup path, on the host itself.

### 11. `sdf.org` was unreachable once, and the limitation has been withdrawn

**Resolved 2026-10-07. Nothing is open here.** An earlier revision recorded
`sdf_members01` and `sdf_members05` in `verify/fetch.py`'s
`KNOWN_UNREACHABLE` set on the strength of a single 502/504 pair, and this
section carried the limitation forward as fact.

Three consecutive fetches minutes later returned HTTP 200 for both pages (7860
and 2972 bytes, byte-identical each run), both quotes are verbatim in the
fetched bytes, and with all 35 captures present:

- `python3 verify/fetch.py` -> `35/35 fetched`, exit 0
- `python3 verify/claim.py` -> `68 hit, 0 miss, 0 pages with no capture`, exit 0
- `python3 verify/fetch.py --check` -> `35 claims, 35 captures`, exit 0

`KNOWN_UNREACHABLE` is now empty on purpose. A transient failure recorded as a
standing limitation outlives its cause and is inherited by a later session as
current; here it also marked two verifiable rows unverifiable on every host that
could verify them.

**Route to reopen:** if a fetch fails, read the status and body before writing
down why. Nothing here is a property of any host class.

### 12. PythonAnywhere: settled on first-party evidence, and it is DEAD

**Closed 2026-10-07.** The earlier route was to fetch `/pricing/`, because
`/user/` returns HTTP 404 and the row had no bytes at all. `/pricing/` is HTTP
200, and the free plan appears there twice: as a visible plan-builder page, and
as a JSON config the page embeds.

The config is the machine-readable half, and it is unambiguous:

    "free": {"daily_cpu_limit_seconds": 100, "disk_space_gb": 0.5,
             "max_webapps": 1, "uwsgi_workers": 1,
             "max_always_on_tasks": 0, "postgres_enabled": false,
             "postgres_disk_space_gb": 1}

Two of those numbers decide the row. `max_always_on_tasks` is **0**, so there
are no scheduled or always-on tasks to schedule, and the census row's claim that
"scheduled tasks are the supported persistence mechanism" was contradicted by the
vendor's own data. `daily_cpu_limit_seconds` is **100**, a daily budget that will
not hold a node up, and a quota is a wall no relay defeats. The row is DEAD.

Captured as `verify/pages/pythonanywhere_pricing.html`, with four visible
phrases in `verify/claims.json`. The two figures above are **not** in that
phrase list, and the reason is worth recording: the config lives inside a
`<script>` block, which `verify/claim.py` strips on purpose because script
contents are not rendered text. A quotation drawn from a script blob would be a
quotation of something a reader cannot see on the page. They are machine-readable
data and are labelled as such rather than smuggled in as prose.

**Unknown:** whether the browser console itself persists between sessions with no
scheduled task. That is the one thing the config does not answer, and it does not
change the verdict - 100 CPU-seconds a day is the wall either way.

## Found while checking, now fixed

Both of these were reported by a deep review and both were fixed in
`58f88a1` and the commit after it. They are kept here because a reader
comparing this file against an older revision will hit them.

- **`tools/check-always-on-free-extended.py`'s worked example was stale.** Its
  docstring said `neon-free is counted T2 today`, which was true when written and
  wrong after the correction. Corrected, along with the oracle example that
  claimed the row failed its quota clause when it fits (1,488 against 1,500
  OCPU-h), and three places that still said 17 DEAD rows when there are 19.

- **A quoted limitation outlived its cause.** `sdf.org` was recorded as
  unreachable from one 502/504 pair and the note was carried forward as fact by
  three files at once. See section 11.

- **`tools/check-all.py` described the withdrawn sdf limitation in its own
  docstring**, quoting a `KNOWN_UNREACHABLE` entry that no longer exists. A
  reader debugging a capture failure would have been sent after a cause that had
  been disproved.
