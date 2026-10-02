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
| 2 | [Oracle Cloud](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 2.74 |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 3.12 |
| 4 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 3.29 |
| 5 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 4.11 |
| 6 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 4.44 |
| 7 | [Lizard](https://lizard.build/pricing) | 0.0180 | 5.40 |
| 8 | [shellbox](https://shellbox.dev/) | 0.0200 | 6.00 |

**The same providers at 24/7** (the regime where a sandbox becomes a VPS) are
roughly 2.4x the 10 h/day figure, and the order barely changes. Agent 37
publishes its own always-on figure: *"From $4.76/month, 2 vCPU, 4 GB RAM and
4 GB persistent disk at 730 running hours."*

**Free tiers, which revision 1 buried in a column:**

- **13 providers** publish a credit that recurs every month. The largest in the
  entire market is **Modal at $30/month**, then Freestyle $18.38, Run Cloud $15.
- **79 providers** publish a one-time signup credit. The famous $300 from
  Google, AWS, Azure, Oracle and IBM are **one-time**. They do not renew.
- **124 cards** sell a $0 plan and publish no credit, quota or cap. Whether that
  is a usable free tier or an unpriced meter is not in the card, so it is
  listed separately and called unknown rather than free.

**Subscription floors beat the hourly rate.** boat's metered rate is $0.018/hour,
but its $20 plan is a *usage credit*, not a surcharge — boat's own docs say
*"not a fee: every dollar comes back as sandbox time"*. So the bill cannot fall
below $20 and boat is **$20 at every duty cycle**, including 1 h/day.

## Reproduce it

    bash   experiments/10-fetch-corpus.sh               # re-fetch the corpus at its pinned commit
    python3 experiments/20-extract-provider-universe.py # read every card from primary fields
    python3 experiments/70-period-model.py              # price 3 shapes x 4 duty cycles
    python3 experiments/80-render-catalogue.py          # render the four tables
    python3 experiments/40-crosscheck-engine.py         # re-price with the corpus's own engine
    python3 experiments/50-firstparty-audit.py          # re-fetch vendor pages for a sample
    python3 experiments/60-guard-mutation.py            # can the guards actually fail?
    python3 poc/peli-cloud-query.py --budget 5          # query the old single-workload ranking

Every script prints its conditions and writes a JSON artefact under `data/`.

## Layout

    references/battleships/   the source corpus, in-tree at its pinned commit
    experiments/               the instrument: fetch, extract, price, render, cross-check, audit, guard
    data/                      generated artefacts
    poc/                       a query tool over the period model
    docs/CATALOGUE.md          the catalogue: four tables, every provider linked
    docs/FINDINGS.md           the write-up, opening with what it did not establish

## Licence

0BSD.