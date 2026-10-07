# Deep reviews R26-R35: the always-on free compute census

Scope, 2026-10-06 to 2026-10-07, against the always-on census added in PR #1
(`data/always-on-free.json`, `docs/ALWAYS-ON-FREE.md`) and the guards, renderer
and evidence tooling that came with it. Ten reviews, ten methods, each naming
what it attacked, what it found, and what changed. Three of them found nothing,
and that is stated as a result rather than padded.

The count moved **22 counted rows to 19**, with seven rows re-tiered. The
extended guard grew from 14 to 19 planted defects, all caught by the clause each
names. `verify/claim.py` went from 68 phrases over 35 pages to 72 over 36, and
every one of them now verifies from this host.

The deepest problem this pass found was not in the data. It was that three tools
could report success having verified nothing, and a fourth could pass a page
that no live fetch could reproduce.

---

## R26 - three tools could report success having verified nothing

**Attacked:** every tool in `verify/`, each with a defect it exists to catch.

**Finding:** three of them, and the combination was worse than any one.

`verify/fetch.py` returned 0 from `fetch()` with the `return` sitting outside
the `try`, with no reference to `ok`. It printed `33/35 fetched` and exited 0.

`verify/probe.py` had no `return` in `main()` at all, so it exited 0
unconditionally, and it wrote `verify/reachability.json` unconditionally.
Failing-before, in a `/tmp` copy so the artefact survived:

    $ python verify/probe.py
    0/14 reachable, 0 returned an SSH banner
    wrote verify/reachability.json
    exit=0

That replaced a real 10/14-reachable, 9-banner measurement from a residential
Windows host with fourteen DNS failures, and reported success.

Worse than either: **a fetch that failed left its previous capture in place**,
and `claim.py` read those stale bytes. Failing-before, on the real merged code,
with a planted capture:

    planted stale capture   md5=e36a317cf4bd375e959fe1a628d0596c
    verify/fetch.py         33/35 fetched   exit=0
    capture after the fetch md5 unchanged
    verify/claim.py         [HIT] sdf_members01: '20 MB disk quota...'   exit=0

