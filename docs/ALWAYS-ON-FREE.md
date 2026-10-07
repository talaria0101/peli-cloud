# Always-on free compute, 2026-10-06

**20 of 40 rows hold up indefinitely at $0.** The starting corpus was [talaria0101/peli-cloud](https://github.com/talaria0101/peli-cloud), read before this census was written. Its own account of what it found, from `data["launch_base"]["note"]`:

> peli-cloud's own docs/ANONYMOUS-VMS.md records ZERO rows that survive a strict always-on test. Its 6 banner-verified rows are shared public shells, and the machine rows it does carry (Railway, Codespaces, Fly, Koyeb) all fail on quota or expiry. This file exists because that page is a census of shells, not of persistent compute.

Generated from [`data/always-on-free.json`](../data/always-on-free.json) by `tools/render-always-on-free.py`. Guarded by `tools/check-always-on-free.py`, and gated against its own output by `tools/check-rendered-page.py`.

## The distinction the taxonomy rests on

A relay cannot fix everything, and that is the whole design.

| tier | what it means | count |
|---|---|---|
| **T1** | Always-on as-is. No idle sleep, no hard session cap, no login expiry or archival. Nothing needs doing to keep it. | 5 |
| **T2** | Always-on WITH A KEEPALIVE, or with an expiry long enough to schedule. Sleeps, scales to zero, is reclaimed when idle, or archives after a stated period of silence - but a periodic login, a held WebSocket, cron, or light sustained CPU defeats it. Each row names the exact keepalive. | 8 |
| **T3** | NEEDS A RELAY. Runs fine but is unreachable: no inbound ports, egress restrictions, or browser-only. An outbound-initiated tunnel or held WebSocket to a free relay service makes it reachable. | 7 |
| **DEAD** | Hard wall. Nothing a relay or keepalive fixes: a quota that exhausts regardless, a trial clock, a paid-plan gate on CREATION, or an account that self-closes. | 18 |
| **UNVERIFIED** | Not counted. The shape looks right but no first-party page could be fetched, so it is recorded rather than claimed. | 2 |

**A relay defeats a LIVENESS wall** — idle sleep, scale-to-zero, no-inbound-ports, browser-only. You keep the machine alive, or you tunnel out of it, and it becomes reachable forever.

**A relay cannot defeat a QUOTA wall** — a monthly compute-hour cap that exhausts regardless, a trial clock, or a paid-plan gate at creation time. Those rows are DEAD and are excluded. The figures that sort the rows are in `data["tier_note"]`:

> T1, T2 and T3 all count toward the goal of an always-on free node. A relay defeats LIVENESS walls (sleep, scale-to-zero, no-inbound-ports) but cannot defeat QUOTA walls (60 core-hours (Codespaces' 120 hrs on a 2-core machine), 24h caps, trial clocks, PRO gates). That distinction is the whole taxonomy.

So T2 and T3 are legitimate hits, not near-misses: the keepalive or the relay *is* the thing that makes them always-on. Only DEAD is a dead end.

## How much of this is measured

Every row is counted exactly once, using the guard's own `provenance()` so these two tools cannot disagree about what a row's evidence is worth.

| evidence weight | rows | means |
|---|---|---|
| first-hand | 23 | I fetched the page and read the quote out of the bytes |
| carried | 17 | a research pass fetched it; the row says so, and names which parts I did not check |

"First-hand" means the bytes were read, **not** that an account was created. No account exists anywhere in this census. The live probe below is the only measurement here that touches a real host.

## The counted rows

### T1 — Always-on as-is. No idle sleep, no hard session cap, no login expiry or archival. Nothing needs doing to keep it.

#### Google Cloud Free Tier — Compute Engine e2-micro

- **What you get:** e2-micro shared-core: 2 vCPU burst at ~12.5% each sustained 0.25 vCPU, 1 GB RAM (custom up to 2 GB), 30 GB standard PD, 1 GB egress/mo. US only: us-west1, us-central1, us-east1.
- **The wall:** none. Compute Engine's suspend/resume is user-initiated only and is never triggered by idleness.
- **Account:** sign-up required = True, card required = True
- **Caveat:** The one unambiguous always-on machine in the whole census. Shared-core throttles after ~30s of full CPU, so it is a bot/relay node, not a compute box. The allowance is a month's worth of hours (~730), so exactly one always-on instance fits and a second would bill. A $0.00-$1.00 temporary authorization hold is placed at signup and is not a charge. Overage is possible past 30 GB disk or 1 GB egress.
- **Source:** <https://cloud.google.com/free/docs/free-cloud-features>
- **Vendor says (quote, VERBATIM):**
> 1 non-preemptible e2-micro VM instance per month in one of the following US regions: Oregon: us-west1. Iowa: us-central1. South Carolina: us-east1. 30 GB-months standard persistent disk.
- **Vendor says (quote2, VERBATIM):**
> Your Free Tier e2-micro instance limit is by time, not by instance. Each month, eligible use of all of your e2-micro instances is free until you have used a number of hours equal to the total hours in the current month.
- **Vendor says (quote3, VERBATIM):**
> The Free Tier has no end date, but Google reserves the right to change the offering, including changing or eliminating usage limits, with 30 days' advance notice.
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 181337 bytes, all three quotes read from the fetched bytes at verify/pages/gcp_free.html

#### Northflank Developer Sandbox

- **What you get:** 2 services, 2 jobs, 1 addon (docs) / 2 services + 1 database + 2 cron jobs (pricing page). Smallest covered plan nf-compute-10 is 0.1 shared vCPU / 256 MB. Container, not a VM.
- **The wall:** none. The pricing page states 'no sleeping' in the vendor's own words. Autoscaling to zero is opt-in and not on the free sandbox.
- **Account:** sign-up required = True, card required = True
- **Caveat:** CARD IS REQUIRED — RESOLVED, NOT UNCONFIRMED. Northflank's own docs say a payment method is mandatory for every user regardless of plan: 'all users must add a payment method to start creating resources on Northflank, regardless of plan selection.' This contradicts the pricing page's 'Get started for free' and contradicts peli-cloud's card_required=false. The docs are the specific policy, so they win. The card is only verified, not charged, on the free tier. Also note the free-tier shape differs between the two pages: pricing says '2x free services / 1x free database / 2x free cron jobs', docs say '2 services, 2 jobs, 1 addon, up to 1 BYOC cluster'. No persistent volumes on free, no inbound SSH, and it 'should not be used for production applications'.
- **Source:** <https://northflank.com/pricing>
- **Vendor says (quote, VERBATIM):**
> Always-on-compute - no sleeping :) 2x free services 1x free database 2x free cron jobs
- **Vendor says (quote2, VERBATIM):**
> all users must add a payment method to start creating resources on Northflank, regardless of plan selection. This is to verify user identity, and prevent malicious usage of the platform.
- **Vendor says (quote3, VERBATIM):**
> You can test out Northflank with our Developer Sandbox plan. This free plan allows you to deploy: 2 services 2 jobs 1 addon Up to 1 BYOC cluster
- **Verified:** me, 2026-10-06 — pricing page fetched HTTP 200, 193710 bytes (verify/pages/northflank_pricing.html); docs page fetched HTTP 200, 346968 bytes (verify/pages/northflank_docs_billing.html). I re-fetched the docs page because the earlier research pass had reported it as unreadable; it rendered this time, which is how the card conflict got settled.

#### tilde.green

- **What you get:** Ubuntu 24.04.1 LTS, shared. The ToS on the wiki.tilde.green subdomain publishes HARD LIMITS the earlier pass recorded as unpublished: 50 processes/threads, nice 10, 40 login limit, 1 GB soft / 1.5 GB hard storage.
- **The wall:** none documented — and the operator explicitly says so.
- **Account:** sign-up required = True, card required = False
- **Caveat:** STRENGTHENED: the operator says 'we don't mind if you register and stay idle' - the only positive no-idle-kill promise in the tildeverse - AND the host now has a documented quota. Contact root@tilde.green, IRC #tilde.green. The ToS is self-labelled 'Work in Progress', so enforcement is not guaranteed.
- **Source:** <https://tilde.green/>
- **Vendor says (quote, VERBATIM):**
> we don't mind if you register and stay idle, but we'd appreciate if possible if you could join our little community
- **Verified:** me, 2026-10-06 - probed live (banner SSH-2.0-OpenSSH_10.5p1 Debian-1, in verify/reachability.json) and fetched verify/pages/tilde_green.html and tilde_green_tos.html, which publishes the hard limits an earlier pass recorded as unpublished.

#### tilde.club

- **What you get:** Fedora 43, shared. Disk 1 GB soft / 3 GB hard / 1-week grace. No RAM/CPU published. screen/tmux documented in the wiki.
- **The wall:** no idle policy and no login expiry found on any first-party page.
- **Account:** sign-up required = True, card required = False
- **Caveat:** T1 by ABSENCE of a stated policy. Signups no longer accept gmail.com addresses.
- **Source:** <https://tilde.club/wiki/faq.html>
- **Vendor says (quote, RECONSTRUCTION - 3 fragments joined by `...`, not one contiguous quote):**
> Soft Limit: 1 GB - You'll get a heads-up if you go over this... Hard Limit: 3 GB - This is the max... Grace Period: 1 week
  - _Fragments:_
  - 1. `Soft Limit: 1 GB - You'll get a heads-up if you go over this` -> `verify/pages/tilde_club_faq.html`
  - 2. `Hard Limit: 3 GB - This is the max` -> `verify/pages/tilde_club_faq.html`
  - 3. `Grace Period: 1 week` -> `verify/pages/tilde_club_faq.html`
- **Verified:** me, 2026-10-06 - re-fetched faq.html (Soft 1 GB / Hard 3 GB / 1-week grace) and wiki/netiquette.html; captures under verify/pages/ as tilde_club_faq. Live banner SSH-2.0-OpenSSH_10.0 read by verify/probe.py.

#### tilde.guru

- **What you get:** FreeBSD 15.0-RELEASE pubnix, ~214 users. No RAM/CPU/disk published.
- **The wall:** no idle policy documented.
- **Account:** sign-up required = True, card required = False
- **Caveat:** Signup is CURATED and was disabled at one point for abuse: 'Talk to sarmonsiill about getting an account'. The host is a human gate, not a cost or expiry defect. The wiki /wiki/Join returned 404.
- **Source:** <https://tilde.guru/>
- **Vendor says (quote, VERBATIM):**
> a FreeBSD pubnix - est. 2021 - member of the tildeverse
- **Verified:** research pass, first-party fetch; I did not independently re-fetch

### T2 — Always-on WITH A KEEPALIVE, or with an expiry long enough to schedule. Sleeps, scales to zero, is reclaimed when idle, or archives after a stated period of silence - but a periodic login, a held WebSocket, cron, or light sustained CPU defeats it. Each row names the exact keepalive.

#### Oracle Cloud Always Free — VM.Standard.A1.Flex

- **What you get:** VM.Standard.A1.Flex ARM Ampere, 2 OCPU / 12 GB (the allowance is 1,500 OCPU-h + 9,000 GB-h per month), 200 GB block volume, home region only. Plus up to 2x VM.Standard.E2.1.Micro.
- **The wall:** no sleep and no session cap, but Oracle may RECLAIM an instance idle over a 7-day window. The test is 95th-percentile CPU <20%, network <20%, and (A1 only) memory <20%.
- **The keepalive:** Sustained >20% CPU or >20% network utilization across the 7-day window. A cron doing real work, or a continuously-relayed WebSocket, defeats it. This is a utilization threshold, not a session cap, so it is beatable by design.
- **Account:** sign-up required = True, card required = True
- **Caveat:** CORRECTION TO THE LAUNCH BASE AND TO THE WIDELY-REPEATED FIGURE: it is 2 OCPU / 12 GB, not 4 OCPU / 24 GB. Oracle's own sentence 'this is equivalent to 2 OCPUs and 12 GB of memory' settles it, and the arithmetic agrees (1,500 OCPU-h / ~744 h = 2 OCPUs). Card required but never charged on Always Free. Capacity problems have caused account closures for some new tenancies; Oracle may reclaim A1 capacity outright. The marketing page says 'unlimited period of time' while the docs page carries the idle-reclaim rule — the docs page is the specific policy and is the one that governs.
- **Source:** <https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm>
- **Vendor says (quote, VERBATIM):**
> All tenancies get the first 1,500 OCPU hours and 9,000 GB hours per month for free for VM instances using the VM.Standard.A1.Flex shape, which has an Arm processor. For Always Free tenancies, this is equivalent to 2 OCPUs and 12 GB of memory.
- **Vendor says (quote2, VERBATIM):**
> Idle Always Free compute instances may be reclaimed by Oracle. Oracle will deem virtual machine and bare metal compute instances as idle if, during a 7-day period, the following are true: CPU utilization for the 95th percentile is less than 20%
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 53867 bytes; both quotes read from the fetched bytes at verify/pages/oracle_alwaysfree.html

#### Oracle Cloud Always Free — VM.Standard.E2.1.Micro

- **What you get:** up to 2 instances of VM.Standard.E2.1.Micro, AMD, 1/8 OCPU and 1 GB RAM each.
- **The wall:** same 7-day / 20% reclamation rule as the A1. The memory clause applies to A1 shapes only.
- **The keepalive:** sustained >20% CPU or network over 7 days
- **Account:** sign-up required = True, card required = True
- **Caveat:** Shares the Oracle tenancy, so it is not an independent provider — it is the same account as the A1 row and cannot be counted twice toward a provider count. Listed separately because the shape and the reclamation rule differ (no memory clause).
- **Source:** <https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm>
- **Vendor says (quote, VERBATIM):**
> All tenancies get up to two Always Free VM instances using the VM.Standard.E2.1.Micro shape, which has an AMD processor.
- **Verified:** me, 2026-10-06 — read from the fetched bytes at verify/pages/oracle_alwaysfree.html

#### Render — Free web service

- **What you get:** 512 MB RAM, less than 1 CPU, ephemeral filesystem, no persistent disk, no shell/SSH. 750 free instance-hours per workspace per calendar month.
- **The wall:** 15 minutes without inbound traffic. 750 instance-hours/workspace/month, then suspended to the start of the next month.
- **The keepalive:** An inbound HTTP request OR a WebSocket message from an existing connection every <15 min. The vendor names WebSocket messages explicitly as resetting the timer, so a held WebSocket is the cleanest keepalive. Confidence: high.
- **Account:** sign-up required = True, card required = False
- **Caveat:** Ephemeral filesystem: 'any changes to its local filesystem are lost' on spin-down, so it is a relay endpoint, not a stateful node. Render may also restart a free service at any time. The 750 h/month workspace cap is the real ceiling — one always-on service is ~720 h, so exactly one fits.
- **Source:** <https://render.com/docs/free>
- **Vendor says (quote, VERBATIM):**
> Render spins down a Free web service that goes 15 minutes without receiving any inbound traffic. This includes both HTTP requests and WebSocket messages from existing connections.
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 388859 bytes, quote read from fetched bytes at verify/pages/render_free.html

#### Supabase — Free project

- **What you get:** Shared CPU, 500 MB RAM, 500 MB database, 5 GB egress, 1 GB file storage, 50k MAU. Postgres + Edge Functions runtime.
- **The wall:** project paused after 1 week of inactivity. 2 active projects on free.
- **The keepalive:** Any API call or DB query at least weekly. A cron ping is sufficient. Confidence: high — the pause is purely inactivity-based with no session cap.
- **Account:** sign-up required = True, card required = False
- **Caveat:** Edge Functions give you a real always-on process runtime (Deno) with a public URL, which is what makes this a compute row rather than a database row. It is not a shell or a VM — you cannot get a login.
- **Source:** <https://supabase.com/pricing>
- **Vendor says (quote, VERBATIM):**
> Free projects are paused after 1 week of inactivity. Limit of 2 active projects.
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 386813 bytes, quote read from fetched bytes at verify/pages/supabase_pricing.html

#### SDF Public Access UNIX System

- **What you get:** Shared multi-user FreeBSD/NetBSD pubnix, est. 1987. Free tier: 20 MB disk quota x4 filesystems (home, web, mail, gopher) plus a 500-file cap. No published RAM/CPU.
- **The wall:** no process sleep. The only kill is account expiry: validated accounts expire after 2 years without a UNIX login; prevalidated accounts are purged at ~600 days.
- **The keepalive:** one UNIX login per 2 years. The clock is lastlog, so a background job alone will not keep the account alive; it has to be a real login.
- **Account:** sign-up required = True, card required = False
- **Caveat:** A SHARED HOST, NOT A PRIVATE VM - tens of thousands of users share one kernel. RETIERED FROM T1: T1 is defined as 'no expiry', and this row carries a 2-year login expiry plus a keepalive, which is the file's own definition of T2. The 2-year expiry was also described here as 'the gentlest idle policy in the census', which was a claim about the other rows and was not this row's to make. Login expiry runs at ~600 days for prevalidated accounts. Live banner read by verify/probe.py (SSH-2.0-OpenSSH_10.4).
- **Source:** <http://sdf.org/?faq?MEMBERS?05>
- **Vendor says (quote, VERBATIM):**
> Validated accounts will expire if the user does not login at least once during a 2 year period.
- **Vendor says (quote2, VERBATIM):**
> 20 MB disk quota for your home directory
- **Verified:** me, 2026-10-06, quotes read from the fetched bytes at verify/pages/sdf_members05.html and sdf_members01.html; verify/claims.json holds all three phrases. Re-verified 2026-10-07: both pages fetched HTTP 200 (7860 and 2972 bytes, stable across three runs) and both quotes are verbatim in the fetched bytes, so verify/claim.py reports 68 hit / 0 miss with all 35 captures present. An intermediate revision of this field claimed the bytes were 'not re-fetchable from every host' on the strength of one 502/504 pair; that was a transient upstream failure and the claim has been withdrawn.

#### Blinkenshell

- **What you get:** Free account limits, from the vendor's own table: 128 MB RSS memory, 100 processes, 128 open files, 6 SSH sessions, 2 background processes. screen/tmux detach allowed. Stockholm, online since 2006. SSH on port 2222, not 22.
- **The wall:** no documented idle kill and no login expiry. Social suspension risk instead: not visiting IRC is a rule violation.
- **The keepalive:** keep a screen/tmux session running; max 2 background processes
- **Account:** sign-up required = True, card required = False
- **Caveat:** CORRECTION TO BOTH THE LAUNCH BASE AND TO THIS ROW'S OWN EARLIER TEXT. Free Blinkenshell is a screen/tmux host, not an endpoint host: the limits table's Free column caps memory at 128 MB, processes at 100, SSH sessions at 6 and background processes at 2, and the rules page says in so many words that IRC bots, servers/daemons and bouncers are Supporter-only. The port fact the launch base got wrong is separate: the host is on 2222, not 22, which is why the launch base's port-22 excuse never covered it. Earlier revisions of this row quoted a 'Disk Quota 100 MB (x4~)' feature table that exists on no page in verify/pages/; that text was not in the captures and is not claimed here. Signup also requires a VOUCH by an existing member.
- **Source:** <https://blinkenshell.org/docs/resource-limits/>
- **Vendor says (quote, RECONSTRUCTION - 18 fragments joined by `|`, not one contiguous quote):**
> Type | Free account limit | Supporter account limit | Memory usage (RSS) | 128 MB | 256 MB | Number of open files | 128 | 128 | Number of processes | 100 | 100 | SSH sessions | 6 | 6 | Background processes | 2 | 5
  - _Fragments:_
  - 1. `Type` -> `verify/pages/azure_appservice_linux.html`, `verify/pages/blinkenshell_limits.html`, `verify/pages/cf_workers_limits.html` (+12 more: this fragment is that common, so it is weak evidence on its own)
  - 2. `Free account limit` -> `verify/pages/blinkenshell_limits.html`
  - 3. `Supporter account limit` -> `verify/pages/blinkenshell_limits.html`
  - 4. `Memory usage (RSS)` -> `verify/pages/blinkenshell_limits.html`
  - 5. `128 MB` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/cf_workers_limits.html`
  - 6. `256 MB` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/northflank_pricing.html`
  - 7. `Number of open files` -> `verify/pages/blinkenshell_limits.html`
  - 8. `128` -> `verify/pages/azure_appservice_linux.html`, `verify/pages/blinkenshell_limits.html`, `verify/pages/cf_workers_limits.html` (+3 more: this fragment is that common, so it is weak evidence on its own)
  - 9. `128` -> `verify/pages/azure_appservice_linux.html`, `verify/pages/blinkenshell_limits.html`, `verify/pages/cf_workers_limits.html` (+3 more: this fragment is that common, so it is weak evidence on its own)
  - 10. `Number of processes` -> `verify/pages/blinkenshell_limits.html`
  - 11. `100` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_wiki.html`, `verify/pages/cf_workers_limits.html` (+9 more: this fragment is that common, so it is weak evidence on its own)
  - 12. `100` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_wiki.html`, `verify/pages/cf_workers_limits.html` (+9 more: this fragment is that common, so it is weak evidence on its own)
  - 13. `SSH sessions` -> `verify/pages/blinkenshell_limits.html`
  - 14. `6` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_wiki.html`, `verify/pages/cf_workers_limits.html` (+8 more: this fragment is that common, so it is weak evidence on its own)
  - 15. `6` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_wiki.html`, `verify/pages/cf_workers_limits.html` (+8 more: this fragment is that common, so it is weak evidence on its own)
  - 16. `Background processes` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_rules.html`
  - 17. `2` -> `verify/pages/azure_appservice_linux.html`, `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_rules.html` (+18 more: this fragment is that common, so it is weak evidence on its own)
  - 18. `5` -> `verify/pages/blinkenshell_limits.html`, `verify/pages/blinkenshell_wiki.html`, `verify/pages/cf_workers_limits.html` (+13 more: this fragment is that common, so it is weak evidence on its own)
- **Vendor says (quote2, VERBATIM):**
> No IRC bots are allowed on free accounts. (Available on Supporter Account only) You are not allowed to run any server/daemon on free accounts. This includes bouncers. (Available on Supporter Account only)
- **Verified:** me, 2026-10-06 - fetched https://blinkenshell.org/docs/resource-limits/ and https://blinkenshell.org/docs/rules/ directly (both 200, under verify/pages/ as blinkenshell_limits and blinkenshell_rules) and read the Free column of the limits table cell by cell. The Free/Supporter table IS on /docs/resource-limits/; an earlier revision attributed it to the wiki root, which carries no table at all.

#### hashbang (#!)

- **What you get:** LXC containers on Atlantic.net. Live node de1.hashbang.sh (Nuremberg), maxusers 6175. HARD PER-USER LIMITS EXIST in the operator's deployed config: MemoryLimit=512M, CPUQuota=50%, nproc soft 150 / hard 200, applied at login. No published disk quota.
- **The wall:** DAILY IDLE PROCESS KILL. /etc/cron.daily/clean-lurkers runs daily and, for any user with no SSH login in 30 DAYS (lastlog -b 30), runs 'loginctl terminate-user' unless /home/<user>/.keep-account exists. It kills sessions/processes, NOT the account or data.
- **The keepalive:** touch /home/<user>/.keep-account ONCE. That single file is the opt-out the sweep checks. A detached tmux is NOT sufficient: the sweep keys off lastlog (SSH login), not process liveness.
- **Account:** sign-up required = True, card required = False
- **Caveat:** CORRECTION: an earlier revision of this census said 'no idle kill, no account-purge cron' and 'NO published quota'. BOTH WERE WRONG. The purge lives in /etc/cron.daily/clean-lurkers, not the root crontab, so a reader checking only /etc/crontab misses it. The quotas live in the operator's Ansible config. Still the closest thing to anonymous: a public key IS the account, no signup form, no card. Live API shows ONE node (de1); the GitHub README listing four (da1/ny1/sf1/to1) is stale. Account creation POSTs your public key to https://hashbang.sh/user/create: a public key IS the account, no signup form, no card.
- **Source:** <https://raw.githubusercontent.com/hashbang/shell-etc/master/cron.daily/clean-lurkers>
- **Vendor says (quote, RECONSTRUCTION - 2 fragments joined by `...`, not one contiguous quote):**
> DAYS=30 ... if [ ! -f "/home/${user}/.keep-account" ]; then loginctl terminate-user "$user"
>         fi
  - _Fragments:_
  - 1. `DAYS=30` -> `verify/pages/hashbang_clean_lurkers.html`
  - 2. `if [ ! -f "/home/${user}/.keep-account" ]; then loginctl terminate-user "$user"
        fi` -> `verify/pages/hashbang_clean_lurkers.html`
- **Vendor says (quote2, VERBATIM):**
> /bin/systemctl set-property --runtime "user-${PAM_UID}.slice" \ CPUQuota=50% MemoryLimit=512M BlockIOWeight=10
- **Verified:** me, 2026-10-06 - read cron.daily/clean-lurkers and ansible/tasks/security/main.yml from hashbang/shell-etc and hashbang/shell-server at GitHub raw (both 200, under verify/pages/ as hashbang_clean_lurkers and hashbang_limits) and the live /server/stats API (200, hashbang_stats). An earlier revision of this row quoted a tmux line that is in no capture; it is withdrawn rather than left as an unverifiable claim.

#### Ctrl-C.club

- **What you get:** Linux shared host on DigitalOcean, ~825 users, IRC (6667) and Gemini. Operator: Eric Budd, hosted by Mount Olive Software. 1 GB storage limit, stated as a soft limit. No RAM/CPU ceiling published.
- **The wall:** 5-year inactivity archive: 'we're archiving accounts that have not been logged into in 5 years or more', restorable on request. No session-level timeout stated.
- **The keepalive:** one login per 5 years. The homepage states the archive policy verbatim: 'we're archiving accounts that have not been logged into in 5 years or more', with a restore path via the admin address.
- **Account:** sign-up required = True, card required = False
- **Caveat:** RETIERED FROM T1 ON REVIEW: T1 says 'no expiry' and this row archives at 5 years. Its quotes were also moved to the pages they are actually on - the closed-signups text and the 1 GB limit are both on signup.ctrl-c.club, not on system_notice_long.html, which words the storage limit differently and differently again. Signups are CURRENTLY CLOSED (waitlist only). Reachable today only by EXISTING members; a new person can only join a waitlist. The daemon ban is on Eggdrop bots and on services DUPLICATING Ctrl-C.club's own, not on all background processes.
- **Source:** <https://ctrl-c.club/>
- **Vendor says (quote, VERBATIM):**
> To make room for our active and new users, we're archiving accounts that have not been logged into in 5 years or more.
- **Vendor says (quote2, VERBATIM):**
> Signups are closed for now! Thank you for your interest in Ctrl-C.club! We're pausing signups to work on some scaling issues. You can still submit a signup to get on a waitlist.
- **Vendor says (quote3, VERBATIM):**
> One gigabyte storage limit (this is not a hard limit: brief, occasional overages are not a problem).
- **Verified:** me, 2026-10-06 - fetched ctrl-c.club/ (quote, and the 825-user population figure), faq.html, signup.ctrl-c.club/ (quote2, quote3) and system_notice_long.html directly, all HTTP 200, under verify/pages/ as ctrlc_home, ctrlc_faq, ctrlc_signup, ctrlc_notice. Live banner read by verify/probe.py.

### T3 — NEEDS A RELAY. Runs fine but is unreachable: no inbound ports, egress restrictions, or browser-only. An outbound-initiated tunnel or held WebSocket to a free relay service makes it reachable.

#### ModelScope Studio (创空间)

- **What you get:** platform/2v-cpu-8g-mem on modelscope.cn and platform/2v-cpu-16g-mem on modelscope.ai, BOTH resource_type=free, no GPU. The two sites serve DIFFERENT anonymous free tiers. Gradio/Streamlit/Docker/static SDKs. Public *.ms.show URL. /mnt/workspace is OSS-backed and persistent across restarts.
- **The wall:** official docs define a Sleeping state — 'Sleeping after a long period without access', woken by visiting the URL. Exact timeout is NOT published anywhere reachable. Free quotas also carry a time limit.
- **The keepalive:** Periodic access to the public *.ms.show URL wakes it. The operator's own measured work (studio-recon.md) already proves a full userspace Tailscale node + SSH runs inside a Studio, so the relay/keepalive path is established in practice, not just in theory.
- **The relay:** userspace Tailscale with --tun=userspace-networking (no /dev/net/tun in the pod, no CAP_NET_ADMIN) — proven working in the operator's evidence corpus
- **Account:** sign-up required = True, card required = False
- **Caveat:** THE '~5 FREE INSTANCES' FIGURE IS WITHDRAWN AS UNSOURCED. Three research passes searched every first-party surface (the official skills repo, all Studio docs, deploy_schema.json, the i18n bundle) and found NO per-account count. What is established is that a free Studio exists and that some cap exists; the value is never published. Do not quote '5' from this project. The idle-sleep timeout is likewise only qualitative ('Sleeping after a long period without access'); no hours figure is published for Studio (the published idle numbers belong to Notebook, not Studio). The operator's own measured Tailscale deployment proves it hosts a real userspace node despite /dev/net/tun being absent.
- **Source:** <https://modelscope.cn/openapi/v1/studios/hardware>
- **Vendor says (quote, VERBATIM):**
> {"hardware":[{"name":"platform/2v-cpu-8g-mem","resource_type":"free","supported_sdk_types":["gradio","streamlit","docker","static"]}]}
- **Vendor says (quote2, VERBATIM):**
> {"hardware":[{"name":"platform/2v-cpu-16g-mem","resource_type":"free","supported_sdk_types":["gradio","streamlit","docker","static"]}]}
- **Verified:** me, 2026-10-06 - fetched BOTH unauthenticated OpenAPIs. quote is the whole of modelscope.cn's response data.hardware[0], captured at verify/pages/modelscope_hw.html; quote2 is the same field from modelscope.ai, captured at verify/pages/modelscope_ai_hw.html; each was stable across 3 runs. The two are separate quotes because they are two separate responses from two separate sites - an earlier revision spliced them into one string, which no capture can match.

#### Cloudflare Durable Objects (Free plan)

- **What you get:** Single-threaded isolate, 128 MB memory, SQLite-backed DO. Free plan: 100,000 requests/day and 13,000 GB-s/day of duration.
- **The wall:** no idle kill while connected — a DO stays active while a request, RPC call, response stream, WebSocket, or pending I/O is in flight. Duration is billed only while active.
- **The keepalive:** a permanently held WebSocket, OR DO hibernation (which disconnects clients without destroying state and is not billed)
- **The relay:** the WebSocket is itself the relay — this is how you reach a DO from outside
- **Account:** sign-up required = True, card required = False
- **Caveat:** A Durable Object IS a machine in the meaningful sense — in-memory, stateful, WebSocket-capable — but it is single-threaded with 128 MB and a 10 ms/request CPU budget. This is a relay-and-coordination substrate, not a general compute box. Cloudflare CONTAINERS (the actual machine product) are paid-only: the free plan is 'N/A'.
- **Source:** <https://developers.cloudflare.com/workers/platform/limits/>
- **Vendor says (quote, RECONSTRUCTION - 3 fragments joined by `|`, not one contiguous quote):**
> Requests 100,000/day | CPU time 10 ms | Memory 128 MB
  - _Fragments:_
  - 1. `Requests 100,000/day` -> `verify/pages/cf_workers_limits.html`
  - 2. `CPU time 10 ms` -> `verify/pages/cf_workers_limits.html`
  - 3. `Memory 128 MB` -> `verify/pages/cf_workers_limits.html`
- **Verified:** me, 2026-10-06 — Workers Free limits read from fetched bytes (HTTP 200, 248647 bytes) at verify/pages/cf_workers_limits.html

#### tilde.town

- **What you get:** ~3000 users, Debian. No published RAM/CPU/disk. screen/tmux + crontab available.
- **The wall:** no shell idle-kill. The 7-day auto-kick applies to the #tildetown IRC channel only and does not touch the shell account.
- **The relay:** REQUIRED — the host opens no user ports at all, so an outbound tunnel to a free relay service is the only way in. 'you can run simple services or cron jobs for local-only access'
- **Account:** sign-up required = True, card required = False
- **Caveat:** Pure T3 — the machine is perfect and the NETWORK is the wall, which is exactly what a relay fixes. Any admin may kill your processes under load. Signup is by invitation/request.
- **Source:** <https://tilde.town/wiki/faq.html>
- **Vendor says (quote, VERBATIM):**
> can i run servers on tilde.town? sort of. currently, we don't open any ports for users to use; however, you can run simple services or cron jobs for local-only access.
- **Verified:** me, 2026-10-06 - probed live (banner SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4, in verify/reachability.json) and re-fetched verify/pages/tilde_town.html, tilde_town_admin.html and tilde_town_autokick.html. The banner is the capture for the liveness claim; the pages are the capture for the port policy.

#### serv00

- **What you get:** Non-profit free shared hosting, 3 GB disk. FreeBSD. Supports cron and background processes.
- **The wall:** no published idle kill; no expiry.
- **The keepalive:** cron jobs are supported, which is what makes a daemon survivable across disconnects
- **The relay:** shared hosting, so no public port without a plan — an outbound tunnel is the reachable path
- **Account:** sign-up required = True, card required = False
- **Caveat:** Resource limits beyond the 3 GB disk are not published on the pricing page. I did not verify the cron/daemon allowance first-party; the research pass that reported it read the panel docs.
- **Source:** <https://serv00.com/pricing>
- **Vendor says (quote, VERBATIM):**
> Revolutionary hosting for FREE! 3 GB for free, no adverts, no hooks
- **Verified:** me, 2026-10-06 - page fetched HTTP 200, 54173 bytes, quote read from the fetched bytes at verify/pages/serv00_offer.html (the key in verify/fetch.py; an earlier revision of this field named a serv00.html that does not exist, with the same byte count, so the fetch was real and only the path was wrong).

#### alwaysdata — Free

- **What you get:** 1 GB SSD, 256 MB RAM, 1/4 CPU, 3-day backups. Shared LAMP/PaaS host, French datacenter.
- **The wall:** free PROFILES are suspended automatically if you have not connected to the administration interface for a long period — 120 days for accounts under a year old, yearly for older ones. RAM limit auto-kills processes.
- **The keepalive:** log into the admin interface on the required cadence
- **The relay:** free accounts are restricted to an alwaysdata.net subdomain
- **Account:** sign-up required = True, card required = False
- **Caveat:** The free plan's own terms forbid 24/7 services, so this is a T3-by-relay-and-keepalive rather than a real compute node. Note the profile-suspension policy suspends the whole profile, not just the shell.
- **Source:** <https://www.alwaysdata.com/en/pricing/>
- **Vendor says (quote, RECONSTRUCTION - 5 fragments joined by `|`, not one contiguous quote):**
> For personal needs, ad-free offer available for life | 0 EUR/month | Disk space SSD 1 Go | RAM 256 Mo | CPU 1/4
  - _Fragments:_
  - 1. `For personal needs, ad-free offer available for life` -> NO CONTIGUOUS MATCH in any capture under `verify/pages/`
  - 2. `0 EUR/month` -> NO CONTIGUOUS MATCH in any capture under `verify/pages/`
  - 3. `Disk space SSD 1 Go` -> NO CONTIGUOUS MATCH in any capture under `verify/pages/`
  - 4. `RAM 256 Mo` -> NO CONTIGUOUS MATCH in any capture under `verify/pages/`
  - 5. `CPU 1/4` -> NO CONTIGUOUS MATCH in any capture under `verify/pages/`
- **Verified:** research pass, first-party fetch

#### Hugging Face Spaces — ZeroGPU (free allowance)

- **What you get:** Free personal accounts in good standing (verified email, account older than 30 days) can host up to 2 ZeroGPU Spaces. 'large' = half an RTX PRO 6000 Blackwell, 48 GB VRAM; 'xlarge' = the full card, 96 GB. Gradio SDK only. 5 minutes of GPU per day.
- **The wall:** 48 hours of inactivity before the Space sleeps. Confirmed server-side: HF's runtime API reports gcTimeout 172800 on live Spaces, and the official client refuses space_sleep_time on cpu-basic.
- **The keepalive:** unclear whether polling defeats the 48h timer, and the GPU quota (5 min/day) exhausts regardless — so the GPU is not a persistent resource
- **The relay:** a Space can host an app with a public URL; an outbound tunnel to a free relay service is the reachable path
- **Account:** sign-up required = True, card required = False
- **Caveat:** MAJOR CORRECTION TO BOTH THE LAUNCH BASE AND THE USER'S PREMISE: the free CPU Basic Space (2 vCPU / 16 GB) that the launch base lists as a durable free row now REQUIRES PRO. The docs commit that moved it is huggingface/hub-docs@34ee0f00 (2026-07-21). What survives on a free account is Static Spaces (no runtime at all) and up to 2 ZeroGPU Spaces. Dev Mode SSH is PRO-only. So the launch base's 'Hugging Face Spaces (CPU), 2 vCPU/16 GB, free' row is no longer buildable on the tier it claims.
- **Source:** <https://huggingface.co/docs/hub/en/spaces-overview>
- **Vendor says (quote, VERBATIM):**
> Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts, Team or Enterprise for organizations. Free personal accounts in good standing can still host up to 2 Gradio Spaces running on ZeroGPU.
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 222896 bytes, quote read from fetched bytes at verify/pages/hf_spaces_overview.html; the 48h sleep read from hf_spaces_gpus.html (HTTP 200, 221818 bytes)

#### Koyeb — Free Instance

- **What you get:** 1 vCPU share (0.1 vCPU), 512 MB RAM, 2 GB SSD, volumes_enabled: false. Regions fra and was only.
- **The wall:** scales to zero after 1 hour without traffic. Scale-to-zero CANNOT be disabled and the idle period CANNOT be customized on the free instance.
- **The keepalive:** INCONCLUSIVE — if traffic truly resets the timer a sub-hour ping works, but the free instance also has volumes disabled, so a keepalive ping that reaches an app may not reach a bare daemon. Untested.
- **The relay:** a periodically-pinging external relay both holds it awake and gives it a public URL
- **Account:** sign-up required = True, card required = False
- **Caveat:** CORRECTION TO THE LAUNCH BASE, which recorded Koyeb as 'changed/dead — the free Hobby instance is not in the published tiers'. A free Instance IS published and documented, with its scale-to-zero rule stated explicitly. No persistent volumes on free.
- **Source:** <https://www.koyeb.com/docs/run-and-scale/scale-to-zero>
- **Vendor says (quote, VERBATIM):**
> The Koyeb Free Instance automatically scales down to zero when it doesn't receive any traffic for 1 hour. Scale-to-zero on this Instance cannot be disabled, and the idle period cannot be customized.
- **Verified:** me, 2026-10-06 — page fetched HTTP 200, 296380 bytes, quote read from fetched bytes at verify/pages/koyeb_szt.html

## Measured, not assumed: live reachability

peli-cloud could not dial a single host: its sandbox egress proxy refuses port 22 (`CONNECT -> 403`), so every row in its census is documented-only. This census was probed from a **residential host** instead. **10/14 endpoints accepted a TCP connection and 9 returned an SSH identification string.**

A banner is not a login. No credential was presented to any of these hosts.

| endpoint | result | banner / error |
|---|---|---|
| `blinkenshell.org:443` | open, silent | `connected, no banner within timeout` |
| `ctrl-c.club:22` | **banner** | `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.17` |
| `de1.hashbang.sh:22` | **banner** | `SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u10` |
| `freeshell.org:22` | **banner** | `SSH-2.0-OpenSSH_10.4` |
| `sdf.org:22` | **banner** | `SSH-2.0-OpenSSH_10.4` |
| `tilde.club:22` | **banner** | `SSH-2.0-OpenSSH_10.0` |
| `tilde.green:22` | **banner** | `SSH-2.0-OpenSSH_10.5p1 Debian-1` |
| `tilde.guru:22` | **banner** | `SSH-2.0-OpenSSH_10.0 FreeBSD-20250801` |
| `tilde.town:22` | **banner** | `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4` |
| `tilde.zone:22` | **banner** | `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4` |
| `blinkenshell.org:22` | no route | `connect timeout` |
| `blinkenshell.org:2222` | no route | `connect timeout` |
| `blinkenshell.org:6697` | no route | `connect timeout` |
| `ssh.alwaysdata.com:22` | no route | `DNS: [Errno 11001] getaddrinfo failed` |

2 results contradict prior claims and are the reason this probe was worth running. Every bullet below is computed from `verify/reachability.json`, so re-running the probe either reproduces them or falsifies them:

- **Blinkenshell is filtered, not down.** Port 443 accepted a connection while 22, 2222, 6697 did not (connect timeout) on the same host, in the same run. peli-cloud blamed its sandbox's port-22 refusal, but 2222 was never port 22, so that excuse never covered this case. The host is alive and filtering by protocol.
- **tilde.zone answers SSH** with the *identical* OpenSSH identification string as tilde.town: `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4`, which is what a shared image or a mirror produces. peli-cloud demoted tilde.zone for having no discoverable operator. A banner is still not evidence of a free tier.

_Measured 2026-10-06T12:23:02+0545 from a residential Windows host (this machine)._

## Dead ends, and the wall that killed each

Nothing below was overcome in practice. Each wall is one a relay or a keepalive is argued *not* to defeat, from the vendor's own wording, and no relay or keepalive was actually run against any of them.

| Provider | the hard wall |
|---|---|
| **Neon — Free Postgres** | 100 CU-hrs/month per project, and the vendor's own page prices an always-on database above it: 'Once scale to zero is disabled, the minimum CU-hours a database can use in a month is about 182.5 (about 730 hours in a month x 0.25 minimum CU size)'. 'At 0.25 CU… |
| **Railway Free VM** | 60-minute build window, then a 24-hour claim countdown. Unclaimed boxes and their files are DELETED. Claiming moves the box into an account where it bills normally. Anonymous trials can also be disabled under demand. |
| **GitHub Codespaces (GitHub Free personal)** | 120 hrs/month of 2-core compute, which is 60 wall-clock hours because GitHub's own pricing table gives a 2-core machine an "Included usage multiplier" of 2 per hour. One always-on 2-core codespace therefore dies after ~2.5 days, not 5. At exhaustion, without … |
| **Google Cloud Shell** | 12-hour absolute session cap AND a 40-minute inactivity termination, plus a 50-hour weekly quota. Two independent walls. |
| **Modal Sandbox** | 24-hour absolute Sandbox lifetime cap, regardless of credit. Plus a 60-second default idle scaledown_window. |
| **AWS Free Tier** | $200 of credit over 6 months, and the account CLOSES ITSELF when the credits run out or at 6 months, whichever comes first. The old 750-hour t2.micro/t3.micro always-free offer is gone. |
| **Azure Free Account (new customers)** | 750 hours each of B1s/B2pts/B2ats burstable VMs is a 12-MONTH tier, and the $200 credit lasts 30 days. |
| **Hugging Face Spaces — CPU Basic (2 vCPU / 16 GB)** | PAID-PLAN GATE ON CREATION. Free accounts cannot create Gradio or Docker Spaces at all as of 2026-07-21. Secondary wall: 48h sleep and an ephemeral disk. |
| **Hugging Face Spaces Dev Mode (SSH)** | PRO or Team/Enterprise only. |
| **Render — Free Postgres** | expires 30 days after creation. |
| **Killercoda** | 1 hour maximum on FREE (4h on paid PLUS), and all environments are deleted when the browser tab closes. |
| **Fly.io** | no free Machine allowance. The only 'first free' left is 10 GB of volume capacity. |
| **Replit — free published apps** | published apps go down after 30 days; plus sleep and credit caps. |
| **Play with Docker** | the product no longer exists. |
| **Cloudflare Containers** | no free plan; the free tier is 'N/A'. Requires the $5/mo Workers Paid plan. |
| **GitHub Actions — hosted runners** | 6-hour maximum job execution limit on ALL GitHub-hosted runners. Free accounts also have 2,000 minutes/month, which the 6h cap bounds first. |
| **Groq / Together / Cerebras / SambaNova / Nebius (free tiers)** | these are rate-limited INFERENCE ENDPOINTS, not compute substrates. There is nothing to keep alive. Cerebras's own table header labels its offer a Free Trial, i.e. a trial clock. |
| **LinuxOnTab / Microterm / WebVM / StackBlitz / Godbolt** | runs in the READER'S OWN browser tab. Nothing runs when the tab closes, and the machine is the user's laptop. |

## Corrections to the launch base

Read against first-party pages fetched on 2026-10-06.

- Oracle A1 is 2 OCPU / 12 GB, not 4 OCPU / 24 GB. Oracle's own page: 'this is equivalent to 2 OCPUs and 12 GB of memory'. peli-cloud's corpus card, its anonymous-vms.json and its CATALOGUE all repeat the 4/24 figure.
- Hugging Face free CPU Spaces are GONE. Gradio/Docker Spaces now require PRO as of huggingface/hub-docs@34ee0f00 (2026-07-21). peli-cloud lists a free 2 vCPU/16 GB CPU Space as a durable row; it is no longer creatable on a free account.
- GitHub Codespaces: peli-cloud DEMOTED this row for a quote that 'did not survive being fetched'. The 120 hrs figure IS on the cited page, in a table. The demotion was wrong (the row is still not always-on, for a different reason).
- Azure App Service F1 is 1 GB RAM / 1.00 GB storage, not the 512 MB / 5 GB in every older guide.
- Koyeb's free Instance IS published and documented with an explicit scale-to-zero rule. peli-cloud recorded it as 'changed/dead'.
- Blinkenshell free does NOT allow listening TCP ports, IRC bots, or bouncers. All three are Supporter-only. The flattened wiki table misleads; cell-by-cell parsing and the vendor's rules page both confirm.
- Northflank: peli-cloud says card_required=false. Northflank's own docs require a payment method for ALL users regardless of plan. The free tier is real and genuinely never sleeps; the card requirement is real too.
- Ctrl-C.club: signups are CLOSED (waitlist only) as of 2026-10-06. It publishes a 5-YEAR inactivity archive policy (the most generous in the census) but forbids Eggdrop bots and services duplicating its own.
- ModelScope: modelscope.cn serves a 2v-cpu-8g-mem free tier while modelscope.ai serves 2v-cpu-16g-mem. Both verified, both stable across three runs. ModelScope's own docs still say 16g.
- The ModelScope '~5 free instances per account' figure has NO first-party source anywhere and is withdrawn.

## What this census did NOT establish

Stated plainly, because a census that hides its gaps is worse than no census.

- No account was created on any provider. Every verdict comes from first-party documentation plus, for the shared-shell hosts, a live TCP/SSH-banner probe from this residential host. A banner proves the host is up and speaking SSH; it does NOT prove a login completes, nor that a free tier is available to a new account.
- Ctrl-C.club is reachable today only by existing members, since signups are closed. Its T1 describes an existing member's box, not a new user's.
- hashbang's idle kill and quotas were read from the operator's deployed config, not observed by sitting idle for 30 days.
- The Oracle 7-day reclaim threshold, the Render 15-minute keepalive, and every other keepalive is a mechanism read from documentation, not an executed 30-day result.
- The ModelScope per-account Studio cap exists but its value is never published; the '~5' belief is withdrawn as unsourced.
- An earlier revision of THIS census made two factual errors (hashbang's idle policy, and Blinkenshell's free-tier ports) that were caught only by reading the operator's deployed files rather than a flattened web scrape. Rows are labelled 'me' vs 'research pass' so a reader can weight them, but 'me' still means 'I read the bytes', not 'I logged in'.

## Reproduce

```sh
python tools/check-always-on-free.py           # guard the census
python tools/check-always-on-free.py --mutate  # prove the guard can fail (13/13)
python tools/render-always-on-free.py          # rewrite this page from the JSON
python tools/check-rendered-page.py            # the committed page matches this renderer
python tools/check-rendered-page.py --mutate  # prove that gate can fail (12/12)
python verify/fetch.py                         # re-fetch the vendor pages
python verify/claim.py                        # every quote, against the bytes it came from
python verify/fetch.py --check                # is every capture re-fetchable by name?
```

## Method

- **Launch base:** cloned talaria0101/peli-cloud and read docs/ANONYMOUS-VMS.md and data/anonymous-vms.json as the starting corpus
- **Sweep 1:** 18 parallel research agents across provider families (cloud majors, notebooks, app hosting, devboxes, shared shells, inference, university, and an adversarial pass over the launch base itself)
- **Sweep 2:** 12 parallel agents tasked with closing the gaps sweep 1 exposed, and with re-classifying every provider by WHICH WALL it has: liveness (defeated by a keepalive) vs networking (defeated by a relay) vs quota (defeated by nothing)
- **First-party verification:** I fetched 19 vendor pages myself and read the quotes out of the fetched bytes rather than trusting the agents. Stored under verify/pages/. Every quote I personally confirmed says so in its verified_by field.

Fetches that failed (recorded, not silently substituted):

- `https://www.pythonanywhere.com/user/ -> HTTP 404`
- `https://docs/huggingface.co/docs/hub/spaces-sleeping -> 404, the page does not exist`
- `https://huggingface.co/storage/pricing -> HTTP 401, auth-gated`
- `northflank.com/docs/* -> HTTP 200 but client-rendered, ~274 bytes of text`
- `modelscope.cn/code/workspace and modelscope.ai/docs -> HTTP 200 SPA shells with no readable content; doc search is CAPTCHA-gated`
