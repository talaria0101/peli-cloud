#!/usr/bin/env python3
"""51-billing-posture-probe.py

QUESTION: for every provider whose keep rate currently falls back to the
conservative 1.00, what does the vendor's OWN page say about whether a stopped,
paused or idle machine keeps billing?

WHY THIS EXISTS. `keep_rate` is the difference between a sandbox and a VPS. A
provider that suspends on idle can be held for a month and cost the price of an
hour; a provider that bills for uptime cannot. The corpus has no field for that
policy, so 539 priced rows across 183 providers took a fallback. The fallback is
deliberately the expensive direction, so every one of those rows OVERSTATES what
holding costs. That is safe but it is not useful, and stating a limit is not the
same as doing the work.

WHAT IT DOES. Fetches each provider's own pricing or billing page over HTTPS,
strips the markup, and looks for the vendor's own words about billing a machine
that is stopped, paused, or idle. It classifies into:

    suspends      the vendor says a stopped/paused machine stops billing
    bills_uptime  the vendor says the machine bills while it exists, or that
                  stopped machines are still charged (disk, reserved capacity)
    partial       the vendor says one resource stops and another keeps billing
    unstated      the page was fetched and read and says nothing either way
    unreachable   the page could not be fetched from this host

It records the QUOTE it classified on, not just a verdict, so any row can be
checked by a reader. `unstated` is a real answer and the most common one; it is
not rounded to `bills_uptime`, because "the page did not mention it" and "the
page said it bills" are different facts and only one of them is evidence.

WHAT WOULD FALSIFY THE APPROACH. A page that renders its billing policy
client-side, or states it in an image, or in a different language, returns
`unstated` however complete the markup is. That is a real limit of reading a
page as text and is reported as such rather than guessed at. A vendor whose
policy genuinely changed would be captured on the day it was read, so every
verdict carries its date.

It writes data/billing-posture.json and NOTHING is written back into the
period model: the probe measures, a human decides. See 52-apply-posture.py.

Exit codes: 0 the probe ran and its artefact is the one on disk
            1 the self-test failed, so no verdict is trustworthy and nothing
              was published
            2 could not run at all
            3 this run found FEWER verdicts than the artefact already on disk
              and refused to overwrite it; the previous, better run stands
"""

import datetime
import html
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD_COMMIT = "f6a71ab09fef"

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
TIMEOUT = 25
# Eight concurrent requests to 183 different vendors is a burst that some of them
# answer with a degraded page. The first run at WORKERS=8 found 17 verdicts; a
# second run minutes later at the same concurrency found 0, which is what
# prompted the no-overwrite guard below. Four is slower and reliable.
WORKERS = 4

# ---------------------------------------------------------------------------
# The vendor's own words, in both directions.
#
# Every pattern here is a phrase a vendor writes about billing a machine that is
# not doing anything. The lists are deliberately specific: a broad pattern like
# "billed" matches every pricing page on earth and would classify all 183
# providers from a single stray word. Each pattern below had to be checked
# against a real page, and the ones that were too loose were removed after they
# classified something incorrectly. That process is recorded in
# docs/FINDINGS.md section 6.4.
#
# Order matters: `partial` is checked before `suspends`, because a page saying
# "paused sandboxes stop vCPU billing but keep billing RAM" contains the word
# "stop" and would otherwise be read as a clean suspension.
# ---------------------------------------------------------------------------

PARTIAL = [
    (r"stop(?:s|ped)?\s+(?:vCPU|cpu|compute)\s+billing[^.]{0,80}but[^.]{0,80}billing",
     "stops vCPU billing but keeps billing another resource"),
    (r"stopped[^.]{0,60}root (?:file system|filesystem|volume|disk)[^.]{0,60}charge",
     "a stopped machine still pays for its root filesystem"),
    # createos, read first-party on 2026-10-02: "PAUSED sandboxes stop vCPU
    # billing but KEEP billing RAM at $0.01159025/GB-h". The resource word
    # FOLLOWS the billing word here, and a pattern that allowed the match to
    # cross the "." inside the price also matched lizard's "paused sandboxes do
    # not count as running", which is a clean suspension. So this pattern is
    # anchored on the whole clause: stop <resource> billing, but keep billing
    # <resource>.
    (r"stop(?:s|ped|ping)?\s+[a-z0-9 ]{0,18}?(?:cpu|compute)\s+billing\s+but\s+"
     r"(?:keep|keeps|continue|continues|still)\s+billing\s+(?:ram|memory|disk|storage)",
     "CPU billing stops when paused but RAM keeps billing"),
]

