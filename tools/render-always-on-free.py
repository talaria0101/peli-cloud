#!/usr/bin/env python3
"""Render docs/ALWAYS-ON-FREE.md from data/always-on-free.json.

Every number on the page is generated. Prose that a script can compute should
not be typed, because typed prose drifts the moment the data changes.

    python tools/render-always-on-free.py

`render()` returns the page as a string and writes nothing, so a checker can
re-render in memory and compare rather than re-rendering over the committed
file in place.
"""

import html
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "always-on-free.json"
OUT = ROOT / "docs" / "ALWAYS-ON-FREE.md"
GUARD = ROOT / "tools" / "check-always-on-free.py"
PAGE_GATE = ROOT / "tools" / "check-rendered-page.py"
PAGES = ROOT / "verify" / "pages"
REACH = ROOT / "verify" / "reachability.json"

COUNTABLE = {"T1", "T2", "T3"}
ORDER = ["T1", "T2", "T3", "DEAD", "UNVERIFIED"]

# The host the "filtered, not down" argument is about. Every port claim below
# is read off the `host:port` keys present in verify/reachability.json, so a
# probe that measures a fourth port produces it on the page without an edit.
BULK_HOST = "blinkenshell.org"
# The two hosts whose SSH banners the page compares.
TILDE_PAIR = ("tilde.zone:22", "tilde.town:22")

# How a quote was recovered from the vendor's page. A VERBATIM quote is one
# contiguous span of the bytes. A RECONSTRUCTION is several spans joined with
# ` | ` or ` ... `, and the page says which and where they were found, because
# a table row read cell by cell is not a sentence the vendor ever wrote.
# A ` | ` is an explicit separator a row uses to mean "these are two places on
# the page, not one sentence". An ellipsis followed by a space is a
# transcription gap joining two spans, whether or not a space precedes it:
# "this... Hard Limit" is two spans, and tilde.club's Soft/Hard/Grace quote is
# three. An ellipsis NOT followed by a space is part of the text ("up to 24
# hours...") and is left alone.
RECON_SPLIT = re.compile(r"\s*\|\s*|(?<=\S)\s*\.\.\.(?=\s)")
# The same n-gram window and threshold tools/check-quotes.py already uses, so a
# fragment is attributed by one house rule rather than two.
NGRAM = 4
MIN_FRACTION = 0.55