A fully green pipeline in which the quote had not been re-verified against live
bytes at all. This repo's own `.gitignore` names the hazard for `.quote-cache/`
("a cache that goes stale silently would let the quote check pass against a page
that has since changed"); `verify/pages/` had no such protection.

Also found: `verify/claim.py` exits 0 if a page filter matches nothing (fixed in
the PR itself), and `tools/check-quotes.py` passes with an unknown row id,
printing `rows=0 verified=0`.

**What changed:** `fetch.py` exits non-zero unless every URL returned 200, and a
URL that fails has its capture **deleted** so stale bytes cannot survive into a
green run. `probe.py` gained `--dry-run`, refuses to overwrite when a run
reaches 0 of N endpoints (naming the measurement it left intact), and refuses
duplicate `host:port` targets. `expected_failures` in `probe-hosts.json`, which
documented three control endpoints and was read by nothing, is now reported
against each run.

## R27 - GitHub Codespaces was 2x out, and nine other quantities were right

**Attacked:** every number in `data/always-on-free.json`, `spec`,
`idle_or_session_limit`, `keepalive`, `caveats`, `hard_wall` and `cost`.

**Finding:** one real error, ten verified correct.

The free-tier table reads "Compute time per month | 120 hrs". The same page's
pricing table gives a 2-core machine an **"Included usage multiplier" of 2** per
hour. So one wall-clock hour of a 2-core codespace consumes 2 units of that 120:
120/2 = 60 hours = **2.5 days**, not 5. The row said "~5 days" in its `hard_wall`
and "120 core-hours" in its `caveats`, and `tier_note` quoted the same 120 as
"120 core-hours" while listing it as a quota wall. Corrected in all three
places, because a number that is right in the note and wrong on the row is how a
reader ends up believing both.

Ten quantities that check out:

| claim | check |
|---|---|
| Oracle 1,500 OCPU-h and 9,000 GB-h = 2 OCPU / 12 GB | 1500/2 = 750 h, 9000/12 = 750 h, same ceiling |
| ...and it fits a 744 h month | 2 x 744 = 1,488 against 1,500, 6 h spare |
| Neon 100 CU-hr against a 24/7 database | 730 x 0.25 = 182.5, both figures verbatim on the cited page |
| Render 750 instance-hours | longest month 744 h, so exactly one fits |
| GCP e2-micro 2 vCPU at 12.5% each | 0.25 vCPU, exact |
| Google Cloud Shell 12 h cap against 50 h/week | 12 x 7 = 84 > 50, so the weekly quota binds first |
| ZeroGPU `gcTimeout 172800` | 172800/3600 = 48.0 h exactly |
| Azure free account 750 h | 744 h longest month, 6 h spare |
| GitHub Actions 2,000 min | 33.3 h; at most 5 whole 6-hour jobs |
| the `counts` block | identical to a `Counter` over the rows; tiers sum to 40 |

Also found: the row's `caveats` said "19 vendor pages" where the evidence store
holds 36 captures, and three rows state byte counts that drifted on re-fetch
(third-party HTML changes; recorded as an open question rather than corrected to
a number I could not verify).

## R28 - no fabricated quote survived, and one was on the wrong page

**Attacked:** all 47 populated `quote`/`quote2`/`quote3` fields, with a reader
written from scratch rather than the guard's own matching logic. A guard asked to
confirm itself confirms itself.

**Finding:** nothing fabricated. Of 38 quotes perturbed by one changed word plus
one changed digit, **0 were still accepted**, with a 38/38 unperturbed control in
the same run proving the reader worked.

Five quotes are not on the page they name, one of them a genuine
mis-attribution:

| row | finding |
|---|---|
| `play-with-docker` | cited `docs.docker.com/`, which does not contain the text at all; the real sentence is in the play-with-docker GitHub README, and the quote drops "Kubernetes systems" |
| `alwaysdata-free` | correct values, rewritten wording: the page writes the euro amount with the euro sign and a fraction as U+00BC, the quote spells both out as `0 EUR/month` and `CPU 1/4` |
| `tilde-guru` | the page uses U+00B7 MIDDLE DOT; the quote substitutes ASCII `-` |
| `railway-free-vm` | a table cell `claim window \| 24 hours` rendered as `Claim window - 24 hours` |
| `northflank-sandbox` quote2/quote3 | verbatim on the docs page, absent from the pricing page both in the capture and on a live refetch |

**This review also found the shape that fixes them.** The data carries
`quote_page`/`quote2_page`/`quote3_page` keys alongside the single `source`.
Keyed off those instead, four rows (`modelscope-studio`, `blinkenshell`,
`hashbang`, `ctrl-c-club`) are already correctly attributed, and the northflank
pair becomes a two-key fix rather than a dispute.

## R29 - the page could not be reproduced from a live fetch

**Attacked:** every value on `docs/ALWAYS-ON-FREE.md`, by perturbation: 480
renders, one data field changed at a time, plus a scrub test that replaced every
digit in both JSON files with a literal.

**Finding:** the biggest single defect in the pass, and it was hiding in plain
sight.

`docs/ALWAYS-ON-FREE.md` said `(+28 more)` about which captures contain the
Blinkenshell table cell `6`. A live re-fetch rendered `(+29 more)`, and
`check-rendered-page.py` failed on a clean clone for a reason that had nothing
to do with the census.

Cause, isolated rather than inferred. `locate()` substring-matched short
fragments across all 35 captures, so a bare `6` was "found" in 31 of them: it is
a substring of any number containing a 6 and of any hex UUID. Two captures are
ModelScope API responses carrying a random `request_id`, so every fetch moved the
count. Swapping **only those two UUIDs** back restored both counts, which is
what established causation.

The committed page was therefore reproducible only by luck of a UUID. Short
fragments are now matched on word boundaries: `\b6\b` does not match inside a
UUID, inside `1,500`, or inside `ipv6`. `6` drops from 31 captures to 11, all
of them genuine standalone tokens. Verified by three independent
fetch-and-render cycles, each byte-identical.

The same review found the headline "$0" typed while `rows[].cost` is ignored on
31 rows, and `card_charged` and `category` rendered nowhere. It also found that
the two reachability bullets, which an earlier revision had typed, are now
correctly derived: all four tilde.zone branches and all three Blinkenshell
branches produce different correct text, and the "N results contradict" count
tracks the data with correct singular and plural.

## R30 - the proxy has an allowlist, and it decides before DNS

**Attacked:** what a reader on an arbitrary host can reproduce, by mapping the
egress and then running each measurement.

**Finding:** the repo describes the mechanism wrong, in three files at once.

    CONNECT sdf.org:22    -> HTTP/1.1 403 not on the egress allowlist
    CONNECT sdf.org:80    -> HTTP/1.1 200 Connection Established
    CONNECT sdf.org:443   -> HTTP/1.1 200 Connection Established
    CONNECT sdf.org:2222  -> HTTP/1.1 403 not on the egress allowlist
    CONNECT sdf.org:6697  -> HTTP/1.1 403 not on the egress allowlist

Port 22 returns 403 **for a hostname that does not exist and for loopback**, so
the decision is made on the port alone, before DNS and before any destination is
contacted. It is an allowlist policy, not a refusal by any host, and it covers
2222 and 6697 as well as 22. `verify/reachability.json`'s `why` field, and three
documents that restate it, say only "refuses port 22 with HTTP 403".

Also: `verify/probe.py` never consults the proxy at all. It calls
`socket.create_connection` directly and its `import urllib.request` is unused, so
on a host behind a proxy it dies at the local resolver and reports 14 DNS
failures. And `measured_from` is the hardcoded string "residential Windows host
(this machine)", which every host that runs the probe stamps onto its own
output.

What a reader can reproduce: `verify/fetch.py` and `verify/claim.py`, both, from
a host with HTTP egress. What they cannot: the 14 TCP probes, and the 10/14 and
9-banner figures, because they come from a residential host whose path cannot be
checked from a sandbox at all.

## R31 - three files carried a limitation that had been disproved

**Attacked:** every numeric and named claim across `README.md`,
`docs/ALWAYS-ON-FREE.md`, `docs/ALWAYS-ON-OPEN-QUESTIONS.md`,
`experiments/README.md` and `data/always-on-free.json`.

**Finding:** three disagreements, and one of them was mine.

An earlier revision of this pass recorded `sdf.org` as unreachable, on the
strength of a single 502/504 pair, and wrote that into
`verify/fetch.py`'s `KNOWN_UNREACHABLE`, into the extended guard's exemption,
into `sdf-free-shell`'s `verified_by` ("the bytes are not reproducible from
here"), and into a new section of `docs/ALWAYS-ON-OPEN-QUESTIONS.md`. Three
consecutive fetches minutes later returned HTTP 200 for both pages, byte-identical
each run, and all 72 phrases verify here.

That is the failure this repo's own memory notes warn about: a note written from
a measurement decays into folklore, outlives its cause, and a later session
inherits it as current. It also marked two verifiable rows unverifiable on every
host that could verify them. `KNOWN_UNREACHABLE` is now empty on purpose, the
row's claim is withdrawn in as many words, and the tools' docstrings no longer
name a specific cause they cannot substantiate.

Also: `README.md` said `11/11` mutations where the guard had 13, and said a
banner was read from 8 hosts where the measurement records 9 endpoints across 9
hostnames but 8 distinct operators (`sdf.org` and `freeshell.org` are one host
under two names). Both are now written as both numbers, so neither reading is
lost.

## R32 - the tier definitions were themselves unchecked

**Attacked:** the tier assignments, read against `data/always-on-free.json`'s own
`tiers` and `tier_note` as the specification.

**Finding:** four rows the file's own definitions exclude, and one gap in how the
guard reaches a verdict.

- **`neon-free` was counted T2** on the reasoning that "auto-resume on query
  defeats scale-to-zero". Its own cited page prices an always-on database at
  ~182.5 CU-hours/month against a 100 CU-hour allowance. Defeating scale-to-zero
  is what makes the quota exhaust, which is the wall `tier_note` says a relay
  cannot defeat. DEAD.
- **`sdf-free-shell` and `ctrl-c-club` were T1** while carrying a 2-year login
  expiry and a 5-year archive. T1 is defined as "no expiry. It just runs." Both
  are T2. The same fix also removed a contradiction where two rows each claimed
  to be the most generous idle policy in the census.
- **`azure-appservice-f1` was T2** on a 20-minute idle timeout its own
  `verified_by` said was absent from its own cited page. UNVERIFIED.
- **`hf-spaces-zerogpu` was T3** while its own spec says 5 minutes of GPU per
  day. Found by widening the quota-unit pattern to the per-day form it had
  missed. UNVERIFIED.

The gap: `QUOTA_UNITS` decides a row on vocabulary, and a first version failed
any counted row naming a quota unit, which failed two rows that are correct.
Oracle's 1,488 hours fits inside 1,500 and Render's 744 fits inside 750. The
guard now computes where it can and only falls back to wording where it cannot,
because a guard that fires on true statements trains a reader to ignore it.

## R33 - five committed files carried CRLF from a Windows checkout

**Attacked:** idempotence, encoding and line endings, by running every script
twice and diffing every tracked file.

**Finding:** five files with CRLF, and an encoding fix that had closed half a
boundary.

`data/anonymous-vms.json` (498 lines), `experiments/96-always-on-corrections.py`,
`verify/claims.json`, `verify/probe-hosts.json` and `verify/reachability.json`.
`main` had none of them. The cost was not the bytes: the six-row correction in
`data/anonymous-vms.json` rendered as a **988-line diff in which no line
differed in content**, so the change it carried was reviewed by nobody.

PR #1 pinned `encoding="utf-8"` on the renderer's **write**. The **read** at
`tools/render-anon-vms.py:27` was still `json.load(open(DATA))`, and forcing only
that read to cp1252 reproduced the committed `docs/ANONYMOUS-VMS.md` exactly.
Both boundaries are now pinned, on three tools. Measured both ways with a
harness that sets the locale default and leaves `builtins.open` alone, so a
pinned encoding is respected and only unpinned code is affected:

    pre-pin:  25 raw 0x93 bytes; the file is not valid UTF-8 at all
    pinned:   0 raw 0x93; valid UTF-8

`.gitattributes` now pins `text=auto eol=lf`, and
`tools/check-line-endings.py` reads what is **committed** rather than what a
checkout produces. Verified with a planted CRLF file, reported and `--fix`ed.
`verify/pages/` is excluded on purpose: it is third-party HTML kept byte for
byte.

## R34 - nine attacks passed every gate

**Attacked:** the guards, by trying to break them rather than reading them.

**Finding:** nine, each a state the guard was supposed to exclude.

| attack | why it passed |
|---|---|
| a row quoting another provider's page verbatim | `quote_faults` searched the union of all captures and accepted any hit |
| a pure invention on a row with no capture | honestly-labelled, so UNVERIFIABLE and exit 0 |
| a `hard_wall` that denies the wall exists | the base guard only requires the field to be non-empty |
| a T1 row given a wall in unfamiliar words | `EXPIRY_PHRASES` was six closed stems; eleven real descriptions were silent |
| a lethal quota exempted by a caveat about disks | the exemption was searched across the whole row |
| `tiers.T1` rewritten to assert the wall it promises not to have | every clause checks rows **against** the definitions |
| an UNVERIFIED row with keepalive, relay and no wall | the tier returned early |
| a table quote built from three common tokens | no length floor on fragments |
| `a b c`, which folds to `abc` inside `gitlabci` | whitespace-forgiveness with no floor |

**What changed:** all nine are now planted defects in the extended guard's own
mutation suite, and it reports **19/19 caught, 19 by the clause they names**.
The two that needed the most care:

A row that **has** its own captures is held to them, and a hit outside them
names the foreign capture. Where a row has no capture of its own, an honestly
labelled research-pass row, the union search still runs, because there is
nothing to hold it to and failing it would fail an honest row for someone else's
evidence. That is why the honestly-carried count fell 16 to 12 once the captures
were re-fetched.

The `hard_wall` disclaimer check was too broad on its first attempt and failed
two **correct** rows, `fly-io`'s "no free Machine allowance" and
`cloudflare-containers`'s "no free plan". Both assert a wall. The pattern now
requires the object to be a wall. Recorded in the code, because a guard that
fires on true statements is worse than one that stays quiet.

## R35 - a reader following the documented order destroys the page

**Attacked:** the fresh-clone experience, by cloning to a scratch tree and
running each documented command in the order the documents give them.

**Finding:** one command order is wrong, and one exit code lies.

`docs/ALWAYS-ON-FREE.md`'s Reproduce block runs `render-always-on-free.py`
**before** `verify/fetch.py`. On a fresh clone the renderer finds no captures and
replaces 30 attribution lines with `CAPTURES ABSENT`, a 31-line diff, and exits
**0**. A reader who obeys the document order ends with a corrupted tracked file
and a passing exit code.

`check-rendered-page.py` exits **0** on a fresh clone having run 3 of its 5
clauses. It prints `NOT FULLY CHECKED` and explains itself, so a reader who reads
the output learns the truth, and `tools/check-all.py`'s table nonetheless prints
`PASS` beside it. Anything that looks only at the exit code is misled.

**What changed:** `verify/fetch.py` is documented as the first step, and
`tools/check-all.py` exists precisely because nothing told a reader which of a
dozen gates to run. It reports each gate's own exit code unpiped, and
distinguishes a gate that could not run from a gate that ran and failed, so a
fresh-clone red is legible instead of permanent.

---

## What is still open

`docs/ALWAYS-ON-OPEN-QUESTIONS.md` carries the detail, each item with the route
that closes it and a re-check date. The four that matter most:

- **No account was created on any provider.** Every verdict is documentation
  plus, for the shared-shell hosts, one live banner probe.
- **No keepalive was run for 30 days.** The Oracle 7-day reclaim threshold, the
  Render 15-minute keepalive and every other mechanism is read from
  documentation, not executed.
- **The one live TCP measurement cannot be re-verified from a sandbox.** It
  comes from a residential host behind a network that permits port 22. The
  10/14 and 9-banner figures are a measurement of that host, and this repo can
  neither reproduce them nor contradict them.
- **ModelScope's per-account Studio cap is still unpublished.** Three research
  passes searched every first-party surface and found no quota field to read.

## Limits of this pass

Review R34's own first attempt at the encoding harness injected cp1252 into every
`open()` call, which overrode the pins it was meant to be testing. It proved
nothing, and it was replaced before any conclusion was drawn from it. Recorded
because a review that reports only its successes cannot be checked.

Nothing in this pass created an account, dialled a port 22, or attempted a
login. The findings that changed the census all came from reading the vendor's
own bytes.