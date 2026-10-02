# peli-cloud — findings

**Question.** Every cloud sandbox, VM, dev-env and agent-runtime provider a buyer
can actually reach, catalogued and sorted cheapest-first, with the caveats that
stand between the headline price and the workload: prepay minimums, tier
ladders, stock limits, free-credit structure, and the two providers the operator
named that the corpus may not carry.

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
- **The ranking model is mine, and it is a simplification.** It prices one
  stated workload (below). It excludes always-on cost, egress, storage beyond
  what a card bundles, IPv4, and team seats. A provider cheap on this workload
  can be dear on another. The full corpus cards carry those fields; this table
  does not price them.
- **"Cheapest" means cheapest for the stated workload only**, not cheapest
  provider, best provider, or best value.
- **A previous revision's error rate is unknown to me** because this is revision
  one. Assume more remain. I found and fixed **four** real measurement defects
  in my own first run (two `$0/hour` bugs at different layers, a shape mismatch,
  and a regression I introduced while fixing the second), all described in
  section 5. That is the honest estimate of how many are still wrong: four were
  found by reading the output and by planting one case, so more are likely.

---

## 1. The workload the ranking is priced against

    2 vCPU / 4 GiB RAM / 20 GiB disk
    300 sessions a month, 10 minutes each   (= 50 machine-hours)
    nothing running 24/7, one seat, no GPU, open internet

This is stated because "cheapest provider" has no answer on its own. Change the
workload and the ranking changes: a 24/7 workload is dominated by different
plans, a 100-concurrency workload by fleet caps, a GPU workload by a different
table entirely.

---

## 2. The honest answer first

**The single cheapest thing to run that workload is not an agent-sandbox
provider; it is Scaleway's Stardust instance at about $0.03 a month** — a
1 vCPU / 1 GiB shared "tiny" VM, stock-limited, with no sandbox API. It is the
right answer only if you can live with 1 GiB, an always-on hourly meter and no
agent-sandbox ergonomics.

**The cheapest actual agent-sandbox on this workload is about $0.30 a month
(Agent 37) and $0.69 (zipbox); Lizard and boat both come out at about $0.90.**
The big-name per-resource sandboxes (E2B, Daytona) price at about $8.28 a month
for the same 50 hours, because they bill $0.0504 per vCPU-hour and $0.0162 per
GiB-hour, which is roughly 9x the effective rate of the size-based sandboxes for
a 2-vCPU box.

That gap is the single most useful thing in this pass: **per-resource pricing
and preset-size pricing are different products with very different totals at
small shapes.** The size-based vendors win on a small box; the per-resource
vendors win when the shape is big, when you burst, or when you need fine RAM
granularity.

**There is no large recurring free-credit tier anywhere in the corpus.** 13 of
366 cards publish any recurring monthly credit, and the largest is Modal at
$30/month. The operator's caveat ("some are expensive but offer large free
monthly credits") does not survive contact with the corpus as *recurring* credit:
the large credits ($200-$300) are all **one-time signup credits** that never
recur. A buyer who treats a $300 Google/AWS/Azure signup credit as "free
forever" is wrong; it is free once.

**The cheapest rows are full of trial-tier prices, and that is the biggest trap
in the table.** boat's $0.90 is the arithmetic of its **Trial** plan: $0 fee,
2 concurrent sandboxes, a one-time $0.90 credit, and the card's own condition
reads "auto-converts to the chosen paid plan after 7 days unless cancelled".
The next tier up is **$20/month** for 100 concurrent. So the operator's "$20
subscription upfront" instinct is right about boat, and the $0.90 in this table
is a seven-day number wearing a monthly label. The same pattern runs through the
rows above it: read `entry fee` and `tier`, not just the all-in column.

**What a prepay or minimum actually costs, per row,** is carried in
`data/ranking-cheapest-first.json` as `platform_fee_month_usd`,
`min_commit_month_usd` and `entry_plan`. For the rows where the cheapest
published regime is a prepay, a minimum top-up or a negotiated contract, the
`compromises` column says so in words. Three tiers exist and never blend: a
`self-serve` row is one a new account can buy at that price with no
negotiation; a `not-self-serve-only` row means the cheapest published regime is
spot, a term commit or a sales conversation.

---

## 3. The ranking (self-serve and not-self-serve both shown)