def _load_guard():
    """Import the guard so the page and the check can never disagree.

    The provenance table and the mutation count are both derived from the guard
    rather than typed. An earlier revision hardcoded "9/9" while the guard ran
    11 mutations, which is the exact drift this file's docstring warns about.
    """
    spec = importlib.util.spec_from_file_location("always_on_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_page_gate():
    """Import tools/check-rendered-page.py to read ITS mutation count.

    Loading it here is safe even though it loads this renderer in turn:
    importlib builds a fresh module object each time rather than consulting
    sys.modules, so the pair cannot deadlock each other. Verified by running the
    renderer, which needs this count to print it.
    """
    spec = importlib.util.spec_from_file_location("always_on_page_gate", PAGE_GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cell(row, key, default="—"):
    val = row.get(key)
    if val is None or val == "":
        return default
    return str(val)


def short(s, n=150):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def quote_fragments(quote):
    """Split a quote into the spans it was assembled from.

    ` | ` is an explicit separator a row uses to mean "these are two places on
    the page, not one sentence". An ellipsis followed by a space joins two
    spans; one that runs into the next word ("up to 24 hours...") is part of
    the text and is left alone.
    """
    return [f.strip() for f in RECON_SPLIT.split(str(quote).strip()) if f.strip()]


def _page_text(raw):
    """HTML to comparable text. Same normalisation verify/claim.py uses, so a
    fragment found by one is found by the other."""
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    t = html.unescape(s)
    for a, b in (("’", "'"), ("“", '"'), ("”", '"'),
                 ("—", "-"), ("–", "-"), (" ", " "), ("…", "...")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).lower()


def _squash(s):
    return re.sub(r"\s+", "", s)


def capture_texts():
    """stem -> text for every capture under verify/pages/, or {} if there are
    none. verify/pages/ is gitignored: a fresh clone has none, and a renderer
    that crashed there would fail to regenerate its own page at all."""
    out = {}
    if not PAGES.is_dir():
        return out
    for p in sorted(PAGES.glob("*.html")):
        out[p.stem] = _page_text(p.read_text(encoding="utf-8", errors="replace"))
    return out


def _fragment_fraction(fragment, text):
    words = fragment.split()
    if len(words) < NGRAM:
        return 1.0 if fragment in text else 0.0
    grams = [" ".join(words[i:i + NGRAM]) for i in range(len(words) - NGRAM + 1)]
    return sum(1 for g in grams if g in text) / len(grams)


def locate(fragment, texts):
    """Capture names whose bytes contain this fragment, verbatim or by n-gram.

    Capped by the caller, and the cap is reported rather than hidden. A
    one-word cell like `128` or `6` is in twenty captures, and printing all
    twenty per fragment turned one attribution line into several kilobytes of
    noise that buried the one fact a reader wants: whether the fragment was
    found at all.
    """
    want = fragment.lower()
    sq = _squash(want)
    hits = []
    for stem, text in texts.items():
        if sq and sq in _squash(text):
            hits.append(stem)
        elif _fragment_fraction(want, text) >= MIN_FRACTION:
            hits.append(stem)
    return sorted(hits)


# Above this many captures for one fragment, print the first few and the total.
# Three is enough for a reader to see whether a fragment is common or rare, and
# that is the distinction that matters when the quote is a table cell: `128` in
# twenty captures is much weaker evidence than `Memory usage (RSS)` in one.
MAX_CAPTURES_PER_FRAGMENT = 3


def _where_text(where):
    if not where:
        return "NO CONTIGUOUS MATCH in any capture under `verify/pages/`"
    shown = ", ".join(
        f"`verify/pages/{s}.html`" for s in where[:MAX_CAPTURES_PER_FRAGMENT])
    if len(where) > MAX_CAPTURES_PER_FRAGMENT:
        return (f"{shown} (+{len(where) - MAX_CAPTURES_PER_FRAGMENT} more: this "
                f"fragment is that common, so it is weak evidence on its own)")
    return shown


def _attribution(fragments, texts):
    """Name the capture each fragment was found in, or say plainly that it was
    not. A fragment reconstructed from a table's cells has no contiguous match
    in the capture even though every cell is in it, so 'no contiguous match' is
    the truthful answer and not a failure.

    Returns a LIST, one line per fragment. It used to return one string joined
    with spaces, and an 18-fragment table reconstruction came out as a single
    multi-kilobyte list item that no reader could use. The markup is a list
    because the content is a list.
    """
    lines = []
    for i, frag in enumerate(fragments, 1):
        if not texts:
            tail = "CAPTURES ABSENT - run `python3 verify/fetch.py`"
        else:
            tail = _where_text(locate(frag, texts))
        lines.append(f"  - {i}. `{frag}` -> {tail}")
    return lines


def _quote_block(row, texts):
    """The lines a row's vendor quotes render as, or [] if it carries none.

    quote, quote2 and quote3 are each rendered on their own merits. Only the
    first is required by the guard, so an earlier revision that printed quote2
    inside `if quote` dropped quote3 silently and nothing noticed.

    A quote is emitted as a blockquote, and a blockquote is a LINE construct:
    a `>` prefix applies to one line. The hashbang quote is three lines of shell
    script taken from a capture, so emitting it raw printed a continuation line
    with no `>` on it and the page rendered it as body text quoting itself. Each
    line gets the prefix, which is what a fenced block would also fix and what
    keeps the reader's eye on the whole quote. `_quote_lines` returns a list for
    that reason and the caller joins them.
    """
    out = []
    for key in ("quote", "quote2", "quote3"):
        q = row.get(key)
        if not q:
            continue
        frags = quote_fragments(q)
        if len(frags) > 1:
            sep = "|" if " | " in q else "..."
            out.append(f"- **Vendor says ({key}, RECONSTRUCTION - {len(frags)} fragments "
                       f"joined by `{sep}`, not one contiguous quote):**")
            out.extend(_quote_lines(q))
            out.append("  - _Fragments:_")
            out.extend(_attribution(frags, texts))
        else:
            out.append(f"- **Vendor says ({key}, VERBATIM):**")
            out.extend(_quote_lines(q))
    return out


def _quote_lines(q):
    """A quote as one '> ' line per line of the quote.

    A multi-line quote is a real case, not a hypothetical: the hashbang quotes
    are shell script and YAML read from captures kept under a .html name. One
    `>` prefix on a three-line quote leaves lines two and three as ordinary body
    text, which renders as the page quoting the page.
    """
    lines = str(q).splitlines() or [""]
    return [f"> {line}".rstrip() if line.strip() else ">" for line in lines]


def _host_ports(reach, host):
    """{port: result} for every `host:port` key present in the measurement."""
    out = {}
    for key, res in reach["results"].items():
        h, _, p = key.rpartition(":")
        if h == host and p.isdigit():
            out[int(p)] = res
    return out


def _blinkenshell_bullet(reach):
    """What the Blinkenshell ports did in this run, read off the flags.

    Returns (sentence, contradicts). `contradicts` is False when the run
    supports no claim to contradict, so the count in the sentence above is not
    a constant dressed as a number.

    An earlier revision hardcoded the words 'Port 443 accepted a connection'
    and derived only the failing list, so a run in which 443 timed out printed
    both that sentence and 'blinkenshell.org:443 | no route' three lines apart.
    """
    ports = _host_ports(reach, BULK_HOST)
    if not ports:
        return ("- **Blinkenshell:** this run measured no "
                f"`{BULK_HOST}:*` endpoint, so no port claim is made here.", False)
    up = sorted(p for p, r in ports.items() if r.get("reachable"))
    down = sorted(p for p, r in ports.items() if not r.get("reachable"))
    reasons = sorted({r.get("error") or "no reason recorded"
                      for r in ports.values() if not r.get("reachable")})
    up_s = ", ".join(str(p) for p in up) if up else "no port"
    down_s = ", ".join(str(p) for p in down) if down else "no port"
    plural_up = "" if len(up) == 1 else "s"
    if up and down:
        return (f"- **Blinkenshell is filtered, not down.** Port{plural_up} "
                f"{up_s} accepted a connection while {down_s} did not "
                f"({'; '.join(reasons)}) on the same host, in the same run. "
                + ("peli-cloud blamed its sandbox's port-22 refusal, but 2222 was "
                   "never port 22, so that excuse never covered this case. "
                   if 22 in down and 2222 in down else "")
                + "The host is alive and filtering by protocol.", True)
    if up:
        return (f"- **Blinkenshell accepted every measured port.** Port{plural_up} "
                f"{up_s} connected; no `{BULK_HOST}:*` endpoint in this run was "
                f"refused, so no filtered-or-down claim is made here.", False)
    return (f"- **Blinkenshell answered nothing in this run.** Every measured "
            f"port ({down_s}) failed to connect ({'; '.join(reasons)}). This run "
            f"therefore supports no filtered-or-down claim.", False)


def _tilde_bullet(reach):
    """Compare the two tilde banners, or say why no comparison is possible.

    Returns (sentence, contradicts) on the same terms as the Blinkenshell
    bullet: False when the run supports no claim to contradict.

    Every banner printed here is read out of verify/reachability.json. The
    earlier revision typed 'the identical OpenSSH build string ... (10.0p2
    Debian-7+deb13u4)' into the page, which kept asserting a shared image after
    a run recorded no route at all for tilde.zone:22.
    """
    zone_key, town_key = TILDE_PAIR
    zone = reach["results"].get(zone_key)
    town = reach["results"].get(town_key)
    tail = ("peli-cloud demoted tilde.zone for having no discoverable operator. "
            "A banner is still not evidence of a free tier.")
    if not zone or not zone.get("banner"):
        why = (zone or {}).get("error") or "this run measured no endpoint"
        return (f"- **tilde.zone returned no SSH identification string.** "
                f"`{zone_key}` reported: `{why}`. No comparison with tilde.town "
                f"is made here. {tail}", False)
    if not town or not town.get("banner"):
        return (f"- **tilde.zone answers SSH** with `{zone['banner']}`, but "
                f"`{town_key}` returned no identification string in this run, "
                f"so the two are not compared. {tail}", False)
    if zone["banner"] == town["banner"]:
        return (f"- **tilde.zone answers SSH** with the *identical* OpenSSH "
                f"identification string as tilde.town: `{zone['banner']}`, which "
                f"is what a shared image or a mirror produces. {tail}", True)
    return (f"- **tilde.zone answers SSH** with `{zone['banner']}`, which is "
            f"**different** from tilde.town's `{town['banner']}`. The two hosts "
            f"do not share a build string in this run. {tail}", True)


def render():
    """Return the page as a string. Writes nothing."""
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    rows = doc["rows"]
    counted = [r for r in rows if r["tier"] in COUNTABLE]
    guard = _load_guard()
    _provenance = guard.provenance
    n_mutations = len(guard.MUTATIONS)
    # The page names TWO mutation suites and their counts are different: the
    # census guard's, and the rendered-page gate's. A single variable was used
    # for both, so the page printed the census guard's count next to the page
    # gate's command - 13/13 against a suite that has 12 mutations. The count is
    # read from the tool it describes, which is the whole point of importing the
    # guards rather than typing a number.
    n_page_mutations = len(_load_page_gate().MUTATIONS)
    lb = doc["launch_base"]
    generated = doc["generated"]
    repo_label = lb["repo"].rstrip("/").removeprefix("https://github.com/")

    L = []
    a = L.append

    def emit(s=""):
        # A CR anywhere in a data string would leave the file half CRLF and
        # break the byte-for-byte comparison a checker does against it.
        a(str(s).replace("\r\n", "\n").replace("\r", " "))

    emit(f"# Always-on free compute, {generated}")
    emit()
    emit(f"**{len(counted)} of {len(rows)} rows hold up indefinitely at $0.** "
         f"The starting corpus was [{repo_label}]({lb['repo']}), read before "
         f"this census was written. Its own account of what it found, from "
         f"`data[\"launch_base\"][\"note\"]`:")
    emit()
    emit(f"> {lb['note']}")
    emit()
    emit("Generated from [`data/always-on-free.json`](../data/always-on-free.json) "
         "by `tools/render-always-on-free.py`. Guarded by "
         "`tools/check-always-on-free.py`, and gated against its own output by "
         "`tools/check-rendered-page.py`.")
    emit()

    emit("## The distinction the taxonomy rests on")
    emit()
    emit("A relay cannot fix everything, and that is the whole design.")
    emit()
    emit("| tier | what it means | count |")
    emit("|---|---|---|")
    for t in ORDER:
        if t not in doc["tiers"]:
            continue
        emit(f"| **{t}** | {doc['tiers'][t]} | {sum(1 for r in rows if r['tier'] == t)} |")
    emit()
    emit("**A relay defeats a LIVENESS wall** — idle sleep, scale-to-zero, "
         "no-inbound-ports, browser-only. You keep the machine alive, or you tunnel "
         "out of it, and it becomes reachable forever.")
    emit()
    emit("**A relay cannot defeat a QUOTA wall** — a monthly compute-hour cap that "
         "exhausts regardless, a trial clock, or a paid-plan gate at creation "
         "time. Those rows are DEAD and are excluded. The figures that sort the "
         "rows are in `data[\"tier_note\"]`:")
    emit()
    emit(f"> {doc['tier_note']}")
    emit()
    emit("So T2 and T3 are legitimate hits, not near-misses: the keepalive or the "
         "relay *is* the thing that makes them always-on. Only DEAD is a dead end.")
    emit()

    emit("## How much of this is measured")
    emit()
    emit("Every row is counted exactly once, using the guard's own `provenance()` "
         "so these two tools cannot disagree about what a row's evidence is worth.")
    emit()
    emit("| evidence weight | rows | means |")
    emit("|---|---|---|")
    weights = {}
    for r in rows:
        weights.setdefault(_provenance(r), []).append(r["name"])
    emit(f"| first-hand | {len(weights.get('read', []))} | I fetched the page and read the "
         f"quote out of the bytes |")
    emit(f"| carried | {len(weights.get('carried', []))} | a research pass fetched it; the "
         f"row says so, and names which parts I did not check |")
    emit()
    emit("\"First-hand\" means the bytes were read, **not** that an account was "
         "created. No account exists anywhere in this census. The live probe below "
         "is the only measurement here that touches a real host.")
    emit()

    texts = capture_texts()

    emit("## The counted rows")
    emit()
    for t in ["T1", "T2", "T3"]:
        sel = [r for r in rows if r["tier"] == t]
        if not sel:
            continue
        emit(f"### {t} — {doc['tiers'][t]}")
        emit()
        for r in sel:
            emit(f"#### {r['name']}")
            emit()
            emit(f"- **What you get:** {cell(r, 'spec')}")
            if r.get("idle_or_session_limit"):
                emit(f"- **The wall:** {cell(r, 'idle_or_session_limit')}")
            if r.get("keepalive"):
                emit(f"- **The keepalive:** {cell(r, 'keepalive')}")
            if r.get("relay"):
                emit(f"- **The relay:** {cell(r, 'relay')}")
            emit(f"- **Account:** sign-up required = {cell(r, 'account_required')}, "
                 f"card required = {cell(r, 'card_required')}")
            if r.get("caveats"):
                emit(f"- **Caveat:** {r['caveats']}")
            if r.get("source"):
                emit(f"- **Source:** <{r['source']}>")
            for line in _quote_block(r, texts):
                emit(line)
            if r.get("verified_by"):
                emit(f"- **Verified:** {r['verified_by']}")
            emit()

    emit("## Measured, not assumed: live reachability")
    emit()
    if REACH.exists():
        reach = json.loads(REACH.read_text(encoding="utf-8"))
        s = reach["summary"]
        emit(f"peli-cloud could not dial a single host: its sandbox egress proxy refuses "
             f"port 22 (`CONNECT -> 403`), so every row in its census is documented-only. "
             f"This census was probed from a **residential host** instead. "
             f"**{s['reachable']}/{s['total']} endpoints accepted a TCP connection and "
             f"{s['banners']} returned an SSH identification string.**")
        emit()
        emit("A banner is not a login. No credential was presented to any of these hosts.")
        emit()
        emit("| endpoint | result | banner / error |")
        emit("|---|---|---|")
        for key in sorted(reach["results"],
                          key=lambda k: (not reach["results"][k]["reachable"], k)):
            r = reach["results"][key]
            state = "**banner**" if r["banner"] else ("open, silent" if r["reachable"] else "no route")
            detail = r["banner"] or r["error"] or ""
            emit(f"| `{key}` | {state} | `{detail}` |")
        emit()
        # Each bullet returns (sentence, contradicts). `contradicts` is False
        # when THIS run supports no claim to contradict - a run in which nothing
        # was reachable, or tilde.zone returned no banner. The count and the
        # bullets are derived from that flag rather than typed, so a run that
        # measured nothing cannot leave the page asserting two contradictions
        # it did not find. That is the third instance of the same defect the
        # renderer was fixed for twice already: a sentence that describes a
        # measurement instead of being one.
        bullets = [_blinkenshell_bullet(reach), _tilde_bullet(reach)]
        contradicting = [(s, c) for s, c in bullets if c]
        n = len(contradicting)
        if n:
            # Subject-verb agreement is computed, not hoped for: a fixed
            # "results contradict / are the reason" string prints "1 result
            # contradict prior claims and is" the moment the count drops to
            # one, which is exactly what happened when tilde.zone went dark.
            noun = "result" if n == 1 else "results"
            verb = "contradicts" if n == 1 else "contradict"
            be = "is" if n == 1 else "are"
            emit(f"{n} {noun} {verb} prior claims and {be} the reason this probe was "
                 f"worth running. Every bullet below is computed from "
                 f"`verify/reachability.json`, so re-running the probe either "
                 f"reproduces them or falsifies them:")
            emit()
            for sentence, _ in contradicting:
                emit(sentence)
            emit()
        else:
            emit("This run produced no result that contradicts a prior claim, so no "
                 "such claim is made here. The table above is the whole of what "
                 "was measured, and every line of it is computed from "
                 "`verify/reachability.json`.")
            emit()
        emit(f"_Measured {reach['measured_at']} from a {reach['measured_from']}._")
        emit()

    emit("## Dead ends, and the wall that killed each")
    emit()
    emit("Nothing below was overcome in practice. Each wall is one a relay or a "
         "keepalive is argued *not* to defeat, from the vendor's own wording, and "
         "no relay or keepalive was actually run against any of them.")
    emit()
    emit("| Provider | the hard wall |")
    emit("|---|---|")
    for r in [r for r in rows if r["tier"] == "DEAD"]:
        emit(f"| **{r['name']}** | {short(cell(r, 'hard_wall'), 260)} |")
    emit()

    emit("## Corrections to the launch base")
    emit()
    emit(f"Read against first-party pages fetched on {generated}.")
    emit()
    for c in doc["corrections_vs_launch_base"]:
        emit(f"- {c}")
    emit()

    emit("## What this census did NOT establish")
    emit()
    emit("Stated plainly, because a census that hides its gaps is worse than no census.")
    emit()
    for c in doc["what_this_census_did_not_establish"]:
        emit(f"- {c}")
    emit()

    emit("## Reproduce")
    emit()
    emit("```sh")
    emit("python tools/check-always-on-free.py           # guard the census")
    emit(f"python tools/check-always-on-free.py --mutate  # prove the guard can fail ({n_mutations}/{n_mutations})")
    emit("python tools/render-always-on-free.py          # rewrite this page from the JSON")
    emit("python tools/check-rendered-page.py            # the committed page matches this renderer")
    emit(f"python tools/check-rendered-page.py --mutate  # prove that gate can fail ({n_page_mutations}/{n_page_mutations})")
    emit("python verify/fetch.py                         # re-fetch the vendor pages")
    emit("python verify/claim.py                        # every quote, against the bytes it came from")
    emit("python verify/fetch.py --check                # is every capture re-fetchable by name?")
    emit("```")
    emit()
    emit("## Method")
    emit()
    m = doc["method"]
    emit(f"- **Launch base:** {m['launch_base']}")
    emit(f"- **Sweep 1:** {m['sweep_1']}")
    emit(f"- **Sweep 2:** {m['sweep_2']}")
    emit(f"- **First-party verification:** {m['first_party_verification']}")
    emit()
    emit("Fetches that failed (recorded, not silently substituted):")
    emit()
    for f in m["fetches_that_failed"]:
        emit(f"- `{f}`")
    emit()

    # Exactly one trailing newline: a page that ends in a blank line is a page
    # whose last edit is invisible in a diff.
    return "\n".join(L).rstrip("\n") + "\n"


def main():
    page = render()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # newline="" keeps the "\n" in `page` from being translated on a host whose
    # native line separator is CRLF. The file is LF-only by construction.
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(page)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(page.splitlines())} lines)")

    r = subprocess.run([sys.executable, str(GUARD)], capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
