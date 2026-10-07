#!/usr/bin/env python3
"""check-rendered-page.py - the gate on docs/ALWAYS-ON-FREE.md itself.

tools/check-always-on-free.py guards the DATA. It has nothing to say about the
file the renderer writes: a hand-edited paragraph, a stale page committed
after a row changed, a banner typed into prose, and every clause in that guard
still passes. There was no check on the output at all, and no CI to run one.

Five clauses, each of which failed for a reason that had already happened once:

  1. THE COMMITTED PAGE IS THE RENDERED PAGE. Re-render into a temporary file
     and compare bytes, naming the first differing line and its number. The
     comparison is byte-for-byte rather than line-by-line because the two ways
     a generated file rots quietly are a CRLF that arrived with a Windows
     checkout and a missing or doubled trailing newline. (The page in this
     repository WAS CRLF: it was rendered on a Windows host, and every future
     render on a Linux one would have differed from it on all 399 lines.)

  2. EVERY COUNT IS THE COUNT THE DATA SAYS. Re-derive the row total, the
     counted total, the per-tier counts, the first-hand and carried provenance
     counts, the guard's mutation count, and the reachability summary from the
     JSON, and require each to appear on the page in the place that uses it.
     Every assertion is anchored to its context - a bare "22" would match
     almost any line - so this is a check on the number, not on a substring.

  3. NO BANNER IS TYPED. Every `SSH-2.0-...` / `OpenSSH_...` string on the
     page must occur in verify/reachability.json. This is the clause that
     catches the defect the renderer's own docstring warns about: the tilde.zone
     bullet typed an OpenSSH build string into the page, so with tilde.zone
     recorded as no-route the table said "no route" and three lines below it
     still asserted a shared build. The clause does not need to know which
     bullet a banner is in.

  4. EVERY QUOTE IS RENDERED, AND LABELLED FOR WHAT IT IS. Each of quote,
     quote2 and quote3 in the data must appear on the page under the marker
     its shape calls for: VERBATIM for one contiguous span, RECONSTRUCTION for
     spans joined by ` | ` or an ellipsis. quote3 is on 4 counted rows and was
     rendered nowhere; an earlier revision printed quote2 inside `if quote`, so
     a row without a quote would have dropped both.

  5. EVERY ATTRIBUTION IS TRUE. Where the page says a fragment was found in a
     capture, that capture must exist and contain it. This is what stops the
     attribution added by clause 4 from becoming typed prose of its own.

Usage: python3 tools/check-rendered-page.py            # check
       python3 tools/check-rendered-page.py --mutate   # prove the check can fail
       python3 tools/check-rendered-page.py --strict   # no captures = exit 2

Exit codes:
  0  every clause that could run passed
  1  a clause failed
  2  --strict with no captures under verify/pages/; or no committed page

Captures and this gate
----------------------
verify/pages/ is gitignored (third-party HTML, reproducible on demand), and two
clauses read it: clause 5 checks attributions against it, and clause 1
re-renders, which needs it to name the same capture files the committed page
names. On a fresh clone there are no captures, so a re-render legitimately
differs from the committed page and clause 5 has nothing to check against.
This tool does not pretend that is a pass. It says which clauses it ran, names
the two it could not, and exits 0 on the rest - because exit 1 there would
teach a reader that a fresh clone is broken, and exiting 0 without saying so is
the failure this repo's other tools already document. A `--strict` flag turns
the missing captures into exit 2, for a host that would rather the gate refuse.
"""
import copy
import importlib.util
import json
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "always-on-free.json"
PAGE = ROOT / "docs" / "ALWAYS-ON-FREE.md"
GUARD = ROOT / "tools" / "check-always-on-free.py"
RENDERER = ROOT / "tools" / "render-always-on-free.py"
REACH = ROOT / "verify" / "reachability.json"
PAGES = ROOT / "verify" / "pages"

COUNTABLE = {"T1", "T2", "T3"}
ORDER = ["T1", "T2", "T3", "DEAD", "UNVERIFIED"]
QUOTE_FIELDS = ("quote", "quote2", "quote3")