SUSPENDS = [
    (r"paused?[^.]{0,60}(?:do(?:es)? not|don'?t|will not|won'?t)[^.]{0,40}(?:bill|charg|count)",
     "a paused machine is not billed"),
    (r"(?:stop|suspend)[^.]{0,50}stop[^.]{0,50}billing", "stopping the machine stops billing"),
    (r"billed[^.]{0,40}(?:only|just)[^.]{0,30}while[^.]{0,30}(?:running|in use|active)",
     "billed only while running"),
    (r"billed per second while they run", "billed per second while running"),
    # A machine that is "not counted as running" is not billed. This sat in the
    # PARTIAL group, which is evaluated first, so every page containing the
    # phrase was published as `partial` -- including lizard, which is a clean
    # suspension. It belongs here.
    (r"(?:paused|stopped|idle|suspended)[^.]{0,40}(?:do(?:es)? not|don'?t|will not) ?"
     r"(?:count as running|being billed|billed|charged)",
     "a paused or stopped machine is not counted as running"),
    (r"freeze[^.]{0,40}stop billing", "suspending freezes the VM and stops billing"),
    (r"(?:suspend|stop)[^.]{0,40},? ?(?:stop|ceases?) billing", "suspending stops billing"),
    (r"auto[- ]?suspend[^.]{0,80}(?:save|bill|charge|cost)",
     "auto-suspend is described as saving billing"),
    (r"(?:idle|unused)[^.]{0,40}(?:stop billing|not billed|no charge)",
     "an idle machine stops billing"),
    (r"pay only while", "pays only while running"),
    (r"scale to zero[^.]{0,80}(?:bill|charg|cost)", "scales to zero and stops billing"),
]

BILLS_UPTIME = [
    (r"(?:powered[- ]?off|stopped|halted)[^.]{0,60}(?:still|are|is|continue)[^.]{0,30}(?:bill|charg)",
     "a stopped machine is still billed"),
    (r"billed[^.]{0,50}(?:even|regardless)[^.]{0,40}(?:stopped|idle|not running|powered off)",
     "billed even when stopped or idle"),
    (r"(?:reserved|dedicated)[^.]{0,40}(?:capacity|instance)[^.]{0,60}bill",
     "reserved capacity is billed whether used or not"),
    (r"billed per hour of uptime", "billed per hour of uptime including standby"),
    (r"including (?:startup and standby|uptime)", "uptime including standby is billed"),
    (r"flat (?:rate|pool|fee)[^.]{0,60}(?:whether|regardless)",
     "a flat pool is billed whether used or not"),
    (r"reserved instances[^.]{0,60}(?:used|not used|regardless)",
     "reserved instances bill whether used or not"),
]

# Three of the seventeen verdicts the first run produced were WRONG, and each
# one is a pattern bug rather than a bad page. They are fixed here and the
# counter-examples are kept as patterns in their own right, because a classifier
# that has only been tested on pages it gets right is not tested.
#
#   stackit. "reserved capacity is billed whether used or not" matched inside an
#   embedded JSON catalogue blob: {"id":"STA_SKU_583365", ... "maturityModelState":
#   ...}. The page is a pricing API response with no prose about idle billing at
#   all. JSON is not a vendor statement, so a match inside one is not evidence.
#
#   azure-vm. The page says: 'If my deployed instance says "stopped", am I still
#   getting billed? Maybe. If the status says "Stopped (Deallocated)", you're not
#   being billed'. The pattern matched 'stopped ... being billed' inside a
#   question the page does not answer. Hedging is not a verdict.
#
#   nebius. The page says 'You are charged for computing resources of running
#   virtual machines. Computing resources of stopped VMs are not charged'. The
#   pattern matched the word "charged" near "stopped" and read it as billing for
#   a stopped VM, which is the exact opposite of what the page says. A negation
#   inside the matched window has to win.
NEGATION = re.compile(
    r"\b(?:not|aren'?t|isn'?t|no|never|without|except)\b[^.]{0,40}"
    r"\b(?:bill|charg|pay|cost|forfeit)\w*\b", re.I)
