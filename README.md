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
| 4 | [Oracle Cloud](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 2.74 |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 3.12 |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 3.29 |
| 7 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 3.50 |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 4.11 |

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

**The cheapest providers round up to the hour.** Hetzner ranks fifth at
$0.0104/hour and its billing FAQ says *"always round up the hourly usage"*, with
powered-off servers billed. An agent that starts a sandbox per tool call pays 4x
the headline rate. **25 of 202 providers** are affected; the full table is B1.

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

**The corpus is not in this repository.** `ariana-dot-dev/battleships` publishes
no licence, so its 1183 files are fetched by `10-fetch-corpus.sh` rather than
redistributed here. See [`NOTICE`](NOTICE) for the evidence and for what that
costs: every figure below is checkable by re-running, not diffable against a
committed copy.

## Layout

    references/battleships/   the source corpus, in-tree at its pinned commit
    experiments/               the instrument: fetch, extract, price, render, cross-check, audit, guard
    data/                      generated artefacts
    poc/                       a query tool over the period model
    docs/CATALOGUE.md          the catalogue: four tables, every provider linked
    docs/FINDINGS.md           the write-up, opening with what it did not establish

## Licence

The code and prose here are 0BSD. The third-party corpus is **fetched, not
redistributed**, because it carries no licence: see [`NOTICE`](NOTICE).