# An SSH identification string, as it can appear mid-sentence. The character
# class excludes the backtick and the parenthesis, because the page wraps
# banners in backticks and one row's verified_by ends the banner with ")" -
# matching greedily there produced tokens like "SSH-2.0-OpenSSH_10.5p1)" that
# are not banners and flagged a correct page as broken.
BANNER = re.compile(r"(?:SSH-2\.0-|OpenSSH_)[A-Za-z0-9_.:+@/=~^-]*")
# `N `frag` -> `verify/pages/NAME.html`` as the renderer writes it.
# One attribution list item: "- 1. `<fragment>` -> <where>". The fragment is
# matched non-greedily up to the closing backtick and the item is delimited by
# the NEXT list item or the end of the block, so a fragment that itself contains
# a newline (the hashbang shell quote is two lines) still parses.
#
# It used to expect "- 1 `...` -> ...   2 `...`" on one line, which was the
# shape the renderer emitted before attribution became a list. It matched nothing
# after that change, so clause_attribution returned no failures at all while
# appearing to be a clause. The --mutate suite caught that, which is what it is
# for; a clause that cannot fire is not coverage however well it is documented.
ATTRIB = re.compile(r"^\s*-\s+\d+\.\s+`(.+?)`\s+->\s+(.+)$", re.M)


def self_mutations():
    """This module's own MUTATIONS, read reflectively.

    Counting `len(MUTATIONS)` inline would work and would also make the clause
    tautological with the renderer, which imports this module and reads the same
    list. Going through the name keeps one source of truth.
    """
    return MUTATIONS


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lines_of(text):
    return text.split("\n")[:-1] if text.endswith("\n") else text.split("\n")


def clause_fresh(committed, rendered):
    """The committed page must BE the renderer's output, byte for byte."""
    if committed is None:
        return ["docs/ALWAYS-ON-FREE.md is missing; run tools/render-always-on-free.py"]
    if committed == rendered:
        return []
    a = committed.split("\n")
    b = rendered.split("\n")
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else None
        y = b[i] if i < len(b) else None
        if x != y:
            return [f"line {i + 1} differs from what tools/render-always-on-free.py writes:\n"
                    f"      committed: {x!r}\n"
                    f"      rendered:  {y!r}\n"
                    f"    (committed {len(a)} line(s), rendered {len(b)}; "
                    f"first difference at line {i + 1})"]
    return ["the two files differ but no differing line was found; the comparison "
            "itself is wrong"]


def clause_counts(page, doc, guard, reach):
    """Re-derive every count and require it on the page where it is used.

    Each assertion names the ONE capture group the value must equal. A first
    version asked only whether the value appeared in ANY group, so a page
    reading 'prove the guard can fail (9/13)' passed the mutation-count check
    because 13 was still sitting in the denominator.
    """
    rows = doc["rows"]
    counted = [r for r in rows if r.get("tier") in COUNTABLE]
    fails = []

    def at(pattern, group, value, label, where):
        m = re.search(pattern, page, re.M)
        if not m:
            fails.append(f"{label}: the page has no line matching {pattern!r}, so "
                         f"{where} cannot be checked")
        elif m.group(group) != str(value):
            fails.append(f"{label}: page says {m.group(group)}, the data says "
                         f"{value} ({where})")

    HEADLINE = r"\*\*(\d+) of (\d+) rows hold up indefinitely"
    at(HEADLINE, 1, len(counted), "counted rows", "the headline leading figure")
    at(HEADLINE, 2, len(rows), "total rows", "the headline 'of N rows' figure")

    for t in ORDER:
        if t not in doc["tiers"]:
            continue
        at(rf"\| \*\*{t}\*\* \| .*? \| (\d+) \|", 1,
           sum(1 for r in rows if r.get("tier") == t),
           f"tier {t}", f"the {t} row of the tier table")

    weights = {}
    for r in rows:
        weights.setdefault(guard.provenance(r), []).append(r)
    at(r"\| first-hand \| (\d+) \|", 1, len(weights.get("read", [])),
       "first-hand rows", "the evidence-weight table")
    at(r"\| carried \| (\d+) \|", 1, len(weights.get("carried", [])),
       "carried rows", "the evidence-weight table")

    MUT = r"check-always-on-free\.py --mutate\s+# prove the guard can fail \((\d+)/(\d+)\)"
    at(MUT, 1, len(guard.MUTATIONS), "guard mutation count",
       "the numerator of the guard mutation count in Reproduce")
    at(MUT, 2, len(guard.MUTATIONS), "guard mutation count",
       "the denominator of the guard mutation count in Reproduce")

    # This gate's OWN mutation count, anchored to its own command line.
    #
    # It used to be checked by nothing, and the page printed the census guard's
    # 13 next to this gate's --mutate, which has 12 mutations. Measured: setting
    # that line to 12/12, 99/99 or back to 13/13 all produced no failure. The
    # anchor is the tool name, not a bare "(n/n)", so swapping the two counts
    # between the two commands is caught too.
    PAGE_MUT = r"check-rendered-page\.py --mutate\s+# prove that gate can fail \((\d+)/(\d+)\)"
    own = len(self_mutations())
    at(PAGE_MUT, 1, own, "page-gate mutation count",
       "the numerator of this gate's own mutation count in Reproduce")
    at(PAGE_MUT, 2, own, "page-gate mutation count",
       "the denominator of this gate's own mutation count in Reproduce")

    if reach is None:
        fails.append("verify/reachability.json is missing; the reachability "
                     "summary cannot be checked")
    else:
        s = reach.get("summary", {})
        SUM = (r"\*\*(\d+)/(\d+) endpoints accepted a TCP connection "
               r"and (\d+) returned an SSH identification string")
        at(SUM, 1, s.get("reachable"), "reachability reachable",
           "the reachability summary")
        at(SUM, 2, s.get("total"), "reachability total", "the reachability summary")
        at(SUM, 3, s.get("banners"), "reachability banners",
           "the reachability summary")
    return fails


