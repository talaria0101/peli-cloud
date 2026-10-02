# experiments

The instrument. Every number in `docs/FINDINGS.md` and `data/catalogue-ranked.md`
came out of one of these, and each one can be re-run by somebody who distrusts
the write-up.

Scripts are numbered in the order they were run. A reader landing on `40-` knows
three things ran first and can find them.

| script | question it answers | needs |
|---|---|---|
| `10-fetch-corpus.sh` | can the corpus be re-fetched at its pinned commit? | git, network |
| `20-extract-provider-universe.py` | what does each of the 366 cards publish, read from primary fields only? | python3 |
| `30-rank-providers.py` | which providers are cheapest-first for one stated workload? | `20` |
| `40-crosscheck-engine.py` | where does peli-cloud's model disagree with the corpus's own engine? | `30`, node |
| `50-firstparty-audit.py` | do the corpus's prices still match vendors' live pages? | `20`, network |
| `60-guard-mutation.py` | can the guards in `20` and `30` actually fail, and do they still accept correct input? | `20`, `30` |
| `70-period-model.py` | what does one shape cost at each duty cycle, per provider, before and after credit? | `20` |
| `80-render-catalogue.py` | render the four tables from the period model | `70` |
| `90-exclusion-ledger.py` | where did all 366 cards go, including the ones that price nothing? | `20` |
| `91-minimum-bill-penalty.py` | what does a $/hour table hide about short bursts? | `70` |
| `95-reprobe-unpriced.py` | do the cards priced as unpriced still price nothing today? | `20`, network |
| `61-period-model-guards.py` | can the period model's guards actually fail? | `70`, `80` |
| `62-period-model-mutation.py` | do those guards catch the four defects that actually shipped? | `61` |

`poc/peli-cloud-query.py` queries the result. It does not re-price anything.

## The rules these scripts keep

- **A free plan is not a placeholder rate.** `known()` accepts zero (plan fees,
  credits); `rate_known()` demands a strictly positive hourly rate. Conflating
  them broke 219 providers once and hid a real `$0.50` size once. Both failures
  are recorded in `docs/FINDINGS.md` section 5.
- **Never call the subject's own engine to grade it.** `20` reads the raw card
  fields. `40` calls the upstream engine separately and the two are compared, so
  a disagreement is visible instead of inherited.
- **Size tables flatten.** Some cards nest a list inside `sizes`.
- **Zero is not a free tier.** A card whose only zero-dollar plans are `beta` or
  `application` has no free tier, but a `beta` plan with a published price is
  still a real price and stays in the universe.
- **`60` plants the defect each guard exists to catch**, and also proves each
  guard still accepts a correct input. A guard that refuses everything looks
  identical to a good one until it blocks real work.
- **Everything prints its conditions** (date, corpus commit, workload, model) and
  writes a JSON artefact under `data/`. Nothing deletes its own output.
- **Exit codes mean something:** 0 the measurement ran, 1 it ran and the thing
  was empty or failed, 2 it could not run. `61` uses all three: a planted defect
  is 1, and a tree it cannot find is 2 with a message on stderr. It used to
  crash with a bare `FileNotFoundError`, which is a 1 to the shell and silence
  to a reader, and that silence is what hid the three defects below.
- **The console and the catalogue must agree.** `70` prints the ranking and `80`
  writes the catalogue from the same artefact. When they disagreed, GUARD F in
  `61` caught it; before GUARD F existed they had been disagreeing since the
  period model landed.

## The stated workload

`30` prices exactly one workload and prints it on every run:

    2 vCPU / 4 GiB RAM / 20 GiB disk
    300 sessions a month, 10 minutes each   (= 50 machine-hours)
    nothing 24/7, one seat, no GPU, open internet

Change `WORKLOAD` at the top of `30-rank-providers.py` and re-run it, then re-run
`40`, and the whole table moves. That is the intended way to use this: pick your
workload, get your ranking.

## Known limits of the instrument

- The corpus is somebody else's tree, read at one commit. Prices inherited from
  it are inherited errors.
- `50` can only read pages that render prices server-side. Several large vendors
  (AWS, Azure, Hetzner, Contabo) render client-side and are reported unscored,
  not as passes.
- A **per-invocation** product is excluded from the ranking, not priced. It has
  no $/hour, so there is nothing to rank on a duty cycle. The test is structural
  (no positive hourly rate published anywhere on the mode, and a note that names
  the unit), and every exclusion is listed in `data/period-model.json` under
  `per_request_modes_skipped`. The first version of that test matched note text
  and deleted six real sandbox providers; see `docs/FINDINGS.md` section 5.4.
- No vendor signup, so no realised price, no redeemed credit, and no verified
  concurrency limit. Every number here is a published number, checked for
  arithmetic, never a measured bill.