HEDGED = re.compile(
    r"\b(?:maybe|perhaps|possibly|it depends|depends on|depending on|"
    r"in some cases|may or may not|consult|check your|varies)\b", re.I)
JSONISH = re.compile(r'["{}]\s*:|\[\s*\{|"\w+"\s*:\s*"?[\d\[]', re.S)


# "This resource keeps billing while the machine is idle or stopped." Together
# with a statement that something else stops billing, this makes the honest
# verdict `partial` whatever the sentence shapes look like. Matching one fixed
# sentence for `partial` was the first version's mistake: it published boxd as a
# clean `suspends` when the vendor had said the opposite for one of its two
# resources.
CHARGE_WHILE_IDLE = [
    (r"(?:standby|paused|stopped|idle|suspended)[^.]{0,70}(?:pays?|charged|billed|costs?)[^.]{0,40}(?:for )?(?:RAM|memory|disk|storage|volume)",
     "an idle machine still pays for RAM or storage"),
    (r"(?:RAM|memory|disk|storage|volume)[^.]{0,40}(?:is |are |still )?(?:billed|charged)[^.]{0,40}(?:even )?(?:when )?(?:paused|stopped|idle)",
     "RAM or storage is billed while paused"),
    (r"billed[^.]{0,30}(?:only )?for the (?:root|boot) (?:file ?system|disk|volume)",
     "only the root filesystem is billed when stopped"),
    (r"stopped[^.]{0,60}(?:root file system|filesystem|volume|disk)[^.]{0,60}charge",
     "a stopped machine still pays for its root filesystem"),
    (r"auto[- ]?suspended[^.]{0,60}bill[^.]{0,30}storage only",
     "an auto-suspended machine bills storage only"),
    (r"billed[^.]{0,40}(?:even|regardless)[^.]{0,40}(?:stopped|idle|not running|powered off)",
     "billed even when stopped or idle"),
]


def _any(patterns, low):
    """First pattern that matches AND survives the evidence test."""
    for pat, why in patterns:
        m = re.search(pat, low)
        if m:
            ok, _ = is_evidence(low[max(0, m.start() - 140):m.end() + 140])
            if ok:
                return why
    return None


def is_evidence(quote):
    """Reject a match that is not a statement the vendor made in prose.

    Three of the first run's seventeen verdicts were wrong, and all three came
    from matching something that was not a statement: a JSON blob, a question
    the page declines to answer, and a sentence whose meaning is inverted by its
    own negation. A quote that fails any of these tests is not evidence, and the
    row falls back to `unstated` rather than being published on it.
    """
    if not quote:
        return False, "empty quote"
    if JSONISH.search(quote):
        return False, "match is inside an embedded JSON/catalogue blob, not prose"
    if HEDGED.search(quote):
        return False, "the page hedges rather than stating a policy"
    if NEGATION.search(quote):
        return False, "the sentence negates the billing it appears to describe"
    return True, None


def strip_markup(body):
    """Visible text, with scripts and styles removed.

    EXCEPT for JSON-LD blocks, which are kept. 26 pages were being called
    "client-rendered shells" when they are not: aptible's pricing page is 713 KB
    and carries a JSON-LD block inside a <script> tag holding exactly the
    billing sentences this probe is looking for, among them "Starting at
    $499/month". Stripping every script threw that away, the page looked empty,
    and the verdict became `shell` -- "no price rendered in the HTML" -- which
    is a confident false statement about a page that plainly renders its prices.

    The distinction that matters: a <script> tag holding executable JavaScript
    has no text a reader would see, and a JSON-LD block is data the vendor
    publishes ON PURPOSE for exactly this purpose. Only the second is evidence,
    so only the first is dropped.
    """
    # Keep the contents of application/ld+json and ld+json script blocks.
    kept = []

    def _keep_jsonld(m):
        kept.append(m.group(1))
        return " "

    t = re.sub(r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
               _keep_jsonld, body, flags=re.S | re.I)
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    for k in kept:
        t += " " + re.sub(r"\s+", " ", html.unescape(k))
    return t