def clause_banners(page, reach):
    """No SSH banner on the page may be absent from the measurement file.

    The reachability table prints banners read out of reachability.json, and so
    does the tilde.zone bullet now. A banner that is NOT in that file is prose
    someone typed, and it will still be there after the next probe contradicts it.
    """
    if reach is None:
        return ["verify/reachability.json is missing; no banner on the page can be checked"]
    banners = [r.get("banner") for r in reach.get("results", {}).values() if r.get("banner")]
    fails = []
    seen = set()
    for i, line in enumerate(page.split("\n"), 1):
        for tok in BANNER.findall(line):
            if tok in seen:
                continue
            seen.add(tok)
            if not any(tok in b for b in banners):
                fails.append(f"line {i}: banner {tok!r} is on the page but not in "
                             f"verify/reachability.json; a banner that is not in the "
                             f"measurement file is typed prose")
    return fails


def clause_quotes(page, doc, renderer):
    """Each quote field of each PUBLISHED row must appear under the right marker.

    Published means a counted tier: the page's counted-rows section carries
    T1/T2/T3 only, and DEAD and UNVERIFIED rows get a hard-wall table instead.
    Checking a DEAD row's quote here would fail on a correct page.
    """
    fails = []
    plines = page.split("\n")
    for row in doc["rows"]:
        rid = row.get("id", "<no id>")
        if row.get("tier") not in COUNTABLE:
            continue
        for field in QUOTE_FIELDS:
            q = row.get(field)
            if not q:
                continue
            frags = renderer.quote_fragments(q)
            kind = "VERBATIM" if len(frags) == 1 else "RECONSTRUCTION"
            # The renderer's reconstruction marker is longer than the kind
            # word alone: "RECONSTRUCTION - 2 fragments joined by `...`". A
            # prefix built from the kind alone is a prefix of that, so matching
            # on startswith(head) is correct, but the LABEL check below must
            # accept any marker whose kind word agrees, not require the short
            # form. This clause reads the page as the renderer writes it.
            head = f"- **Vendor says ({field}, {kind}"
            # The marker line and the quoted text are SEPARATE lines: the
            # renderer emits "- **Vendor says (quote, VERBATIM):**" and then one
            # "> " line per line of the quote, because a `>` prefix applies to
            # one line and a multi-line quote printed raw left its continuation
            # lines as body text. So the match has to be over a BLOCK, not a
            # line. An earlier version required the marker line to also contain
            # the quote, which was true when the two were one line and stopped
            # being true when they were split - and it then reported all 33
            # quotes as mislabelled, which is what a checker does when it has
            # quietly stopped looking at the thing it claims to check.
            #
            # `hits` must also stay scoped to THIS row's quote. A page-global
            # search for the marker finds some other row's block, and then the
            # check passes for a row whose marker was relabelled.
            hits = []
            for i, ln in enumerate(plines):
                if not ln.startswith(head):
                    continue
                block = plines[i:i + 1 + len(q.splitlines())]
                # Compare the quoted TEXT, not the rendered lines. The renderer
                # prefixes every line of a multi-line quote with "> ", so a
                # three-line quote renders as "> a\n> b\n> c" while the data
                # holds "a\nb\nc". Comparing raw block text fails on the second
                # line, which is how this clause came to report a quote it was
                # looking straight at. The prefix is stripped per line and the
                # CONTENT is compared, which is the thing both sides mean.
                quoted = [ln[2:] if ln.startswith("> ") else ln
                          for ln in block[1:1 + len(q.splitlines())]]
                if quoted == q.splitlines():
                    hits.append(i)
            if hits:
                continue
            shown_i = next((i for i, ln in enumerate(plines) if q in ln), None)
            if shown_i is None:
                # Multi-line quotes never appear inside one page line, so fall
                # back to matching on their FIRST line before declaring the
                # quote absent.
                first = q.splitlines()[0]
                shown_i = next((i for i, ln in enumerate(plines)
                                if ln.startswith("> ") and first in ln), None)
            if shown_i is None:
                fails.append(f"{rid}.{field}: no line marked 'Vendor says ({field}, "
                             f"{kind})' for this quote; it is not on the page at all")
            else:
                # Report the marker that IS on the page for this quote, so the
                # message names the disagreement rather than the first marker in
                # the document.
                marked = ""
                for i in range(shown_i, -1, -1):
                    if plines[i].startswith("- **Vendor says ("):
                        marked = plines[i].split("):")[0]
                        marked = marked[
                            marked.find("Vendor says") + len("Vendor says ("):]
                        break
                fails.append(f"{rid}.{field}: the page marks it '{marked or 'NO MARKER'}' "
                             f"where the data calls for '{kind}'")
    return fails


