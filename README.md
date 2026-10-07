# peli-cloud

Every cloud sandbox, VM, dev-env and agent-runtime provider, ranked cheapest
first **at every usage period**, with free tiers, subscription floors and credits
each in their own table, and every row linking to the page its numbers came from.

- **What it is:** a research pass over a 366-provider corpus, priced at three
  shapes and four duty cycles, cross-checked against the corpus's own engine and
  spot-checked against vendor pages.
- **What it is not:** a live price feed. Prices are a snapshot from 2026-10-02.

## Start here

| you have | read |
|---|---|
| two minutes | [docs/CATALOGUE.md](docs/CATALOGUE.md) section A, then the 10 h/day `agent` table |
| before you commit to a cheap provider | table B1, the minimum bill |
| ten minutes | [docs/CATALOGUE.md](docs/CATALOGUE.md) in full |
| to buy something | table C, then the duty cycle that matches your agent |
| **a shell with no card and no account** | **[docs/ANONYMOUS-VMS.md](docs/ANONYMOUS-VMS.md)** |
| **a machine that stays UP at $0, indefinitely** | **[docs/ALWAYS-ON-FREE.md](docs/ALWAYS-ON-FREE.md)** - 19 counted rows, tiered by which wall they have |
| **what that census could not settle** | **[docs/ALWAYS-ON-OPEN-QUESTIONS.md](docs/ALWAYS-ON-OPEN-QUESTIONS.md)** |
| **to doubt the census** | **[research/deep-reviews-anon-vms.md](research/deep-reviews-anon-vms.md)** - five reviews; three of them removed rows |
| **an SSH session into this sandbox from outside** | **[research/verification/ssh-relay-2026-10-02.md](research/verification/ssh-relay-2026-10-02.md)**, then `sh tools/ssh-relay-check.sh` |
| **an SSH session OUT to Railway's anonymous VM** | `sh tools/poc-forward-relay.sh` - the relay's forward path works; dropssh v0.2.3's forward client does not |
| to distrust me | [experiments/](experiments/) and `data/*.json` |
| to know what was wrong | [docs/FINDINGS.md](docs/FINDINGS.md) |

## The short version

A cloud sandbox is **not** a VPS. It bills while it runs, and most of them stop
billing when they are stopped. So the price is a function of how long you hold
it, and a single monthly number cannot rank this market.

**At 10 hours/day, 2 vCPU / 4 GiB, before credits:**

