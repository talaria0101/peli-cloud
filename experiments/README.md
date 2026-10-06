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
| `51-billing-posture-probe.py` | what do 183 vendors say about billing a stopped machine? | `70`, network |
| `52-apply-posture.py` | which of those verdicts is safe to act on, and what is each worth? | `51` |
| `53-keep-rate-provenance.py` | for every priced row, is the keep rate measured or assumed? | `70`, `51` |
| `60-guard-mutation.py` | can the guards in `20` and `30` actually fail, and do they still accept correct input? | `20`, `30` |
| `70-period-model.py` | what does one shape cost at each duty cycle, per provider, before and after credit? | `20` |
| `80-render-catalogue.py` | render the four tables from the period model | `70` |
| `90-exclusion-ledger.py` | where did all 366 cards go, including the ones that price nothing? | `20` |
| `91-minimum-bill-penalty.py` | what does a $/hour table hide about short bursts? | `70` |
| `95-reprobe-unpriced.py` | do the cards priced as unpriced still price nothing today? | `20`, network |
| `61-period-model-guards.py` | can the period model's guards actually fail? | `70`, `80` |
| `62-period-model-mutation.py` | do those guards catch the four defects that actually shipped? | `61` |
| `96-always-on-corrections.py` | apply the 2026-10-06 corrections to the anonymous-VM census | none (edits `data/anonymous-vms.json` in place, idempotent) |

The always-on free-compute census lives beside this one rather than inside the
priced catalogue, because it answers a different question ("what stays up at $0",
not "what is cheap") and is guarded separately:

| script | question it answers | needs |
|---|---|---|
| `tools/check-always-on-free.py` | does the always-on census meet its own standard - ten hits, a quote and a source per hit, and no row that claims a keepalive or a relay it does not name? | python3 |
| `tools/check-always-on-free.py --mutate` | can that guard actually fail? | `96` not required |
| `tools/render-always-on-free.py` | render `docs/ALWAYS-ON-FREE.md` from `data/always-on-free.json` | python3 |
| `verify/probe.py` | dial the free-shell hosts and read their SSH banners from a host that can reach port 22 | network |
| `verify/claim.py` | does every quote survive being re-fetched into `verify/pages/`? | python3 |

`poc/peli-cloud-query.py` queries the result. It does not re-price anything.

## The rules these scripts keep

- **A free plan is not a placeholder rate.** `known()` accepts zero (plan fees,
  credits); `rate_known()` demands a strictly positive hourly rate. Conflating
  them broke 219 providers once and hid a real `$0.50` size once. Both failures
  are recorded in `docs/FINDINGS.md` section 5.
- **A free allowance is not a credit.** An allowance is a quantity of a
  resource, denominated in the provider's own unit (Oracle: 1,500 OCPU-h and
  9,000 GB-h a month), and is scoped to one SKU. `monthly_credit` is dollars
  and cannot express it, which is why Oracle's row was wrong by the largest
  amount in the catalogue. It is applied per resource-hour, only to the mode it
  was granted against, and before the floor and the credit, because it is free
  capacity rather than money. Converting an allowance into a dollar figure and
  applying it to a cheaper SKU is how Azure's and Google's grants land on the
  wrong meter in other catalogues.
- **The keep rate is a fraction of HELD time, and it does not scale a duty
  cycle.** The duty cycle is how long you hold the machine; the keep rate is how
  much of that you are billed for. Multiplying the two bills a suspending
  provider for zero hours. The keep rate belongs on the `held 24/7` figure,
  which is the sandbox-versus-VPS comparison, and the table prints both.
- **An unstated policy is not a measured one.** `51` fetches 183 vendor pages and
  gets a policy on 13. The other 170 are `unstated`, `shell` or `unreachable`
  and keep the conservative `1.00`; they are never rounded to "bills for uptime".
  Every published verdict carries the quote it came from, and the classifier
  runs a 14-case self-test on known real pages before it is allowed to publish,
  because it classified four of them wrongly before it classified them right.
- **A page that renders its prices inside a `<script>` is not a shell.**
  JSON-LD blocks are data the vendor publishes on purpose; stripping them
  alongside executable JavaScript made 4 of 26 "client-rendered" verdicts
  false. The stripper extracts JSON-LD first, and three cases in the self-test
  keep it that way.
- **`partial` is never mapped to one number.** A provider that stops billing CPU
  when paused and keeps billing RAM cannot be expressed by a scalar keep rate,
  and mapping it to 0.00 understates the bill by the resource that keeps
  charging. Those rows keep the default and are named as needing a split model.
- **The model reads the probe as an input, in one pass.** An earlier arrangement
  patched keep rates into `data/period-model.json` after the fact, and re-running
  the model silently discarded every one of them. A step that has to be
  remembered is a step that gets forgotten, and that one failed quietly.
- **A card field can disagree with its own name.** `hour == month_cap` means the
  corpus encoded a monthly rent in the hourly field, and the card's note says so.
  173 sizes across 8 cards are encoded that way. Multiplying the rent by hours
  published Hostinger at $17,632.80/month.
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
- **Exit codes mean something:** 0 the measurement ran and its artefact is the
  one on disk, 1 it ran and the thing was empty or failed, 2 it could not run.
  `61` uses all three: a planted defect is 1, and a tree it cannot find is 2
  with a message on stderr. It used to crash with a bare `FileNotFoundError`,
  which is a 1 to the shell and silence to a reader, and that silence is what
  hid the three defects below.
- **`51` also has a 3**, which means "this run found fewer billing-policy
  verdicts than the artefact already on disk, so I did not overwrite it".
  183 vendors fetched in a burst will serve degraded pages, and a run that
  silently replaced 13 verdicts with 3 is worse than no run at all. It is not a
  failure and it must not read as one, so it has its own code.
- **The console and the catalogue must agree.** `70` prints the ranking and `80`
  writes the catalogue from the same artefact. When they disagreed, GUARD F in
  `61` caught it; before GUARD F existed they had been disagreeing since the
  period model landed.
- **A relay and a keepalive fix different walls, and only one of them is fixable.**
  A keepalive defeats a *liveness* wall - idle sleep, scale-to-zero, a
  no-inbound-ports policy. Nothing defeats a *quota* wall - a monthly
  compute-hour cap that exhausts regardless, a 24-hour absolute lifetime, a trial
  clock, a paid-plan gate at creation. `data/always-on-free.json` tiers every row
  by which wall it has, and only a quota wall marks a row DEAD; the guard fails a
  T2 row that names no keepalive and a T3 row that names no relay, so a
  "workaroundable" claim always carries the workaround.
- **A free tier that cannot be created is not a free tier.** Hugging Face kept
  `cpu-basic` at $0 in its pricing table after it moved Space creation behind PRO.
  The price stayed true and the offer stopped existing, which is why `96` demotes
  that row on the strength of the creation gate, not the price.
- **An unstated policy is evidence about documentation, not about the machine.**
  Four tildeverse hosts are tiered from the absence of any published idle policy.
  They are labelled that way rather than as though their operators had promised
  anything, because silence is not a promise and a reader acting on it is taking a
  risk the page does not disclose.

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