def clause_attribution(page, doc, renderer, texts):
    """Every capture the page names must exist and contain the fragment.

    Reads the attribution as a BLOCK for the same reason clause_quotes does: the
    marker line carries no quote text, and the attribution is a LIST under it, so
    `q in ln` was never true and this clause returned no failures at all. A
    clause that cannot fire is not coverage, and it was passing while looking at
    nothing - the same failure verify/claim.py had with an empty page filter.
    """
    fails = []
    plines = page.split("\n")
    for row in doc["rows"]:
        rid = row.get("id", "<no id>")
        if row.get("tier") not in COUNTABLE:
            continue
        for field in QUOTE_FIELDS:
            q = row.get(field)
            if not q or len(renderer.quote_fragments(q)) < 2:
                continue
            idx = None
            for i, ln in enumerate(plines):
                if not ln.startswith(f"- **Vendor says ({field}, RECONSTRUCTION"):
                    continue
                quoted = [x[2:] if x.startswith("> ") else x
                          for x in plines[i + 1:i + 1 + len(q.splitlines())]]
                if quoted == q.splitlines():
                    idx = i
                    break
            if idx is None:
                continue  # clause_quotes reports the missing block
            # The attribution list runs from the "_Fragments:_" line to the next
            # "- **" line or blank, whichever comes first.
            tail_lines = []
            for ln in plines[idx + 1:]:
                if ln.startswith("- **") or ln.startswith("####"):
                    break
                tail_lines.append(ln)
            attr = "\n".join(tail_lines)
            for frag, tail in ATTRIB.findall(attr):
                for name in re.findall(r"verify/pages/([A-Za-z0-9_.-]+)\.html", tail):
                    if name not in texts:
                        fails.append(f"{rid}.{field}: page attributes fragment "
                                     f"{frag[:48]!r} to verify/pages/{name}.html, "
                                     f"which is not a capture")
                    elif name not in renderer.locate(frag, texts):
                        fails.append(f"{rid}.{field}: page attributes fragment "
                                     f"{frag[:48]!r} to verify/pages/{name}.html, "
                                     f"which does not contain it")
    return fails


CLAUSES = [
    "THE COMMITTED PAGE IS THE RENDERED PAGE",
    "EVERY COUNT IS THE COUNT THE DATA SAYS",
    "NO BANNER IS TYPED",
    "EVERY QUOTE IS RENDERED AND LABELLED",
    "EVERY ATTRIBUTION IS TRUE",
]