| # | provider | $/hour | $/month |
|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 1.81 |
| 2 | [Lizard](https://lizard.build/pricing) | 0.0090 | 2.70 |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 2.71 |
| 4 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 3.12 |
| 5 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 3.29 |
| 6 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 3.50 |
| 7 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 4.11 |
| 8 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 4.44 |

**Oracle Cloud is cheaper than all of these at $0.00** and is not in the table
because it is free rather than cheap. Its Always Free allowance covers the
shape; see below and catalogue table B.

**Contabo and netcup are monthly VPSs, and they are here on purpose.** Their
corpus cards encode a month's rent in the hourly field and say so, so the model
divides by 730 hours. Before that correction they published at $4,752 and
$6,128 a month and were excluded from contention entirely.

**Lizard at rank 2 is a disputed row, not a confirmed one.** Its corpus card
carries only the default 4 vCPU size, but the vendor's own pricing page sells
*Small (2 vCPU / 4 GB) at $0.009/hour* and the card's note quotes that sentence.
Lizard's sandbox docs contradict it. The catalogue marks the row `disputed` and
prints the conflict; `docs/FINDINGS.md` section 5.5 has the quotes.

**Oracle's row is the largest known understatement in this table.** Its Always
Free Ampere A1 allowance covers this shape even at 24/7, so a qualifying account
pays $0. This model applies dollar credits only and cannot represent a
resource allowance; `docs/FINDINGS.md` section 6.1 says so explicitly.

**The same providers at 24/7** (the regime where a sandbox becomes a VPS) cost
more, and the order barely changes. Agent 37 publishes its own always-on
figure: *"From $4.76/month, 2 vCPU, 4 GB RAM and 4 GB persistent disk at 730
running hours."* This catalogue prints **$4.34** for the same 2 vCPU / 4 GiB at
24/7, and the two agree once the excluded disk is accounted for: the card's
$0.80/vCPU-mo and $0.70/GB-mo over 730 h is $4.40 of compute, and the
remainder is the 4 GB of persistent disk this model does not price.

**Free tiers, which revision 1 buried in a column:**

- **13 providers** publish a credit that recurs every month. The largest in the
  entire market is **Modal at $30/month**, then Freestyle $18.38, Run Cloud $15.
- **81 providers** publish a one-time signup credit. The famous $300 from
  Google, AWS, Azure, Oracle and IBM are **one-time**. They do not renew.
- **116 cards** sell a $0 plan and publish no credit, quota or cap. Whether that
  is a usable free tier or an unpriced meter is not in the card, so it is
  listed separately and called unknown rather than free.

Every count in this section is generated into `docs/CATALOGUE.md` tables A1, A2
and A3 and checked by `61-period-model-guards.py`, which fails if this prose
disagrees with the data. Prose that a script can compute should not be typed.

**Subscription floors beat the hourly rate.** boat's metered rate is $0.018/hour,
but its $20 plan is a *usage credit*, not a surcharge — boat's own docs say
*"not a fee: every dollar comes back as sandbox time"*. So the bill cannot fall
below $20 and boat is **$20 at every duty cycle**, including 1 h/day.

**The cheapest providers round up to the hour.** Hetzner ranks fourth at
$0.0104/hour and its billing FAQ says *"always round up the hourly usage"*, with
powered-off servers billed. An agent that starts a sandbox per tool call pays 4x
the headline rate. **25 of 202 providers** are affected; the full table is B1.

**One provider is genuinely free, and it is not a `$0` plan.** Oracle's Always
Free Ampere A1 allowance covers this shape outright. Oracle's own page says
*"All tenancies get the first 1,500 OCPU hours and 9,000 GB hours per month for
free for VM instances using the VM.Standard.A1.Flex shape."* A 2 vCPU / 4 GiB box
at 24/7 uses 1,440 OCPU-h and 2,880 GB-h, so the bill is **$0.00 before any
credit**. A 4 vCPU / 8 GiB box at 24/7 uses 2,880 OCPU-h, more than the
allowance, and costs **$13.80**. The allowance is scoped to that one shape and
the home region, and Oracle may reclaim capacity. Table B carries it as its own
table with the arithmetic rather than folding it into the paid ranking.

**Holding a box is a different question from using it, and the keep rate is the
difference.** The catalogue prints `held 24/7` beside the duty-cycle figures.
Lizard costs **$0.27** whether you use it an hour a day or hold it around the
clock, because its page says a paused sandbox does not bill. Contabo costs $0.27
to use for an hour a day and **$6.51** to hold. That is the whole argument for a
sandbox over a VPS.

**How much of that is measured, and how much is assumed.** The keep rate is read
first-party for **96 of 605 priced rows**: 61 from a policy the corpus card
publishes, 5 read by hand, and 30 from an automated probe that fetched **183
vendor pages** looking for the vendor's own words about billing a stopped
machine. It found a policy on 13 of them. The other 509 rows carry a
conservative `1.00` and the catalogue marks them `1.00*` rather than presenting
an assumption as a measurement. Every one of those 509 **overstates** what
holding costs, so the held column is an upper bound on them and never a floor.
`experiments/53-keep-rate-provenance.py` prints the split and
`data/keep-rate-provenance.json` records it per row.

Holding a 1 h/day box for a month, where the keep rate actually bites:

| provider | before | after reading the vendor's page |
|---|---|---|
| islo | $216.00/mo | **$9.00** |
| beam | $163.56 | **$6.81** |
| langsmith-sandbox | $136.08 | **$5.67** |
| zipbox | $9.86 | **$0.41** |

140 of the 183 pages were read and said nothing, 26 render client-side and could
not be read at all, and 3 providers turn out to bill one resource while paused
and not the other, which one number cannot express. All of that is in FINDINGS
6.4, including the four pages the probe classified wrongly before it classified
them right.

**A `$0` tier is not a free tier.** 16 cards mark one `trial_only` because it
blocks usage or expires. Replit's is $0 and buys nothing; its real entry is $18.
River, Vercel and boat were all published at $0 until the corpus's own
verification notes were read.

## Reproduce it

    bash   experiments/10-fetch-corpus.sh               # REQUIRED FIRST: fetch the corpus at its pinned commit
    python3 experiments/20-extract-provider-universe.py # read every card from primary fields
    python3 experiments/70-period-model.py              # price 3 shapes x 4 duty cycles
    python3 experiments/90-exclusion-ledger.py         # account for all 366 cards
    python3 experiments/91-minimum-bill-penalty.py     # what a $/hour table hides
    python3 experiments/80-render-catalogue.py          # render the four tables
    python3 experiments/40-crosscheck-engine.py         # re-price with the corpus's own engine
    python3 experiments/50-firstparty-audit.py          # re-fetch vendor pages for a sample
    python3 experiments/60-guard-mutation.py            # can the guards actually fail?
    python3 experiments/61-period-model-guards.py       # do the period model's guards hold?
    python3 experiments/62-period-model-mutation.py     # do they catch the defects that shipped?
    python3 poc/peli-cloud-query.py --budget 5          # query the old single-workload ranking

Every script prints its conditions and writes a JSON artefact under `data/`.

## The second question: free and anonymous machines, and SSH into a cage

The catalogue prices providers. A separate page answers what you can get a
shell on for nothing, and what it actually takes:

    python3 tools/check-anon-vms.py                       # guard the census
    python3 tools/render-anon-vms.py                      # write docs/ANONYMOUS-VMS.md from the JSON
    python3 tools/check-quotes.py                         # every quote, against the page it cites
    python3 tests/selftest-check-quotes.py                # the quote checker's own known answers
    python3 tests/selftest-check-quotes.py --mutate       # and the mutation that must be caught
    sh      tools/ssh-relay-check.sh                      # a REAL ssh login into this sandbox, over a relay
    sh      tools/poc-forward-relay.sh                    # the forward path OUT, and dropssh's defect in it
    sh      tests/ssh-relay-regressions.sh                # 11 clauses; each names the control it needs
    sh      tests/one-login.sh <name>                     # one login, passwd name drivable (PASSWD_NAME=<n>)

    python3 tools/check-all.py                             # ALL of the above that is python, one pass

[`docs/ANONYMOUS-VMS.md`](docs/ANONYMOUS-VMS.md) carries 26 rows: **15 free or
anonymous machines that a provider says answer SSH, 6 of them dialled and
banner-verified, 1 genuinely anonymous.** Railway's free VM is the only row
needing no account and no card, and its own FAQ says so: *"Railway identifies
you by your SSH key."* Every quote on the page is checked against the page it
cites, by `tools/check-quotes.py`.

Two things that page is careful about, because both are easy to get wrong:

- **`banner-verified` is not a login.** It means a relay dialed the host and
  read its SSH version string. On this host the relay's forward path stops
  before key exchange completes on every target tried, so the page separates
  the three claims rather than counting them as one.
- **SSH is not always on port 22.** Blinkenshell's own FAQ says it uses port
  2222. A sweep that only tries 22 records that entire class of host as dead.

[`research/verification/ssh-relay-2026-10-02.md`](research/verification/ssh-relay-2026-10-02.md)
records how a real SSH session works on a host that cannot bind a TCP port and
has no `/etc/passwd`, the five things that had to be true, the dropssh defect
this work found, and one claim of its own that was measured and then withdrawn.

**The corpus is not in this repository.** `ariana-dot-dev/battleships` publishes
no licence, so its 1183 files are fetched by `10-fetch-corpus.sh` rather than
redistributed here. See [`NOTICE`](NOTICE) for the evidence and for what that
costs: every figure below is checkable by re-running, not diffable against a
committed copy.

## The third question: free, and up forever

The anonymous census above answers *what can I get a shell on*. It is not the
same question as *what stays up on its own*, and the gap between the two is where
this market actually lives. A host that answers a banner may idle-kill your
process the next morning; a machine that never sleeps may carry a monthly quota
that runs out on the twentieth. Neither fact shows up in a table of "free tiers".

[`docs/ALWAYS-ON-FREE.md`](docs/ALWAYS-ON-FREE.md) prices neither, and holds
neither: it records **19 counted rows across 18 independent providers whose
machine stays up indefinitely at $0**, out of 40 rows in all (two of the counted
rows are the same Oracle tenancy, so they are one provider and are not counted
twice),
tiered by the wall each one has.

- **T1** runs as-is. **T2** sleeps but a named keepalive beats it. **T3** runs
  fine but needs a named relay to be reached at all. **DEAD** is a quota or a
  trial clock, and no relay fixes it. That is **T1=5, T2=8, T3=7, DEAD=18**,
  with the remaining 2 rows UNVERIFIED and counted nowhere.

The distinction is load-bearing: a relay defeats a *liveness* wall and never a
*quota* wall, so counting T2 and T3 as real hits is a claim about what a keepalive
or a tunnel actually does, not a way of padding a list. Every T2 row names its
keepalive and every T3 row names its relay, and the guard fails a row that
claims one without naming it.

    python3 verify/fetch.py                         # FIRST. Re-fetch the vendor pages; the gates below
    #                                            read verify/pages/, which is gitignored, and the
    #                                            renderer writes CAPTURES ABSENT without it.
    python3 tools/check-all.py                     # every gate in this repo, one pass
    python3 tools/check-always-on-free.py           # guard the census
    python3 tools/check-always-on-free.py --mutate  # prove the guard can fail (13/13)
    python3 tools/check-always-on-free-extended.py  # is every quote in a capture? (19/19 mutations)
    python3 tools/render-always-on-free.py          # write docs/ALWAYS-ON-FREE.md
    python3 tools/check-rendered-page.py            # the committed page is what the renderer writes
    python3 verify/probe.py                         # dial the hosts, read their SSH banners
    python3 verify/claim.py                         # every phrase, against the bytes it came from

`verify/fetch.py` is first because the order matters and getting it wrong is
silent: run the renderer on a fresh clone and it replaces 30 attribution lines
with `CAPTURES ABSENT`, exits 0, and leaves you with a corrupted page. The page
in `docs/ALWAYS-ON-FREE.md` says so in its own Reproduce block now.

`tools/check-all.py` exists because at one point there were a dozen gates and
nothing said which to run. It reports each gate's own exit code unpiped and
separates a gate that could not run from one that ran and failed, so a red
result on a host without captures is legible rather than permanent.

Two things that page is careful about, for the same reason the anonymous census
is:

- **A banner is not a login, and it is not a free tier.** `verify/probe.py` dials
  the shared-shell hosts from a host that can reach port 22, which the sandbox
  this repository was written in cannot - its egress proxy refuses 22. **Nine of
  the fourteen endpoints dialled answered with a version string**, which is eight
  distinct operators: `sdf.org` and `freeshell.org` are the same host under two
  names. That proves they are up; it says nothing
  about whether an account exists or whether signup is open.
- **Silence is not a promise.** Several hosts are tiered on the *absence* of a
  published idle policy. They are labelled as such rather than as though the
  operator had guaranteed anything, because silence is evidence about
  documentation and not about the machine.

The census is a snapshot with a 90-day shelf life;
[`docs/ALWAYS-ON-OPEN-QUESTIONS.md`](docs/ALWAYS-ON-OPEN-QUESTIONS.md) carries
what it did not settle, with the route that closes each gap.

## Layout

    references/battleships/   the source corpus, in-tree at its pinned commit
    experiments/               the instrument: fetch, extract, price, render, cross-check, audit, guard
    data/                      generated artefacts
    poc/                       a query tool over the period model
    docs/CATALOGUE.md          the catalogue: four tables, every provider linked
    docs/ANONYMOUS-VMS.md      free/anonymous machines that answer SSH, generated from its JSON
    docs/ALWAYS-ON-FREE.md     always-on free compute, tiered by which wall it has
    docs/FINDINGS.md           the write-up, opening with what it did not establish
    tools/                     the guards and renderers for both censuses, and the relay SSH check
      check-always-on-free-extended.py   traces every counted quote back into a capture under verify/pages/
      check-rendered-page.py             the gate on docs/ALWAYS-ON-FREE.md itself: the committed bytes, every count, every banner
    tests/                     the relay SSH regressions, 11 clauses, each with a control
    verify/                    first-party page captures, the reachability probe, and the quote re-check
    research/verification/     first-party notes behind the numbers

## Licence

The code and prose here are 0BSD. The third-party corpus is **fetched, not
redistributed**, because it carries no licence: see [`NOTICE`](NOTICE).