Full 211-row table with per-row free-credit structure, tier and the exact mode
it was priced by: [`data/catalogue-ranked.md`](data/catalogue-ranked.md). The top
40:

| # | provider | category | isolation | all-in $/mo | rank in full table | free | tier |
|---|---|---|---|---|---|---|---|
| 1 | Scaleway Instances (Stardust 1C/1G) | hyperscaler | vm | 0.03 | 1 | - | self-serve (stock-limited) |
| 3 | Agent 37 | agent-sandbox | gvisor | 0.30 | 3 | $1 once | self-serve |
| 4 | IBM Cloud VPC (burstable) | hyperscaler | vm | 0.33 | 4 | $200 once | self-serve |
| 5 | Oracle Cloud (burstable) | hyperscaler | vm | 0.46 | 5 | $300 once | self-serve |
| 7 | zipbox | agent-sandbox | firecracker | 0.69 | 7 | $25 once | self-serve |
| 9 | boat.dev | agent-sandbox | vm | 0.90 | 9 | $1 once | self-serve |
| 10 | Lizard | agent-sandbox | container | 0.90 | 10 | $10 once | self-serve |
| 12 | shellbox | agent-sandbox | firecracker | 1.00 | 12 | - | self-serve |
| 19 | Koyeb Sandboxes | agent-sandbox | vm | 1.44 | 19 | - | self-serve |
| 23 | Together Code Sandbox | agent-sandbox | firecracker | 1.50 | 23 | - | self-serve |
| 28 | Fly.io Machines | paas | firecracker | 1.76 | 28 | - | self-serve |
| 39 | AWS EC2 (on-demand) | hyperscaler | vm | 2.46 | 39 | $100 once | self-serve |
| 94 | Freestyle | agent-sandbox | bare-metal-vm | 6.61 | 94 | $18.38/mo credit | self-serve |
| 112 | Daytona | agent-sandbox | container | 8.28 | 112 | - | self-serve |
| 115 | E2B | agent-sandbox | firecracker | 8.28 | 115 | - | self-serve |

The rows for E2B and Daytona are not an omission; they sit far down the table at
their true $8.28. They are called out because "cheapest" and "well-known" point
at different providers. Freestyle at rank 94 is the clearest case of a provider
whose free credit is real and fully documented and which is still **not** cheap,
because its $18.38 of allowance is non-fungible: a 2-vCPU box at $0.04032/vCPU-h
cannot spend a $0.04032/hour credit faster than it burns it, so the credit buys
roughly 460 vCPU-hours against a 50-hour workload and the rest expires.

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

## 6. Independent cross-check against the upstream engine (the control)

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

## 7. Coverage check against the wider market (a real negative result)

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

## 8. What the proof of concept does and does not handle

`experiments/` and `data/` are the instrument. Concretely:

- `10-fetch-corpus.sh` re-fetches the corpus at the pinned commit and says what
  it could not get.
- `20-extract-provider-universe.py` extracts every card from primary fields only.
  It never calls the upstream engine (that would be the subject grading itself).
- `30-rank-providers.py` applies the stated workload and emits the two-tier
  ranking.
- `40-crosscheck-engine.py` re-prices with the upstream engine (strict and soft)
  and localises the disagreement.
- `50-firstparty-audit.py` re-fetches vendor pages for a named sample and
  reports agreement, disagreement, and unreadable pages honestly.

The guard-mutation review that produced defects 3 and 4 is a file, so a later
session can re-run it rather than re-derive it: `experiments/60-guard-mutation.py`.

**Not handled:** no vendor signup was performed, so no *purchase* path, no
realised price and no real concurrency limit is verified. Free-credit figures
are as published, never redeemed. Region availability and network allowlists are
recorded per card but not re-fetched for every provider. The model does not
price egress, storage overage, IPv4 or seats at scale.

---

## 9. The exact commands

Run from the repo root, in order:

    bash experiments/10-fetch-corpus.sh
    python3 experiments/20-extract-provider-universe.py
    python3 experiments/30-rank-providers.py
    python3 experiments/40-crosscheck-engine.py     # needs node on PATH
    python3 experiments/50-firstparty-audit.py      # needs network

Each prints its conditions (date, corpus commit, workload, model) and writes a
JSON artefact under `data/`. Numbers in this document came from those runs on
2026-10-02; re-running on a later day re-prices the same corpus against that
day's vendor pages and may differ.