def check(page, doc, guard, reach, renderer, texts, rendered, quiet=False, skip=()):
    """Run every clause. `skip` neutralises clauses a mutation cannot isolate.

    Clause 1 is a byte comparison, so it fires on ANY edit to the page. A
    mutation that perturbs the DATA rather than the page is therefore run with
    clause 1 skipped, which is what proves the named clause stands on its own
    instead of riding on the catch-all. The skip is printed with the result.
    """
    runs = (
        (CLAUSES[0], lambda: clause_fresh(page, rendered)),
        (CLAUSES[1], lambda: clause_counts(page, doc, guard, reach)),
        (CLAUSES[2], lambda: clause_banners(page, reach)),
        (CLAUSES[3], lambda: clause_quotes(page, doc, renderer)),
        (CLAUSES[4], lambda: clause_attribution(page, doc, renderer, texts)),
    )
    fails = []
    per = {}
    for name, fn in runs:
        if name in skip:
            per[name] = []
            if not quiet:
                print(f"  [SKIP] {name}  <- cannot run here, see above")
            continue
        got = fn()
        per[name] = got
        if not quiet:
            print(f"  [{len(got) and 'FAIL' or ' ok '}] {name}")
        fails.extend(got)
    return fails, per


# ---------------------------------------------------------------- mutations
# Each mutation perturbs ONE clause's own input and names the clause that must
# catch it. A mutation caught by a neighbouring clause proves nothing about the
# one it is named after, so each is built to trip only its own.
#
# Page-level defects (a hand edit, a typed banner) necessarily trip clause 1 as
# well, because the page no longer matches the render. That is the gate working,
# not a leak, so those mutations keep clause 1 enabled and are exempt from the
# isolation rule. Data-level mutations skip clause 1, which is what proves the
# named clause stands on its own instead of riding on the catch-all.

def _mutate_fresh(st):
    st["page"] = st["page"].replace(
        "## The counted rows", "## The counted rows (edited by hand)", 1)


def _mutate_counted(st):
    for r in st["doc"]["rows"]:
        if r["tier"] == "T1":
            r["tier"] = "DEAD"
            break


def _mutate_tier(st):
    for r in st["doc"]["rows"]:
        if r["tier"] == "T2":
            r["tier"] = "DEAD"
            break


def _mutate_provenance(st):
    # Flip one counted row's verification from first-hand to a research pass:
    # both provenance counts on the page are then wrong.
    for r in st["doc"]["rows"]:
        if r["tier"] in COUNTABLE and str(r.get("verified_by", "")).startswith("me, "):
            r["verified_by"] = "research pass, re-checked but not re-fetched"
            return
    raise AssertionError("no first-hand counted row to flip")


def _mutate_mutations(st):
    # The page understates how many mutations the guard runs.
    st["page"] = re.sub(r"prove the guard can fail \(\d+/(\d+)\)",
                        lambda m: f"prove the guard can fail (9/{m.group(1)})",
                        st["page"], count=1)


def _mutate_reach(st):
    # The probe re-runs and records one more reachable endpoint; the page is
    # stale. Clause 1 would also catch this, so it is skipped here to show the
    # count clause alone is enough.
    st["reach"]["summary"]["reachable"] += 1


def _mutate_banner(st):
    # The defect this gate exists for: a banner typed into prose that no probe
    # recorded, in the tilde.zone bullet, which is where the real one was typed.
    st["page"] = st["page"].replace(
        "- **tilde.zone answers SSH**",
        "- **tilde.zone answers SSH** with `SSH-2.0-OpenSSH_9.9p1 Ubuntu-1ubuntu1`", 1)


def _mutate_banner_file(st):
    # The same defect from the other side: the page is untouched, but the
    # measurement file no longer records the banner the page prints, so the
    # page is asserting a string the probe does not have. The replacement has to
    # be a DIFFERENT build: an earlier version wrote 'Debian-2' where the file
    # said 'Debian-1', which still contains the page's token as a prefix, and
    # the clause correctly passed it.
    st["reach"]["results"]["tilde.green:22"]["banner"] = "SSH-2.0-OpenSSH_9.9 Debian-9"


def _mutate_drop_quote3(st):
    st["page"] = "\n".join(ln for ln in st["page"].split("\n")
                            if "Vendor says (quote3," not in ln)


