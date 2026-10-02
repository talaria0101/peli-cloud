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
  per day are chosen round numbers. A real agent's distribution is not uniform,
  and a provider with a high minimum billable unit may bill far more than
  `hours x rate` for a bursty agent. The `min_billed_seconds` column in
  `data/period-model.json` carries that, and nothing in the tables adjusts for it.
- **This is revision 2, and revision 1 was wrong in seven documented ways**
  (section 3). The largest: it priced stoppable sandboxes as fixed monthly hosts,
  which is the VPS comparison this task is not asking for. Revision 1 had also
  fixed four of its own measurement defects before publication (section 5).
  **That is the honest estimate of what is still wrong here:** at least seven
  things were wrong in a document that read as finished, cited and reviewed, and
  I found them only when the model itself was questioned. Assume more remain.

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
- `70-period-model.py` prices three shapes at four duty cycles and records the
  keep rate, the minimum billable unit and the subscription floor per provider.
- `80-render-catalogue.py` renders the four tables every row of which links to
  the provider's own page.
- `30-rank-providers.py` is revision 1's single-workload ranking. It is kept, and
  still runs, because `40` cross-checks against the upstream engine using the
  same shape of question; but it is superseded by 70/80 for ranking purposes.
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

## 9. The exact commands

Run from the repo root, in order:

    bash   experiments/10-fetch-corpus.sh
    python3 experiments/20-extract-provider-universe.py
    python3 experiments/70-period-model.py          # shapes x duty cycles
    python3 experiments/80-render-catalogue.py      # the four tables
    python3 experiments/40-crosscheck-engine.py     # needs node on PATH
    python3 experiments/50-firstparty-audit.py      # needs network
    python3 experiments/60-guard-mutation.py

Each prints its conditions (date, corpus commit, workload, model) and writes a
JSON artefact under `data/`. Numbers in this document came from those runs on
2026-10-02; re-running on a later day re-prices the same corpus against that
day's vendor pages and may differ.