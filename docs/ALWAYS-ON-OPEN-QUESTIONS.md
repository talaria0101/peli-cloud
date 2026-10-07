# Open questions in the always-on free compute census

Each item is something the census could **not** settle. Each carries the route
that would close it and the date it was opened. Nothing here is a settled fact,
and nothing here is a reason to lower the bar.

Opened 2026-10-06. Third pass closed items 2, 3, 4 and 5 below.

## RESOLVED in the third pass — kept here so the reasoning is not lost

### hashbang (#!) — two real errors found and corrected

An earlier revision of this census said "no idle kill, no account-purge cron"
and "NO published RAM/CPU/disk quota". **Both were wrong.** The operator's own
deployed config, read directly from GitHub raw:

- `/etc/cron.daily/clean-lurkers` runs daily and, for any user with no SSH
  login in **30 days**, runs `loginctl terminate-user` — unless
  `/home/<user>/.keep-account` exists. It kills **processes**, not the account.
- `ansible/tasks/security/main.yml` applies `MemoryLimit=512M`, `CPUQuota=50%`,
  nproc 150/200 to every UID ≥ 1000 at login.

The purge is in `cron.daily/`, **not** the root `crontab`. A reader checking only
`/etc/crontab` gets a false negative — which is exactly what happened here. Row
moved T1 → **T2** with `.keep-account` as the keepalive.

### Ctrl-C.club — signups are CLOSED

`signup.ctrl-c.club` says verbatim: *"Signups are closed for now! ... You can
still submit a signup to get on a waitlist."* The apex page still carries a
stale 2023 "Signups are open!" banner, but the live MOTD is dated 2026-10-06 and
points at the current rules. So its T1 describes an **existing member's** box, not
a new user's. It also publishes a **5-year** inactivity archive — the most
generous policy in the census — and forbids Eggdrop bots and duplicate services.

### ModelScope — the "~5 free instances" figure is WITHDRAWN

Three research passes searched every first-party surface (official skills repo,
all Studio docs, `deploy_schema.json`, the i18n bundle) and found **no
per-account count anywhere**. A cap demonstrably exists; its value is never
published. Do not quote "5" from this project.

Also found: **modelscope.cn and modelscope.ai serve different free tiers** —
`2v-cpu-8g-mem` vs `2v-cpu-16g-mem`, both `resource_type=free`, both stable
across three runs. ModelScope's own docs and skills repo still hardcode 16g, so
the `.cn` endpoint may under-report what you actually receive.

### tilde.green — strengthened, quota found

The ToS lives on the **`wiki.tilde.green` subdomain**, which the first two passes
never probed. It publishes hard limits the census had recorded as unpublished:
50 processes, nice 10, 40 login limit, 1 GB soft / 1.5 GB hard storage. And the
operator's promise is the only positive no-idle-kill statement in the tildeverse:
*"we don't mind if you register and stay idle."*

## Still open

### 1. Northflank free-tier shape (not the card question)

**Settled:** a payment method is required for all users regardless of plan, per
Northflank's own billing docs — contradicting their pricing page and peli-cloud.

**Open:** the two pages disagree on the free-tier contents.

- pricing page — "2x free services / 1x free database / 2x free cron jobs"
- docs page — "2 services, 2 jobs, 1 addon, Up to 1 BYOC cluster"

Only matters if you want the database or the cron allowance. **Route:** sign up,
or ask support. **Re-open if** older than 60 days.

### 2. PythonAnywhere free tier

**UNVERIFIED and deliberately not counted.** `https://www.pythonanywhere.com/user/`
returns HTTP 404. **Route:** fetch `/pricing/` and read the free tier's RAM,
storage, CPU-second quota and idle policy. If bash + scheduled tasks survive, it
becomes T3.

### 3. Ctrl-C.club daemon policy scope

The Eggdrop/duplicate-service ban is verified. Whether a *generic* non-duplicate
background daemon is permitted is **not stated** on any reachable page
(`/rules` and `/about` both 404; the real rules are at `system_notice.html`).
**Route:** ask admin@ctrl-c.club.

### 4. Blinkenshell — filtered, not down, and still unprovisionable

Measured from a residential host on 2026-10-06: ports 80 and 443 open, HTTPS
returns 200 with 55 KB; ports 22, 2222 and 6697 all **silently time out**. The
host is alive and selectively filtered. **Route:** try from a different network or
a relay. Note the free tier still forbids listening ports (Supporter-only), so
even a successful connection gives you a tmux bot host, not an endpoint host.

### 5. No keepalive has actually been run

Every T2 keepalive is a mechanism read from vendor documentation. The closest
thing to measured evidence is the operator's own Tailscale deployment inside a
ModelScope Studio, which proves the transport works but not the 30-day threshold.

The load-bearing unknown is **Oracle**: the 7-day reclaim is defeated by >20%
sustained CPU or network, and nobody has confirmed a light cron survives it.

**Route:** stand up one Oracle A1 with a cron keepalive, leave it 14 days, check
whether the console ever reclaimed it.

### 6. Ingress was never completed

The probe read a **banner** from 8 hosts. No login was attempted, because no
account exists. A banner proves the host speaks SSH; it does not prove
credentials work, that signup is open, or that a free tier exists.

**Route:** create one T1 account and one T3 account, dial both from here.

### 7. tilde.zone is live but unattributed

The probe read `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4` — the **identical**
build string as tilde.town. Not counted as a free shell: a banner is not evidence
of a free tier, and no operator page was found. **Route:** find the operator, or
a signup path, on the host itself.

## Re-check cadence

The free-tier market turns over fast — Hugging Face moved CPU Spaces behind PRO
on 2026-07-21, and the launch base's Oracle figure was stale by 2×. Treat this as
a snapshot with a **90-day shelf life**. Re-run `python verify/fetch.py` and
`python verify/probe.py` after that.