def _mutate_new_quote3(st):
    # quote3 exists on 4 rows and the renderer now renders it. Give a fifth row
    # one and the gate must notice the page is behind the data.
    for r in st["doc"]["rows"]:
        if r["tier"] in COUNTABLE and not r.get("quote3"):
            r["quote3"] = "a quote nobody has put on the page yet"
            return
    raise AssertionError("every counted row already has a quote3")


def _mutate_relabel(st):
    # The MARKER on the page is edited, not the data: a verbatim quote is
    # relabelled RECONSTRUCTION. The data is unchanged, so this is purely a
    # page defect and must be caught as one.
    #
    # The marker is now its own line, "- **Vendor says (quote, VERBATIM):**",
    # with the quoted text on the following "> " lines, so the old
    # ", VERBATIM):** >" pattern matched nothing and this mutation reported NO-OP
    # - which reads like a weak mutation when it is a stale one.
    for ln in st["page"].split("\n"):
        if ln.endswith(", VERBATIM):**"):
            st["page"] = st["page"].replace(
                ln, ln.replace(", VERBATIM):**", ", RECONSTRUCTION):**"), 1)
            return
    raise AssertionError("no verbatim marker on the page to relabel")


def _mutate_fake_attribution(st):
    # A capture the page names stops containing the fragment: the page goes on
    # attributing the quote to bytes that no longer say it.
    #
    # It targets hashbang_clean_lurkers, which the page really does attribute
    # fragments to (hashbang.quote names it twice). An earlier version replaced
    # ctrlc_signup's text, and no attribution on the page names that capture,
    # so the clause had nothing to fire on and the mutation was reported MISSED
    # - which reads like the clause being weak when it was the mutation aiming
    # at nothing. A mutation that cannot be planted is not coverage.
    st["texts"]["hashbang_clean_lurkers"] = (
        "the page was re-fetched and no longer says this")


MUTATIONS = [
    ("hand-edit the page after the renderer wrote it",
     _mutate_fresh, CLAUSES[0], "differs from what tools/render-always-on-free.py", ()),
    ("promote a T1 row to DEAD without re-rendering (counted rows)",
     _mutate_counted, CLAUSES[1], "counted rows", (CLAUSES[0],)),
    ("promote a T2 row to DEAD without re-rendering (tier table)",
     _mutate_tier, CLAUSES[1], "tier T2", (CLAUSES[0],)),
    ("downgrade a first-hand row to a research pass (provenance table)",
     _mutate_provenance, CLAUSES[1], "first-hand rows", (CLAUSES[0],)),
    ("understate the guard's own mutation count in Reproduce",
     _mutate_mutations, CLAUSES[1], "guard mutation count", (CLAUSES[0],)),
    ("probe records one more reachable endpoint and the page is stale",
     _mutate_reach, CLAUSES[1], "reachability reachable", (CLAUSES[0],)),
    ("type an SSH banner into the page that no probe recorded",
     _mutate_banner, CLAUSES[2], "but not in verify/reachability.json", ()),
    ("the measurement file stops recording a banner the page prints",
     _mutate_banner_file, CLAUSES[2], "but not in verify/reachability.json", (CLAUSES[0],)),
    ("drop every quote3 from the page (4 rows carry one)",
     _mutate_drop_quote3, CLAUSES[3], ".quote3:", ()),
    ("a quote gains a quote3 nobody checked against the bytes",
     _mutate_new_quote3, CLAUSES[3], ".quote3:", (CLAUSES[0],)),
    ("relabel a verbatim quote on the page as a reconstruction",
     _mutate_relabel, CLAUSES[3], "where the data calls for", ()),
    ("a capture the page names no longer contains the fragment",
     _mutate_fake_attribution, CLAUSES[4], "does not contain it", (CLAUSES[0],)),
]


