# peli-cloud — findings (revision 2)

**Question.** Every cloud sandbox, VM, dev-env and agent-runtime provider a buyer
can actually reach, catalogued and sorted cheapest-first **at every usage
period**, with free tiers, subscription floors and prepay minimums left visible
instead of folded into one number.

**Date of pass.** 2026-10-02 (UTC). Machine: Linux x86_64, Python 3.14, Node
v26.8.1. Corpus commit: `f6a71ab09fef` (battleships, 2026-10-01). First-party
pages re-fetched 2026-10-02. Every number below is reproducible with the scripts
in `experiments/`.

---

## 0. What this did NOT establish (read before the table)

- **This is one corpus, re-read, not the whole market.** 366 provider cards came
  from ariana-dot-dev/battleships at `f6a71ab09fef`. I did not build 366 cards
  from 366 vendors' sites. The ranking is a re-analysis of that corpus, so it
  inherits every price error and every missing vendor in it.
- **Coverage was spot-checked, not proven complete.** I diffed the corpus
  against three independent 2026 "best agent sandbox" roundups (Upstash, Mastra,
  ajayk.sh). Every provider those three name is already in the corpus. That is
  good evidence the corpus is not missing the well-known names; it is not
  evidence it carries every long-tail or regional provider.
- **Prices are a snapshot.** They are as published on the vendor page on the
  corpus's check date (mostly 2026-09-28..30) and as re-confirmed by my
  first-party audit on 2026-10-02 for a 19-provider sample. Providers move.
- **The first-party audit confirms figures; it does not clear them.** Of 19
  sampled pages, 3 render client-side and were read as unscored, 6 matched
  every figure on the card, and 10 left some unconfirmed: 440 figures the
  probe could not find. Most of those (AWS 182, Azure 225, Vercel 22) are
  per-instance-size rates that no single page prints as one flat list, so they
  are a limit of reading a page as text, not evidence the corpus is wrong. A
  figure the card **derives** from a published bundle is reported separately and
  is not counted as a miss: `fly-machines`' `vcpu_h` 0.02916 is the published
  $0.043056/h performance price minus the 2 GB of RAM bundled at
  $0.006948/GB-h, and the audit recomputes that subtraction from the card's own
  note rather than reporting the card as wrong. This audit started out scoring
  **0 of 19** as a full match, because it compared printed strings and read
  E2B's per-second `$0.000014` as a disagreement with the corpus's
  `$0.0504/hour`; those are the same price and it now matches them by unit
  equivalence. A probe that reported 511 misses was measuring formatting, not
  prices.
- **The keep rate is read from published features, not measured.** A provider that
  publishes `auto_stop_idle: true` is recorded as suspending on idle; a provider
  that publishes nothing is recorded as `1.00`, billed for uptime, because a
  plain VM is. **No sandbox was created and stopped**, so no keep rate in this
  document is observed behaviour. It is a reading of the vendor's own feature
  list. Only 28 of 366 cards publish `auto_stop_idle` at all.
- **The period model excludes egress, storage beyond what a card bundles, IPv4
  and team seats.** A provider cheap here can be dear there. The full corpus
  cards carry those fields; these tables do not price them.
- **Duty cycles are arithmetic, not measured profiles.** 1, 4, 10 and 24 hours
  per day are round numbers. A real agent's distribution is not uniform, and no
  agent here was instrumented to find out what it is.
- **The minimum-bill figures are bounds, not bills.** Table B1 of the catalogue
  prices two usage profiles against the same demand. The `bursty` column sits on
  the pessimistic side by construction: it assumes every session is shorter than
  the provider's minimum, so a 15-minute call costs a full hour. That is the
  right side to err on when choosing, and the wrong side to budget from.
- **This is revision 4, and every earlier revision shipped errors that a check
  found and a reading did not.** Revision 1 was wrong in seven documented ways
  (section 3). Revision 2 added three more of its own (section 7). Revision 3
  added two: it published $/hour for 202 providers without mentioning that 42 of
  them bill a one-hour minimum (section 8 of the catalogue), and it read a `$0`
  tier as a `$0` entry price on 16 cards where the corpus had already flagged
  the tier as one that blocks usage (section 8). **Three revisions in, the
  defect rate was still roughly one per revision, and the last one was sitting
  in a file the corpus had shipped for me.** Assume more remain.

---

## 1. The workload the ranking is priced against

Three shapes:

| key | shape | what it is for |
|---|---|---|
| `tiny` | 1 vCPU / 1 GiB | a shell, a build step, a short tool call |
| `agent` | 2 vCPU / 4 GiB | the normal agent sandbox |
| `devbox` | 4 vCPU / 8 GiB | a developer box you keep around |