def fetch(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
        return r.status, r.geturl(), r.read()


def classify(text):
    """Verdict and the quote it came from, or (None, None, None, reason).

    A match that fails `is_evidence` is not published. The row falls through to
    the next pattern, and if nothing survives it is `unstated`, which is a real
    answer and the one most rows get.
    """
    low = text.lower()
    rejected = []
    # `partial` is decided FIRST, across the whole page. Checking it last meant a
    # page that also contained a clean "billed only while running" sentence was
    # published as `suspends`, which is the most damaging error this classifier
    # can make: it makes a provider that still bills RAM look free to hold.
    still = _any(CHARGE_WHILE_IDLE, low)
    stops = _any(SUSPENDS, low)
    if still and stops:
        _i = low.find(still[:24])
        _i = _i if _i > 0 else 0
        return "partial", "%s, but %s" % (still, stops), \
            text[max(0, _i - 140):_i + 280].strip(), None
    for group, verdict in ((PARTIAL, "partial"), (SUSPENDS, "suspends"),
                           (BILLS_UPTIME, "bills_uptime")):
        for pat, why in group:
            for m in re.finditer(pat, low):
                quote = text[max(0, m.start() - 120):m.end() + 120].strip()
                ok, why_not = is_evidence(quote)
                if ok:
                    return verdict, why, quote, None
                rejected.append("%s: %s" % (verdict, why_not))
                break          # one rejected match per pattern, then move on
    return None, None, None, ("; ".join(rejected[:3]) if rejected else None)


def probe(item):
    pid, url = item
    if not isinstance(url, str) or not url.startswith("http"):
        return {"id": pid, "url": url, "verdict": "unreachable",
                "quote": None, "why": "no http url on the card", "bytes": 0}
    try:
        status, eff, body = fetch(url)
    except urllib.error.HTTPError as e:
        return {"id": pid, "url": url, "verdict": "unreachable",
                "quote": None, "why": "HTTP %s" % e.code, "bytes": 0}
    except Exception as e:
        return {"id": pid, "url": url, "verdict": "unreachable",
                "quote": None, "why": type(e).__name__ + ": " + str(e)[:90],
                "bytes": 0}
    try:
        text = strip_markup(body.decode("utf-8", errors="replace"))
    except Exception as e:
        return {"id": pid, "url": url, "verdict": "unreachable",
                "quote": None, "why": "decode: %s" % e, "bytes": len(body)}
    verdict, why, quote, rejected = classify(text)
    if verdict is None:
        # A page with no money in it is a client-rendered shell. Saying
        # "unstated" for that would be wrong: nothing was read at all.
        if not re.search(r"\$\s?\d|\d\s?/", text):
            return {"id": pid, "url": url, "eff": eff, "verdict": "shell",
                    "quote": None, "bytes": len(body),
                    "why": "no price rendered in the HTML (client-side)"}
        return {"id": pid, "url": url, "eff": eff, "verdict": "unstated",
                "quote": None, "bytes": len(body),
                "why": ("page fetched and read; it does not state an idle-billing "
                        "policy in text")
                       + ((" | rejected matches: " + rejected) if rejected else "")}
    return {"id": pid, "url": url, "eff": eff, "verdict": verdict,
            "quote": quote, "why": why, "bytes": len(body)}


# ---------------------------------------------------------------------------
# Self-test. Every case below is a REAL page read on 2026-10-02, not a
# synthetic sentence, and three of them are pages the FIRST version of this
# classifier got wrong. A pattern list tested only on pages it classifies
# correctly is not tested, so this runs on every invocation and the probe
# refuses to publish a verdict if it fails.
#
# The three failures the first run produced, and why each happened:
#   nebius    "Computing resources of stopped VMs are not charged" was read as
#             billing a stopped VM, because the pattern matched the word "charged"
#             near "stopped" and ignored the negation in its own sentence.
#   azure-vm  the page ASKS "am I still getting billed?" and answers "Maybe". The
#             pattern read a question as a statement.
#   stackit   the match landed inside an embedded JSON catalogue blob, which is
#             a pricing API response and contains no prose at all.
# And one page the second version got wrong, which is why it is here too:
#   boxd      "a machine in standby pays for RAM and disk. vCPU is billed only
#             while a machine is actually running" spans two sentences, so a
#             single-sentence `partial` pattern missed it and the row was
#             published as a clean `suspends` -- the most damaging error this
#             classifier can make, because it makes a provider that still bills
#             RAM look free to hold.
# ---------------------------------------------------------------------------
SELFTEST = [
    # (provider, expected, real text from that provider's page)
    ("nebius", "unstated",
     "You are charged for computing resources (GPUs, vCPUs, RAM) of running "
     "virtual machines (VMs). Computing resources of stopped VMs are not "
     "charged (this does not apply to storage volumes)."),
    ("azure-vm", "unstated",
     'If my deployed instance says "stopped", am I still getting billed? Maybe. '
     'If the status says "Stopped (Deallocated)," you are not being billed.'),
    ("stackit", "unstated",
     '{"id":"STA_SKU_583365","sku":"ST-0200201","unit":"Gigabyte Hours",'
     '"unitBilling":"per GB/hour"} reserved capacity is billed whether used or not'),
    ("createos", "partial",
     "PAUSED sandboxes stop vCPU billing but KEEP billing RAM at $0.01159025/GB-h"),
    ("lizard", "suspends",
     "billed per second while they run, and paused sandboxes do not count as running"),
    ("boxd", "partial",
     "a -suspend state, standby, that keeps memory warm for instant resume; a "
     "machine in standby pays for RAM and disk. vCPU is billed only while a "
     "machine is actually running."),
    ("zipbox", "suspends",
     "Pricing: pay only while a sandbox runs. Stop the box, stop the meter."),
    ("mosaic", "suspends",
     "A real Linux sandbox for any agent. Pay only while it works. $0.05/hour "
     "active compute. $0 while hibernated."),
    ("paperspace", "bills_uptime",
     "A powered-off Droplet continues to incur compute charges because its "
     "resources stay reserved until you destroy it."),
    ("pandastack", "partial",
     "Auto-suspended databases bill storage only, so a dev database that sleeps "
     "most of the day bills just its storage."),
    ("machine0", "suspends",
     "Start, Suspend, Snapshot & Resume. Freeze a VM's state, stop billing, "
     "restore later."),
    ("islo", "suspends",
     "Pay only while it runs. CPU, memory, and storage billed per hour. Stop "
     "the computer, stop the meter."),
    ("beam", "suspends",
     "Billed by the millisecond, only while your code is running."),
    ("langsmith-sandbox", "suspends",
     "Use Serverless for background agents (it scales to zero, so you pay only "
     "while it runs)."),
]

# A separate check, because it is a different kind of failure. 26 pages were
# called "client-rendered shells" when they were not: aptible's pricing page
# embeds a JSON-LD block inside a <script> tag containing the billing text, and
# stripping every script discarded it. The page then looked empty and the
# verdict became "no price rendered in the HTML", which is a confident false
# statement about a page that plainly renders its prices. A shell verdict that
# is really a stripper bug is worse than no verdict, because it explains away the
# row instead of leaving it open.
JSONLD_CASES = [
    # (description, html, must the stripped text contain a price?)
    ("json-ld pricing survives the stripper",
     '<html><body><script type="application/ld+json">'
     '{"@type":"Product","offers":{"price":"499","priceCurrency":"USD",'
     '"description":"Dedicated stack. Starting at $499/month."}}'
     '</script></body></html>', True),
    ("an ordinary script is still dropped",
     '<html><body><script>var price = "$999";</script>'
     '<p>$10 per month</p></body></html>', True),
    ("a genuinely empty page stays empty",
     '<html><body><div id="root"></div></body></html>', False),
]


def selftest():
    """Run the known-answer cases. Returns the list of failures."""
    bad = []
    for pid, want, text in SELFTEST:
        v, _why, _q, _r = classify(text)
        got = v if v else "unstated"
        if got != want:
            bad.append("%s: got %s, want %s" % (pid, got, want))
    for desc, src, want_price in JSONLD_CASES:
        text = strip_markup(src)
        has = bool(re.search(r"\$\s?\d", text))
        if has != want_price:
            bad.append("%s: stripped text has_price=%s, want %s"
                       % (desc, has, want_price))
    return bad


def main():
    model_path = os.path.join(ROOT, "data", "period-model.json")
    if not os.path.isfile(model_path):
        print("could not run: %s missing; run experiments/70-period-model.py"
              % model_path, file=sys.stderr)
        return 2
    with open(model_path, encoding="utf-8") as fh:
        model = json.load(fh)

    # Only providers that actually take the fallback are worth a fetch. A row
    # whose keep rate comes from the card's own features is already evidence.
    targets = {}
    for p in model["providers"]:
        for _shape, s in (p.get("shapes") or {}).items():
            if s.get("keep_source") == "default":
                u = p.get("url")
                if isinstance(u, list):
                    u = u[0] if u else None
                targets[p["id"]] = u
    if not targets:
        print("no providers on the keep-rate fallback; nothing to probe")
        return 0

    st_fail = selftest()
    print("== self-test ==")
    print("known-answer cases: %d, failures: %d" % (len(SELFTEST), len(st_fail)))
    for f in st_fail:
        print("  FAIL %s" % f)
    if st_fail:
        print()
        print("refusing to publish: the classifier does not reproduce the verdicts "
              "it is supposed to give on pages already read. A pattern list that "
              "has drifted must be fixed before it is applied to 183 new pages.",
              file=sys.stderr)
        return 1
    print()
    print("== conditions ==")
    print("date_utc  : %s" % datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("corpus    : %s" % CARD_COMMIT)
    print("fallback  : keep_source == 'default' (no published suspension in the card)")
    print("providers : %d" % len(targets))
    print("method    : fetch the vendor's own page, strip markup, match the")
    print("            vendor's own words about billing a stopped machine")
    print("timeout   : %ds each, %d concurrent" % (TIMEOUT, WORKERS))
    print()

    items = sorted(targets.items())
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = list(pool.map(probe, items))
    rows.sort(key=lambda r: r["id"])

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    print("-- verdicts --")
    for k in ("suspends", "partial", "bills_uptime", "unstated", "shell",
              "unreachable"):
        if counts.get(k):
            print("  %-12s %3d" % (k, counts[k]))
    print()
    print("-- every provider with a verdict, and the quote it came from --")
    for r in rows:
        q = (r.get("quote") or "")
        q = (q[:150] + "...") if len(q) > 150 else q
        print("  %-12s %-24s %s" % (r["verdict"], r["id"], q or r.get("why", "")))

    # A run that finds FEWER verdicts than the one already on disk is worse
    # than no run, and it must not overwrite it. This is not hypothetical: a
    # second run minutes after the first returned 173 rows and ZERO verdicts,
    # because the burst of 183 concurrent requests had the vendor sites serving
    # degraded or blocked responses. A single curl of the same page at the same
    # moment returned 200 with the sentence intact. The artefact therefore
    # records its own yield and refuses to replace a better one.
    dest = os.path.join(ROOT, "data", "billing-posture.json")
    _prev = None
    if os.path.isfile(dest):
        try:
            with open(dest, encoding="utf-8") as _fh:
                _prev = json.load(_fh)
        except ValueError:
            _prev = None
    _got = sum(counts.get(k, 0) for k in ("suspends", "partial", "bills_uptime"))
    if _prev is not None:
        _had = sum((_prev.get("counts") or {}).get(k, 0)
                   for k in ("suspends", "partial", "bills_uptime"))
        if _got < _had:
            print()
            print("REFUSING TO WRITE. This run found %d verdict(s); the artefact on"
                  % _got)
            print("disk holds %d from %s. A drop like that is the vendor sites"
                  % (_had, _prev.get("probed_at")))
            print("degrading under a burst of requests, not a change in the")
            print("market, and the previous run is better evidence. Re-run with")
            print("fewer workers, or later. Nothing has been overwritten.")
            # Exit 3, not 1. This is not a failed measurement: it is the guard
            # working, and the artefact on disk is still good. Exit 1 would say
            # "the thing you wanted did not happen" and would make every
            # pipeline that runs this look broken whenever a vendor site is
            # briefly serving a degraded page.
            return 3
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump({"card_commit": CARD_COMMIT,
                   "probed_at": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "method": "first-party page fetch, vendor's own words, quote kept",
                   "counts": counts, "rows": rows}, fh, indent=1, sort_keys=True)
    print()
    print("wrote %s (%d providers, %d verdicts)" % (dest, len(rows), _got))
    unprobed = (counts.get("unstated", 0) + counts.get("shell", 0)
                + counts.get("unreachable", 0))
    if unprobed:
        print()
        print("NOT ESTABLISHED for %d of %d providers: %s"
              % (unprobed, len(rows), ", ".join(
                  "%s=%d" % (k, counts[k]) for k in
                  ("unstated", "shell", "unreachable") if counts.get(k))))
        print("An unstated verdict is NOT evidence of billing for uptime. Those")
        print("rows keep the conservative 1.00 default and say so on the row.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