def mutate_run(state, guard, renderer, rendered):
    caught = 0
    for name, mutate, clause, expect, skip in MUTATIONS:
        # The guard module cannot be deep-copied, and no mutation touches it,
        # so it is passed through rather than carried in the state.
        st = {k: copy.deepcopy(v) for k, v in state.items()}
        try:
            mutate(st)
        except Exception as exc:            # a mutation that cannot be planted
            print(f"  NO-OP      {name}\n"
                  f"             <-- could not plant the defect: {exc}")
            continue
        if all(st[k] == state[k] for k in ("page", "doc", "reach", "texts")):
            print(f"  NO-OP      {name}\n"
                  f"             <-- the mutation changed nothing, so nothing was tested")
            continue
        print(f"  [{name}]")
        allf, per = check(st["page"], st["doc"], guard, st["reach"],
                          renderer, st["texts"], rendered, skip=skip)
        hit = per.get(clause, [])
        others = [f for c, fs in per.items() if c != clause for f in fs]
        named = [f for f in hit if expect in f]
        if named:
            caught += 1
            print(f"  CAUGHT     {name}")
            print(f"             by {clause}: {named[0]}")
            if skip:
                print(f"             ({', '.join(skip)} skipped so the clause is "
                      f"shown to stand alone)")
            if others:
                print(f"             ALSO tripped {len(others)} unrelated failure(s)")
        else:
            print(f"  MISSED     {name}")
            print(f"             {clause} did not fire; expected {expect!r}, got "
                  f"{(hit or ['<nothing>'])[0]}")
    total = len(MUTATIONS)
    print(f"\n{caught}/{total} mutations caught by the clause they name")
    return 0 if caught == total else 1


def main():
    strict = "--strict" in sys.argv
    if not PAGE.exists():
        print("docs/ALWAYS-ON-FREE.md does not exist; nothing to check. "
              "Run tools/render-always-on-free.py.")
        return 2

    renderer = load_module(RENDERER, "always_on_renderer")
    guard = load_module(GUARD, "always_on_guard")
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    reach = json.loads(REACH.read_text(encoding="utf-8")) if REACH.exists() else None
    committed = PAGE.read_text(encoding="utf-8")
    texts = renderer.capture_texts()

    # Re-render into a temp file, as the clause name says, and read it back.
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "ALWAYS-ON-FREE.md"
        tmp.write_text(renderer.render(), encoding="utf-8")
        rendered = tmp.read_text(encoding="utf-8")

    state = {"page": committed, "doc": doc, "reach": reach, "texts": texts}
    if "--mutate" in sys.argv:
        if not texts:
            print("REFUSING TO RUN MUTATIONS: there are no captures under "
                  "verify/pages/, so two of the five clauses cannot run and a "
                  "mutation count would be counting fewer checks than it "
                  "claims. Run: python3 verify/fetch.py")
            return 1
        print(f"mutating a passing gate ({len(lines_of(committed))} lines)\n")
        return mutate_run(state, guard, renderer, rendered)

    n_rows = len(doc["rows"])
    n_counted = sum(1 for r in doc["rows"] if r.get("tier") in COUNTABLE)
    print(f"rendered page gate - docs/ALWAYS-ON-FREE.md "
          f"({len(lines_of(committed))} lines, {n_counted}/{n_rows} counted, "
          f"{len(texts)} captures)")
    if not texts:
        print("\nNO CAPTURES under verify/pages/ (gitignored; run python3 verify/fetch.py).")
        print("Two clauses read those captures and cannot run here:")
        print("  - clause 1, the committed page against a fresh render. The committed")
        print("    page names capture files; a render here says CAPTURES ABSENT. That")
        print("    difference is an artefact of the missing directory, not drift, so")
        print("    reporting it would train a reader to ignore this gate.")
        print("  - clause 5, which checks that each capture the page names really")
        print("    contains the fragment attributed to it. Nothing to check against.")
        print("Clauses 2, 3 and 4 are run: they read the JSON, the reachability file")
        print("and the committed page, none of which are gitignored.")
        fails, _ = check(committed, doc, guard, reach, renderer, texts, committed,
                         skip=(CLAUSES[0], CLAUSES[4]))
        if fails:
            print(f"\nFAIL ({len(fails)})")
            for f in fails:
                print(" -", f)
            return 1
        print("\nNOT FULLY CHECKED. Clauses 2, 3 and 4 ran and passed. Clauses 1 and 5")
        print("could not run without verify/pages/, so exit 0 is NOT a claim that the")
        print("committed page matches this renderer. To check that: python3 verify/fetch.py")
        return 2 if strict else 0

    fails, _ = check(committed, doc, guard, reach, renderer, texts, rendered)
    if fails:
        print(f"\nFAIL ({len(fails)})")
        for f in fails:
            print(" -", f)
        return 1
    print("\nok rendered_page_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