Four duty cycles per shape: **1, 4, 10 and 24 hours per day**, which is 30, 120,
300 and 720 machine-hours a month at 30 days.

These are stated because "cheapest provider" has no answer on its own. Change the
shape and the ranking changes; change the duty cycle and it changes again, and
sometimes the *kind* of provider that wins changes with it. Concurrency, GPU,
region and egress are not priced in these tables; the corpus cards carry them
and the upstream engine models them, which is what the cross-check in section 6
compares against.

---

## 2. The honest answer first

**A cloud sandbox is not a VPS, and revision 1 of this document priced it like
one.** That was the central error and it is corrected here. A sandbox bills while
it runs and most of them stop billing when they are stopped, so **the price is a
function of how long you hold it**. One monthly number cannot rank this market:
the cheapest provider at 2 hours/day is not the cheapest at 24/7.

Everything below is therefore published as a function of hours, at three shapes
and four duty cycles, in [docs/CATALOGUE.md](CATALOGUE.md).

### At 10 hours/day, 2 vCPU / 4 GiB, before credits

| # | provider | $/hour | $/day | $/week | $/month |
|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 0.06 | 0.42 | **1.81** |
| 2 | [Oracle Cloud](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 0.09 | 0.64 | **2.74** |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.10 | 0.73 | **3.12** |
| 4 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.11 | 0.77 | **3.29** |
| 5 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 0.14 | 0.96 | **4.11** |
| 6 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 0.15 | 1.04 | **4.44** |
| 7 | [Lizard](https://lizard.build/pricing) | 0.0180 | 0.18 | 1.26 | **5.40** |
| 8 | [shellbox](https://shellbox.dev/) | 0.0200 | 0.20 | 1.40 | **6.00** |

At **24/7** the same shape costs roughly 2.4x more and the order barely
changes; Agent 37's own page states *"From $4.76/month, 2 vCPU, 4 GB RAM and
4 GB persistent disk at 730 running hours"*, which is $4.34 of compute plus
$0.36 of disk.

### The three things that actually decide the bill

1. **A subscription floor can beat the hourly rate.** boat meters at
   $0.018/hour, but its $20 plan is a *usage credit*, not a surcharge. boat's own
   docs (fetched 2026-10-02): *"not a fee: every dollar comes back as sandbox
   time at the rates above."* The bill therefore cannot fall below $20, and boat
   is **$20 at every duty cycle**, including 1 hour/day. A provider whose floor
   exceeds your usage is a rental, not a metered box.
2. **Free credit is smaller and rarer than it is advertised.** 13 of 366 cards
   publish a credit that recurs; the largest is Modal at **$30/month**. 79
   publish a one-time signup credit, and the famous $300 figures from Google,
   AWS, Azure, Oracle and IBM are **one-time**: they do not renew. A further 124
   cards sell a $0 plan and publish no credit, quota or cap at all, which is
   recorded as unknown rather than free.
3. **The cheapest row is a different provider at every duty cycle, and the
   cheapest *kind* of provider changes too.** Per-resource sandboxes (E2B,
   Daytona at $0.0504/vCPU-h) lose to size-based ones (zipbox $0.0137/h,
   Lizard $0.0180/h) on a small box; the order reverses as the shape grows,
   because a 2 vCPU box is 2 units of the expensive model and one unit of the
   cheap one.

## 3. Where revision 1 was wrong

Written down because a reader who only sees the current tables cannot tell what
the earlier ones got wrong, and the corrections are the useful part.

| revision 1 said | why it was wrong | corrected in |
|---|---|---|
| "the cheapest is Scaleway Stardust at $0.03/month" | that was a 1 vCPU / 1 GiB machine priced as if the workload were 2 vCPU / 4 GiB, and it is stock-limited. At the real shape it is not the cheapest, and it is not an agent sandbox | table C, `tiny` vs `agent` |
| one monthly total per provider | reads a stoppable machine as a fixed monthly host, which is the VPS comparison the task is not asking for | the whole of table B |
| no hourly figure, no duty cycle | the cheapest provider is a function of hours; one number hides the answer | `$/hour`, `$/day`, `$/week`, `$/month` per duty cycle |
| "no large recurring free-credit tier; 13 of 366, max $30" | correct, but it was a paragraph in the middle of a write-up, and the *one-time* credits were folded into the same sentence | tables A1, A2 and A3, separately |
| boat at $0.90, "the first plan you can stay on is $20" | the $20 is not a cheaper tier you upgrade to, it is a **floor** the bill cannot fall below. The row was directionally right and structurally wrong | `floor` column; boat is $20 at every duty cycle |
| 211 ranked rows, ranked on one workload | a provider that fits 4 vCPU was ranked against one that fits 1 vCPU | three shapes, priced separately |
| the two named providers were checked; the third was a typo | correct, and still true, but it was the most-emphasised finding in the document when it is a one-line naming correction | section 4 |

### What revision 2 added

Revision 2 fixed the model but shipped three errors of its own, all found by
running a check rather than by reading the output:

| revision 2 said | why it was wrong | corrected in |
|---|---|---|
| "11 cards could not be priced" | 148 were missing from the ranking; the 11 was a post-filter count | section 7.3, table D |
| "the 86 unpriced cards are a vendor choice" | generalised from three pages; 20 of them publish a machine rate | section 7.2, `95-reprobe-unpriced.py` |
| arker at $0.0302/h | that is `eu-hetzner-proposed`, a region that does not exist; the live rate is $0.1877/h | section 7.1, pre-launch skip |

The single defect that produced most of the rest: **revision 1 never asked what
a sandbox is.** It took a corpus of cards, multiplied a rate by a month, and
sorted. The cards know the difference — 28 modes publish `auto_stop_idle`, 40
publish `pause_resume`, and `pricing: pool` bills whether used or not — and that
information went unused.

---

## 4. The two providers the operator named, and one that does not exist

### Scaleaway / Stardust — this is a naming error, and I checked it three ways

The operator wrote "scaleaway's Stardust instances". **Stardust is Scaleway's,
not Scaleaway's.** Evidence, in the order I ran it:

1. **The corpus already says Scaleway.** `references/battleships/research/cards/
   scaleway.json` carries a dedicated `stardust` mode, STARDUST1-S, 1 vCPU /
   1 GiB, ~$0.00068/h, flagged `stock`, split out of Scaleway's main table on
   2026-09-29. grep for "scaleaway" across the whole corpus returns nothing.
2. **The domain is a parked for-sale page.** `scaleaway.com` resolves to a
   page reading "scaleaway.com is for sale — Buy for $15,000 or Lease to Own"
   (confirmed via the text-extraction proxy on 2026-10-02). It is not a cloud
   provider.
3. **No such provider exists in any search engine.** Five independent queries
   for "scaleaway" return Scaleway (a French cloud), a commercial scale/degreaser
   manufacturer, and nothing that is a compute provider. There is no "Scaleaway"
   cloud with a "Stardust" instance type.

**Verdict: confirmed, the correct entry is Scaleway Instances, and it is rank 1
at about $0.03/month.** If the operator meant some other company, that company
is not findable and I did not invent it. Scaleway's Stardust is genuinely the
cheapest stock item in the whole corpus, so the intent behind the note is served
even though the name was wrong.

### Lizard.build — in the corpus, and it matches the live page

`lizard.build/pricing` fetched 2026-10-02 confirms, verbatim from the page:
Small (2 vCPU / 4 GB) $0.009/h, Medium (4/8) $0.018/h, Large (8/16) $0.036/h,
$10 free credit valid 7 days, concurrency 5 free / 20 after first top-up / 100
after $20 total paid. The corpus card and my first-party audit agree on every
one of those. Lizard is rank 10 at about $0.90 all-in. Isolation is `container`,
not a microVM — it is the cheapest fire-class boundary in the top of the table
alongside boat and shellbox.

### freestyle.sh — in the corpus, and it matches, with the best-documented free credit

`freestyle.sh/pricing` fetched 2026-10-02 confirms: Free $0 (hard cap, 10
concurrent), Hobby $50/mo, Pro $500/mo (fees are a usage credit, not a
surcharge), $0.04032/vCPU-h and $0.0129/GiB-h, 200 vCPU-h + 400 GiB-h + 60,000
GiB-h storage allowances on every plan. The corpus's `monthly_credit` of
$18.38 is exactly 8.064 + 5.16 + 5.16 (the vCPU-hour and two GiB-hour
allowances valued at the per-hour rates); the upstream verify note shows that
arithmetic. Freestyle ranks **94 at about $6.61 all-in**, which is the point:
it has the most thoroughly documented free credit in the corpus and it is still
not cheap, because the credit is denominated in hours of the wrong size.

---

## 5. Measurement defects I found and fixed (and two I found in the corpus)

These are the things that would have made this table wrong, kept because a reader
distrusting the numbers should see what broke and how. The first two were caught
by reading the pipeline output; the third and fourth were caught by the
guard-mutation review (planting the defect the guard exists to catch), which is
how the third should have been found the first time.

- **Bug 1: a `$0/hour` size.** The first run ranked 45 providers at exactly
  $0.00/month. Cause: `aws-ec2`'s `gpu-l4` size table lists `g6.xlarge` at
  `"hour": 0` (AWS no longer publishes a price for it). A truthiness test read a
  literal 0 as a real price. Fix: an **hourly rate** is published only if it is
  **positive**; zero is not a rate.
- **Bug 2: shape mismatch counted as a match.** I first priced each card at its
  *cheapest* published size regardless of whether it fit 2 vCPU / 4 GiB, so a
  card whose only box was 1 vCPU or 8 vCPU could outrank a card that actually
  fit. Fix: pick the cheapest size that satisfies the requested shape; when none
  does, price the largest offered and label it `smallest usable size is N vCPU /
  M GiB` rather than pretending it fits.
- **Bug 3: bug 1, one layer deeper.** Fixing it in the ranker was not enough.
  The `$0` size stayed in the *extractor's* size list, so the ranker's "cheapest
  size that fits" still selected it and then dropped the whole card for being
  free, when the card had a real `$0.50` size beside it. A planted card with
  sizes `[$0, $0.50]` priced as `None` instead of `$0.50`. Fix: the extractor
  filters non-positive rates out of the size list and reports how many it
  dropped, as `n_zero_priced_sizes`.
- **Bug 4: the fix for bug 3 was itself wrong.** Applying positive-only to
  *every* number broke 219 providers whose entry plan is legitimately `$0`; the
  ranking lost Scaleway and the free tiers. A free plan and a `$0/hour` rate are
  different things. Fix: two functions. `known()` accepts a published number
  including zero (plan fees, credits); `rate_known()` demands a strictly
  positive hourly rate. AWS Lambda is the check that the two are now correctly
  separated: its `vcpu_h` is 0 (CPU bundled) and it is priced on `ram_gib_h:
  0.04` alone, at $8.00.
- **Corpus defect (reported, not fixed): a nested size list.**
  `research/cards/scaleway.json` mode `dedicated-compute` nests a **list
  inside** its `sizes` array (the MEMORY3 row is a list of sizes, not a size).
  The upstream engine's own size filter (`s.vcpu >= W.vcpu`) would throw on that
  element; `coasty` nests one level too. My extractor flattens it and reports
  how many rows it flattened.
- **Corpus defect (reported, not fixed): an ambiguous `hour: 0`.**
  `aws-ec2.json`, as in bug 1. Whether it is an unpriced placeholder or a
  genuinely free size, the data does not say, and an ambiguous price that reads
  as free is a defect.

I did not verify that the upstream engine actually throws on the nested size
list at the live site, only that the element would fail its own predicate. The
two corpus defects are in somebody else's tree, so they are reported with file
and mode, not edited.

### 5.4 Four defects in the period model, found by reading its own output

The period model (`70-`) landed with a guard suite that could not run, so the
four defects below shipped unguarded. All four are fixed, and
`62-period-model-mutation.py` now plants each one and proves the guard refuses
it. Each is stated with the output that exposed it.

- **Bug 5: the console table ranked on the credit-adjusted price.** The
  catalogue and the console were generated from the same artefact by two
  scripts that disagreed about which number to sort on. `80-render-catalogue.py`
  sorted on `billed_month_no_credit`; `70-period-model.py` sorted on
  `billed_month_with_credit`. The console therefore put **Run Cloud** at rank 1
  of the 2 vCPU / 4 GiB / 10 h/day table with a month of **$0.00**, because its
  $15 recurring credit exceeded that month's $13.98 bill, while the published
  catalogue put Agent 37 at $1.81. Same data, same day, two different answers,
  and the one a reader sees first was the wrong one. The clamp to $0.00 also
  affected 5 of 202 rows at 1 h/day and 1 of 202 at 10 h/day. Fix: both sort on
  the pre-credit price, and a row whose pre-credit month is $0.00 is dropped
  from the ranking rather than shown as free, because a $0.00 position is an
  artefact of the model, not a price.
- **Bug 6: `keep_basis` was a leaked loop variable.** The basis travelled on a
  name bound while scanning a card's modes, so every priced row carried
  whatever the **last** mode of that card happened to say. `aws-lambda` shipped
  `keep_source: requires_always_on` beside `keep_basis: "billed for uptime (no
  suspension feature published)"` — two different claims about the same rate,
  and a reader cannot tell which is the one that was applied. Fix: the basis
  travels with the selected candidate, so a row's basis is its own mode's.
- **Bug 7: the per-invocation exclusion was a note-text match, and it deleted
  six real providers.** A per-invocation product publishes `vcpu_h: 0` with a
  real `ram_gib_h`, which the model read as "CPU is free, memory costs
  $0.06/GiB-h" — pricing a per-millisecond invoker as if it were a 1 vCPU / 1 GiB
  box billed by the hour. The first fix searched the mode's note for `requests`
  and `GB-s`. That dropped **36 modes across 23 cards**, including **Lizard,
  Railway, Kernel, Sail, CreateOS and InstaVM**, every one of which bills per
  second of running time and is a real sandbox. `requests` also matches
  Kubernetes *resource* requests (`gke-agent-sandbox`, `google-agent-engine`),
  inbound HTTP requests (`deno-sandbox`, `sail`, `sandbox0`) and the phrase "no
  requests" (`azure-container-apps`); `GB-s` is per **second**. The test that
  works is structural: a mode is per-invocation only if it publishes **no
  positive hourly rate anywhere**, and a note names the unit. Every exclusion is
  now listed in `data/period-model.json` under `per_request_modes_skipped`
  rather than dropped silently.
- **Bug 8: the guard suite could not run, which is why 5 to 7 shipped.**
  `61-period-model-guards.py` hardcoded `ROOT = '/workspace/peli-cloud'`, so on
  any other clone it raised `FileNotFoundError` before executing a single
  assertion. The exit code was nonzero, but the failure was a traceback with no
  `FAIL` lines, so a run log showed a red exit and nothing to act on. Every
  other script in `experiments/` derives `ROOT` from `__file__`; `61` was the
  only one that did not. Fix: derive it the same way, and exit **2** with a
  message when no tree is found, which is this repo's code for "could not run"
  and is distinguishable from a guard failure at a glance.

### 5.5 A licence problem, and a price that was double the vendor's

Both found by reading a **parallel independent implementation** of the same
corpus (`Nemo-010/peli-cloud`, 8 commits, its own `tools/rank.py` and
`research/tools/derive.mjs`) rather than by re-reading my own output. It reached
the same corpus with a different model and found two things about mine.

- **Bug 9: I was redistributing an unlicensed corpus under 0BSD.**
  `ariana-dot-dev/battleships` publishes **no licence**:
  `gh api repos/ariana-dot-dev/battleships --jq .license` returns `null` and
  `gh api repos/ariana-dot-dev/battleships/license` returns 404, and its tree
  has no `LICENSE` file. This repository committed all **1183** of its files
  (13 MB) inside a project whose `LICENSE` grants anyone anything. That is a
  grant of redistribution rights over somebody else's work that nobody granted,
  and the `0BSD` line in the README implied the whole tree was mine to give
  away. Fix: the corpus is no longer committed. It is a build input, restored by
  `10-fetch-corpus.sh` at the pinned commit, and `.gitignore` keeps it out. The
  cost is stated in `NOTICE`: every figure in the catalogue becomes
  *checkable* rather than *diffable*, and if upstream is rewritten the pinned
  commit becomes unreachable and the inputs are gone.
- **Bug 10: Lizard was priced at double the vendor's advertised rate.** The card
  (`research/cards/lizard.json`, mode `sandbox`) carries **one** size, `medium`
  at 4 vCPU / 4 GiB / $0.018/h, and pins `min_vcpu: 4`, so no shape below 4 vCPU
  can be priced at all. The **same card's note** quotes the vendor's FAQ:
  *"Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at
  $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour."* The cheapest
  advertised machine was in the card as prose and absent from its data. I
  re-fetched `lizard.build/pricing` on 2026-10-02 and the sentence is still
  there, word for word, so the rate is the vendor's own and my table was
  charging twice for the same class of machine: **$5.40/month at 10 h/day
  against $2.70**, which is second only to Agent 37. Fix: an explicit
  `ADVERTISED_SIZES` table in `70-period-model.py` carrying the URL, the quote
  and the conflict, consulted before the card's size table. A regex that scraped
  sizes out of note prose was considered and rejected: it matched one card and
  would have been a fragile way to turn prose into prices.
  **This is a correction, not a confirmation.** `lizard.build/docs` says create
  options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB
  rather than 8 GB, so the two first-party pages contradict each other and
  `lizard.build/changelog` renders *"Couldn't load this page."*, which dates
  neither. Every affected row is therefore marked **`disputed`** in the
  catalogue's "buy it?" column and the conflict is printed under the table. If
  the docs are right, the row goes back to $5.40.

## 6. Independent cross-check against the upstream engine (the control)

### 6.1 What the parallel implementation does better, and what it does worse

`Nemo-010/peli-cloud` re-priced the same 366 cards at the same pinned commit
with a different model and its own code (`tools/rank.py`,
`research/tools/derive.mjs`). It found the two defects in section 5.5, which is
the strongest evidence in this document, because they were found by a different
model rather than by re-reading my own output. It is also wrong in ways worth
recording, since the comparison is more useful than either side alone.

**What it does better.**

- **A per-request session model instead of a duty-cycle multiplier.** It prices
  each horizon as the cheapest split into sessions of at least 30 minutes, so a
  provider with an 8-hour session cap still appears with a note saying restarts
  are needed. My model multiplies a rate by hours and never asks how those hours
  are delivered, so a session-capped provider is priced as though the cap did
  not exist. Mine is the arithmetic; its is the closer approximation of how a
  sandbox is actually used.
- **It checks the 13 pages it re-fetched against the card, one at a time, with
  quotes and a verdict per provider** (`research/verification/2026-10-02.md`).
  Mine checks 19 with a numeric matcher, and section 0 records that the matcher
  was measuring formatting rather than prices until it was made unit-aware.
- **It quantified a free *allowance* rather than a free *credit*.** Oracle's
  Always Free Ampere A1 covers 1,500 OCPU-h + 9,000 GB-h a month, which covers
  this shape even 24/7, so the honest Oracle row is $0, not the $7.41 I publish.
  My model applies `monthly_credit` and nothing else, so that row is wrong by
  the largest single amount in either catalogue. **This is a known gap in my
  line and I have not fixed it**, and it is a structural one: `oracle-cloud.json`
  carries `"free": {"monthly_credit": 0, "one_time_credit": 300}` and **no
  allowance field exists anywhere in the corpus**, so an allowance is not merely
  unmodelled, it is unrepresentable without inventing a field and converting an
  allowance into dollars at the provider's own rate table. The correct fix is a
  separate allowance model priced per resource-hour, not a discount on the
  dollar credit.

**What it does worse.**

- **It ranks on the credit-adjusted price, and publishes `$0` rows.** Kedge is
  `$0` at 1 h, 10 h, 1 day and 1 week, and rank 3 in its sandbox table, because
  its $5 monthly credit exceeds those bills. The true cost of Kedge at 1 h is
  about $0.03. Azure Container Apps is rank 5 at $3.60 for the same reason and
  Google Cloud Run rank 7 at $4.36. It applies the credit inside the upstream
  engine and **never preserves the pre-credit figure**: `total_no_credit` appears
  nowhere in its committed `data/usage.json`, so it cannot rank on it even in
  principle. That is bug 5 in this document, which I fixed in my own line
  before reading its work.
- **Its README cites `data/derived.json` three times, including as the place to
  find `total_no_credit`, and that file is not committed.** `tools/rank.py`
  reads it, so the published catalogue depends on an artefact a reader cannot
  obtain without re-running its whole toolchain.
- **A `$0` in its "cheapest at each horizon" table is a credit artefact.** The
  1 h column lists "Amika $0, Anchor Browser $0, Azure $0", which reads as
  three free sandboxes and is one free tier plus two credits.

**Neither of us is right about the shape of this market.** Mine publishes 3
shapes x 4 duty cycles and one comparison shape; its own README says plainly
that it is "a shape ranking, not a fit ranking" and that required features are
not applied. Both inherit every error in one corpus at one commit.

A ranking that is one model's opinion is a survey. I re-priced the same 366
cards with battleships' **own** `site/engine.js`, in two modes, on the same day:

- **strict** (`PM.priceCard`): no relaxation, no spot, no negotiation, no term
  commit. Same question my model asks.
- **soft** (`PM.priceSoft`): relaxes spot / sales / term / capped-shape / region
  until a row prices, and labels the relaxation.

Result on 2026-10-02:

- The engine prices **164** cards strict, **218** soft. **Relaxation alone buys
  54 more providers (33% more than the strict set)** — that is the price of
  "you have to accept a spot instance or negotiate to use this provider".
- Against my model, strict: **142 priced by both**, **69 only by peli-cloud**,
  **22 only by the engine**, 133 by neither.
- The 22 "engine only" are, without exception, **browser-session and
  web-scraping products** (Browserbase, Browserless, Firecrawl, ZenRows, and
  similar). These sell minutes of a remote browser or a scraping API, not
  general machines. I excluded them by design; the engine includes them. This is
  a **definitional difference, not an error on either side**, and it is the
  clearest single illustration of what "provider" has to mean for a question
  like this.
- The 69 "peli-cloud only" are mostly **Windows and macOS-only** cards (the
  engine's default workload is Linux-only) and **alt-regime** prices (spot,
  term commits, burstable) that my two-tier model now records separately rather
  than folding into the headline.

So the cross-check does not "confirm" my ranking; it **localises** exactly where
the two definitions of the question part company, and every part-company row is
explained. That is the strongest form of agreement available here, because the
two models were built independently and the residual is not noise.

---

## 7. Three defects in the corpus, found by auditing rather than reading

These came out of revision 2's own checks and none of them is a judgement call
about pricing. Each names the file and the line of evidence.

### 7.1 A pre-launch price was ranking a provider 6x under its live rate

`research/cards/arker.json` carries six modes. The two cheapest are
`eu-hetzner-proposed` at **$0.0302/h** and `eu-scaleway-proposed` at $0.0310/h.
Its live on-demand mode on the same card is **$0.1877/h**. arker was carrying a
top-20 row in revision 2 on a region that does not exist yet.

leap0's only mode is `preview`, and after the fix it correctly has no price at
all. computeruse-cloud's only rate-bearing mode is
`unavailable-preview-active-second-offering`, same outcome. Six modes across
four cards name a pre-launch region or offering; all six are now skipped and
listed in `data/period-model.json` under `prelaunch_modes_skipped`.

**Verdict: confirmed.** The trigger is a mode key containing `proposed`,
`preview`, `soon`, `coming`, `waitlist`, `upcoming` or `unavailable`; the wrong
result is a ranked row on a price no buyer can be charged.

### 7.2 Thirty-four of the eighty-six "unpriced" cards are not unpriced

Revision 2 wrote that the 86 cards with no rate were "a vendor choice, not a gap
in the corpus", generalised from three pages I happened to check (ainclave,
bytebot, butter). Re-probing all 86 with `experiments/95-reprobe-unpriced.py`
refuted that. The honest split:

| verdict | cards | meaning |
|---|---|---|
| no dollar figure on the page | 45 | the corpus is right |
| unreachable at the card's url | 7 | no verdict either way |
| **publishes a machine rate the card never captured** | **20** | **the corpus card is wrong** |
| dollars present, but not a machine rate | 14 | ambiguous, left ambiguous |

BuildJet is the clearest case: it publishes **$0.004/min for 2 vCPU / 8 GB**,
$0.008, $0.016, up to $0.128, and the card records no rate at all. Artillery
publishes $0 / $199 / $499 plans. Also in the 20: Brimble, Clusy, Dexto, Isle,
Nodus Compute, Server4Agent, PaperPod, Party, Metorial, Dockup.

None of the 20 were re-priced here. Turning a marketing page into a card is
implementation work, and a guessed rate is worse than a visible gap because
nobody can check it.

**Verdict: confirmed for the 20, refuted for my own revision 2 claim, plausible
for the 14.** A second pass that classifies each of the 20 by hand would settle
which are per-machine and which are per-seat.

### 7.3 The exclusion count was understated by an order of magnitude

Revision 2's table D said "11 cards could not be priced". The ledger over all
366 cards found 148 cards missing from the ranking. The 11 was the count after
a category filter, not the count of what was missing, and it is exactly the kind
of number that reads as complete. All 366 are now accounted for in
`data/exclusion-ledger.json` and rendered in table D:

| status | cards |
|---|---|
| ranked at all three shapes | 197 |
| ranked for some shapes | 9 |
| gpu-only | 15 |
| pre-launch only | 2 |
| priced but only for larger machines | 16 |
| no rate in the card | 86 |
| off-category (browser, scraping, non-compute) | 41 |
| **total** | **366** |

---

## 8. What the corpus's own verify notes say that I did not read

The corpus ships 45 hand-verification notes under `research/verify/`, one per
provider, each recording what was re-fetched, what was corrected and what could
not be verified. **Revisions 1, 2 and 3 never opened them.** Reading them found a
defect that changes published entry prices, and confirmed two findings I had
reached independently.

### 8.1 A `$0` tier that blocks usage was being sold as a `$0` entry price

`upstash-box.md`: *"the Free tier is a hard cap (usage blocked, not billed), but
the engine would pick it as 'PAYG minus $0.50'... Added `trial_only: true` so it
is never auto-picked."* The card already carries the flag. My model never read
it, so it treated any `$0` plan as a free entry.

16 cards mark a plan `trial_only`. Six of them changed materially once excluded:

| provider | was shown as | is actually | excluded tier |
|---|---|---|---|
| Replit | $0 | **$18** | Starter (free) |
| Rivet | $0 | **$20** | Free |
| Vercel Sandbox | $0 | **$20** | Hobby |
| boat | $0 | **$20** | Trial |
| CodeSandbox SDK | $0 | **$12** | Build (free) |
| Tensorlake | $0 | **$250** | Free, Usage Credits (prepaid) |

Every row now also names the plan it was priced from, so a `$0` entry can be
checked against the tier that produces it. runloop is the instructive
counter-example: its `Basic` plan is a genuine `$0` paid tier next to a `$250`
`Pro`, so it stays at $0.

**Verdict: confirmed.** Trigger is `trial_only: true` on a plan; wrong result is
a $0 entry price on a tier that blocks usage or expires.

### 8.2 Two findings the notes independently confirm

- `arker.md` describes the EU rows as *"proposed prices, not currently
  published offers"*, which is the same conclusion revision 3 reached from the
  mode key alone. Two independent routes to one finding.
- `hetzner-cloud.md` quotes the billing FAQ: *"always round up the hourly
  usage"*, *"never exceed its monthly price cap"*, and powered-off servers are
  billed. That confirms both halves of what section 8 of the catalogue now
  shows: the one-hour granularity and the `keep = 1.00`.

### 8.3 A modelling limit these notes expose

Koyeb's card distinguishes eco instances, which *"scale to zero via deep sleep
only"*, from standard types, which light-sleep. This model has one keep rate per
mode, so it cannot express a graduated sleep policy, and it has no
`light_sleep_enabled` field to read. Koyeb is not in the ranked set so nothing
published here is affected, but a provider with two sleep tiers would be
mistranscribed: the cheaper tier would be recorded as fully billed.

**Verdict: plausible, not confirmed.** Koyeb would need a real card to test it
against and is not priced here.

---

## 9. Coverage check against the wider market (a real negative result)

The task said the corpus may not cover all providers and to research widely.
I searched for providers the corpus might miss and **found none that the corpus
lacks**, within the reach of general web search:

- Three independent 2026 roundups of agent-sandbox providers (Upstash's, Mastra's,
  ajayk.sh's) name: Upstash Box, E2B, Daytona, Modal, Cloudflare Sandbox, Vercel
  Sandbox, Northflank, Runloop, Freestyle, Fly.io, PandaStack, Mastra itself.
  **All are in the corpus.**
- Direct queries for "scaleaway" (the operator's third named example) return no
  such compute provider; see section 4.

**What would have made this check fire:** a long-tail provider with no
first-party page that a roundup did not name, or a regional provider (for
example a Chinese or Indian sandbox) that English-language roundups skip. Search
reach here is Brave, plus direct fetches; DuckDuckGo, Bing, Mojeek and Startpage
all served bot-challenges or captchas from this host, so the "research widely"
step is bounded by what one working search index can see. Assume more providers
exist than these three roundups and the corpus surface; assume fewer are
*missing from it* than the roundups suggest.

---

## 10. What the proof of concept does and does not handle

`experiments/` and `data/` are the instrument. Concretely:

- `10-fetch-corpus.sh` re-fetches the corpus at the pinned commit and says what
  it could not get.
- `20-extract-provider-universe.py` extracts every card from primary fields only.
  It never calls the upstream engine (that would be the subject grading itself).
- `70-period-model.py` prices three shapes at four duty cycles and records the
  keep rate, the minimum billable unit and the subscription floor per provider.
- `80-render-catalogue.py` renders the four tables every row of which links to
  the provider's own page.
- `30-rank-providers.py` is revision 1's single-workload ranking. It is kept, and
  still runs, because `40` cross-checks against the upstream engine using the
  same shape of question; but it is superseded by 70/80 for ranking purposes.
- `90-exclusion-ledger.py` assigns every one of the 366 cards a status and a
  reason, and fails if they do not add up to 366.
- `95-reprobe-unpriced.py` re-fetches the providers the corpus says are unpriced
  and separates "publishes nothing" from "publishes a rate the card missed".
- `40-crosscheck-engine.py` re-prices with the upstream engine (strict and soft)
  and localises the disagreement.
- `50-firstparty-audit.py` re-fetches vendor pages for a named sample and
  reports agreement, disagreement, and unreadable pages honestly.

The guard-mutation review is a file, so a later session can re-run it rather than
re-derive it: `experiments/60-guard-mutation.py`.

**Not handled:** no vendor signup was performed, so no *purchase* path, no
realised price and no real concurrency limit is verified. Free-credit figures
are as published, never redeemed. Region availability and network allowlists are
recorded per card but not re-fetched for every provider. The tables do not price
egress, storage overage, IPv4 or seats at scale. **No sandbox was actually
started and stopped**, so every keep rate is a reading of a published feature
flag, not a measurement. Concurrency and bursty-agent behaviour (the
`min_billed_seconds` penalty) are recorded per provider but not modelled into
the period figures.

---

## 11. The exact commands

Run from the repo root, in order:

    bash   experiments/10-fetch-corpus.sh
    python3 experiments/20-extract-provider-universe.py
    python3 experiments/70-period-model.py          # shapes x duty cycles
    python3 experiments/90-exclusion-ledger.py     # all 366 accounted for
    python3 experiments/80-render-catalogue.py      # the four tables
    python3 experiments/95-reprobe-unpriced.py      # re-probe the unpriced cards (network)
    python3 experiments/40-crosscheck-engine.py     # needs node on PATH
    python3 experiments/50-firstparty-audit.py      # needs network
    python3 experiments/60-guard-mutation.py
    python3 experiments/61-period-model-guards.py

Each prints its conditions (date, corpus commit, workload, model) and writes a
JSON artefact under `data/`. Numbers in this document came from those runs on
2026-10-02; re-running on a later day re-prices the same corpus against that
day's vendor pages and may differ.