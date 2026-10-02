# peli-cloud

Every cloud sandbox, VM, dev-env and agent-runtime provider you can actually
buy, catalogued and sorted **cheapest first**, with the caveats that stand
between the headline number and the workload.

- **What it is:** a research pass and a re-analysis of a 366-provider corpus,
  priced on one stated workload, cross-checked against the corpus's own pricing
  engine, and spot-checked against vendors' live pages.
- **What it is not:** a live price feed. Prices are a snapshot.

## Start here

| you have | read |
|---|---|
| two minutes | [docs/FINDINGS.md](docs/FINDINGS.md) section 2, the honest answer |
| ten minutes | the whole of [docs/FINDINGS.md](docs/FINDINGS.md) |
| to buy something | [data/catalogue-ranked.md](data/catalogue-ranked.md), the 211-row table |
| to re-check me | [experiments/](experiments/) and `data/*.json` |
| to build on this | [experiments/README.md](experiments/README.md) |

## The short version

- The **cheapest** way to run a 2 vCPU / 4 GiB agent workload for 50 hours a
  month is **Scaleway's Stardust** instance at about **$0.03/month** (1 vCPU /
  1 GiB, stock-limited, no sandbox API). The cheapest actual agent sandbox is
  about **$0.30/month** (Agent 37) and **$0.69** (zipbox); Lizard and boat are
  **$0.90**.
- **Per-resource and preset-size pricing are different products.** E2B and
  Daytona, the best-known sandboxes, price the same workload at about **$8.28**,
  roughly 9x the size-based vendors, because they bill per vCPU-hour and
  per GiB-hour.
- **Recurring free credit barely exists.** Only 13 of 366 cards publish any
  monthly credit and the largest is **$30/month** (Modal). The big credits
  ($200-$300 from Google, AWS, Azure, Oracle, IBM) are **one-time signup
  credits that never recur**.
- **Watch the minimums.** Several of the cheapest rows (boat especially) only
  open up after a prepay or minimum top-up. The table's `entry fee`, `tier` and
  `notes` columns carry this per row.
- **"Scaleaway" is a typo for Scaleway.** Scaleaway's domain is parked and for
  sale; no such cloud provider exists. See [FINDINGS](docs/FINDINGS.md#4-the-two-providers-the-operator-named-and-one-that-does-not-exist).

## Reproduce it

    bash   experiments/10-fetch-corpus.sh              # re-fetch the corpus at its pinned commit
    python3 experiments/20-extract-provider-universe.py # read every card from primary fields
    python3 experiments/30-rank-providers.py           # rank cheapest-first on the stated workload
    python3 experiments/40-crosscheck-engine.py        # re-price with the corpus's own engine (strict + soft)
    python3 experiments/50-firstparty-audit.py         # re-fetch vendor pages for a sample
    python3 poc/peli-cloud-query.py --budget 5         # query the result

Every script prints the conditions it ran under (date, corpus commit, workload,
model) and writes a JSON artefact under `data/`.

## Layout

    references/battleships/   the source corpus, at its pinned commit (a git tree)
    experiments/               the instrument: fetch, extract, rank, cross-check, audit
    data/                      generated artefacts + the ranked catalogue table
    poc/                       a one-question query tool over the catalogue
    docs/FINDINGS.md           the write-up, opening with what it did not establish

## Licence

0BSD.