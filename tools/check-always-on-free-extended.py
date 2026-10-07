#!/usr/bin/env python3
"""check-always-on-free-extended.py - the five checks the census guard is missing.

tools/check-always-on-free.py passes on data that has quietly rotted. Six
mutations were measured against it and all six pass, because it only ever asks
whether a quote is TRUTHY, never whether it is REAL:

  oracle-a1-alwaysfree.quote   -> a fabricated sentence       PASSES
  a T2 row promoted to T1, keepalive and counts made consistent   PASSES
  all DEAD rows deleted, counts made consistent                   PASSES
  gcp-e2-micro.source           -> https://example.com/not-real PASSES
  a "research pass" row relabelled first-hand                    PASSES
  a DEAD row's quote set to null                                 PASSES

The first is the one that matters. The census exists because Oracle's 4 OCPU /
24 GB figure was wrong, and it corrected that by re-reading the source bytes.
A guard that cannot tell a verified quote from an invented one cannot protect
the correction it was written to make: the next Oracle-sized error lands in the
file and the guard stays green. So this module checks that quotes are
TRACEABLE - that some capture under verify/pages/ actually contains them - and
the other four clauses close the four structural holes around it.

It is an ADDITION, never a replacement. check-always-on-free.py is imported and
its check() is called first, so nothing it catches can be caught less often
here. Its clauses are not restated, only extended.

  1. QUOTE FIDELITY. A counted row's quote / quote2 / quote3 must be findable
     in a capture. Four shapes pass, and each is checked honestly:
       - VERBATIM. The quote is a contiguous run of the capture's text.
       - TABLE RECONSTRUCTION. The quote joins table cells with " | ". Passes
         only if EVERY |-separated fragment is present in the SAME capture, and
         at least one fragment is three words or longer. Both halves are
         needed: requiring only the long fragments lets "Account plan | 15
         GB-month | CPU time 10 ms" pass on one coincidental four-word match,
         and requiring only short ones lets any two tokens match any page.
       - ELISION. The quote uses " ... " to mark a jump. Same rule, same
         reason.
       - FOLDED. Contiguous once whitespace is ignored. See folded() below for
         why that tolerance exists and exactly what it forgives.
     Text is normalised the way verify/claim.py normalises it (drop
     script/style/svg, drop tags, html.unescape, collapse whitespace, lowercase,
     fold smart quotes, dashes and the multiplication sign), plus the one
     whitespace tolerance documented on folded().

  2. TIER INTEGRITY. The tier definitions in the JSON are not decoration:
     T1 means "no idle sleep, no hard session cap, no expiry". So a T1 row may
     not carry a keepalive (that means it needs one) and may not disclose an
     expiry, login-expiry or retention wall in idle_or_session_limit. A DEAD
     row may not carry a keepalive or a relay, because nothing a relay or
     keepalive fixes is not what killed it. And a counted row may not name a
     QUOTA unit in spec or idle_or_session_limit: tier_note says a relay
     defeats liveness and networking walls but "cannot defeat QUOTA walls
     (120 core-hours, 24h caps, trial clocks, PRO gates)", so a row whose own
     spec admits a monthly cap is not a row a relay rescues. neon-free WAS
     counted T2 on exactly this reasoning and its own cited page put a 24/7
     database at ~182.5 CU-hr against a 100 CU-hr allowance; commit 940fb87
     moved it to DEAD. A quota unit is not by itself a wall, though: see
     quota_arithmetic(), because the two rows that quote an allowance larger
     than their own usage (oracle 1,488 against 1,500 OCPU-h, render 744
     against 750 instance-hours) fit, and failing them would be noise that
     trains a reader to skip this clause.

  3. PROVENANCE HONESTY. A verified_by that starts with "me, " claims a human
     read bytes off a first-party page. That claim must resolve to a capture
     that can be re-fetched: verify/fetch.py's urls dict is the registry of
     what is re-fetchable, and a name that is not a key there can never be
     regenerated, so it is a pointer to evidence that does not exist. Two
     failures, kept apart on purpose: a name that is not a KEY in urls, and a
     name that IS a key but has no file on disk (sdf_members05 today - the
     sdf.org capture is absent, so the row's own bytes are not in the repo).

  4. SOURCE PLAUSIBILITY. A counted row's source must be an http(s) URL on a
     host that is not a reserved placeholder, so "https://example.com/" cannot
     pass for a citation. Every counted row's host is printed, because a host
     is something a human can eyeball in a second and a regex cannot certify.

  5. ROW INVENTORY. The row ids are pinned to MANIFEST below. Without it,
     deleting the DEAD rows is invisible: the counted floor still holds and the
     declared counts can be made consistent, which is exactly what a mutation
     does. A census that can be quietly emptied is not a census. (The DEAD count
     is 18, not the 17 an earlier comment here said; this file's comments were
     written before 940fb87 moved neon-free from T2 to DEAD.)

WHAT IS *NOT* A FAILURE HERE - the distinction this file exists to keep

Many rows honestly say "research pass, first-party fetch" and ship no capture.
That is a labelled limitation, not a defect: the row told the reader who did
the work and what weight to give it. So the absence of a capture is reported
as UNVERIFIABLE - printed, counted, and exited 0 on - and only these fail:

     "claims first-hand, and the artefact is absent"   -> FAIL (clause 3)
     "says carried, and there is no artefact to check" -> report only

A research-pass row is never failed for lacking a capture it never claimed to
have. What it IS failed for is a quote that a capture contradicts, which is a
different claim: there the bytes are present and the quote is wrong. Clause 1
draws that line by asking whether the row has any capture to check against at
all - one it names, or one registered for its own source URL.

Usage: python3 tools/check-always-on-free-extended.py           # check
       python3 tools/check-always-on-free-extended.py --mutate  # prove it fails
"""
import copy
import html
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
DATA = os.path.join(ROOT, "data", "always-on-free.json")
PAGES = os.path.join(ROOT, "verify", "pages")


def _load(module_name, path):
    """Import a file that is not a valid module name (check-always-on-free.py)
    without duplicating a single one of its clauses."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = _load("check_always_on_free", os.path.join(TOOLS, "check-always-on-free.py"))

# verify/fetch.py's urls dict is the registry of pages this repo can re-fetch.
# It chdir()s to ROOT on import, so the cwd is put back: this module resolves
# every path absolutely and must not leave the caller's shell somewhere else.
_cwd = os.getcwd()
try:
    FETCH = _load("verify_fetch", os.path.join(ROOT, "verify", "fetch.py"))
finally:
    os.chdir(_cwd)
URLS = getattr(FETCH, "urls", {})

# verify/fetch.py's record of which pages are known to be unreachable from SOME
# hosts. Kept as a separate name so a reader can see at a glance that this file
# reads another tool's decision rather than making its own.
UNREACHABLE = getattr(FETCH, "KNOWN_UNREACHABLE", {}) or {}

COUNTABLE = BASE.COUNTABLE

# The 40 row ids at commit 4cfca5b, read out of the JSON rather than typed by
# hand. An id that appears or disappears is a change to the census's shape, and
# shape is what a reader trusts.
MANIFEST = frozenset({
    "gcp-e2-micro",
    "oracle-a1-alwaysfree",
    "northflank-sandbox",
    "oracle-e2-micro-alwaysfree",
    "render-free-web-service",
    "azure-appservice-f1",
    "supabase-free-project",
    "modelscope-studio",
    "sdf-free-shell",
    "blinkenshell",
    "cloudflare-do",
    "tilde-town",
    "hashbang",
    "serv00",
    "pythonanywhere",
    "alwaysdata-free",
    "hf-spaces-zerogpu",
    "koyeb-free-instance",
    "neon-free",
    "ctrl-c-club",
    "tilde-green",
    "tilde-club",
    "tilde-guru",
    "railway-free-vm",
    "github-codespaces",
    "google-cloud-shell",
    "modal-sandbox",
    "aws-free-tier",
    "azure-free-account",
    "hf-spaces-cpu-basic",
    "hf-dev-mode",
    "render-postgres-free",
    "killercoda",
    "fly-io",
    "replit-free",
    "play-with-docker",
    "cloudflare-containers",
    "github-actions",
    "inference-apis",
    "browser-linux",
})

# --- quote normalisation -------------------------------------------------
# verify/claim.py normalises a capture so a phrase survives being re-rendered
# by the vendor's templating. Same idea here, run over a whole quote instead
# of a short phrase, plus the glyph folds a transcription actually makes.
#
# Folded deliberately: the multiplication sign U+00D7 for "x" (Northflank
# prints "2× free services"), the ellipsis character for three dots, en and
# em dashes for hyphen, and both directions of smart quotes. These are
# transcription equivalences, not content changes.

_GLYPH_FOLDS = (
    ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
    ("–", "-"), ("—", "-"), ("×", "x"), ("…", "..."), ("•", " "),
    ("·", " "), (" ", " "),
)
_DROP_TAGS = re.compile(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>")
_ANY_TAG = re.compile(r"(?s)<[^>]+>")
_WS = re.compile(r"\s+")
_ELISION = re.compile(r"\s*\.\.\.\s*")
_TABLE_SPLIT = re.compile(r"\s*\|\s*")

# verify/pages/<name>.html, and the "captures under verify/pages/ as a, b, c"
# form ctrl-c-club and tilde.club use.
RE_CAPTURE_PATH = re.compile(r"verify/pages/([A-Za-z0-9_.-]+)\.html")

# A row whose capture is absent only because this host cannot reach the vendor
# must SAY that in its own verified_by. Without this, "unreachable from here"
# would become a general excuse for a capture that was never taken, which is the
# opposite of what the clause is for. The wording has to name the host-
# dependence, not merely mention the filename.
RE_UNREACHABLE_DISCLOSED = re.compile(
    r"not\s+re-?fetchable|unreachable|does\s+not\s+resolve|502|504|"
    r"not\s+reproducible\s+from\s+(?:every|this|here)|host[- ]dependent",
    re.I,
)
RE_CAPTURE_LIST = re.compile(r"under verify/pages/[^)]*\bas\s+([A-Za-z0-9_., -]+)", re.I)


def _flatten(html_text):
    """Tags out, entities in, glyphs folded. No whitespace collapsing yet.

    A capture that is not HTML at all is returned UNTOUCHED, and that is a real
    case rather than a hypothetical one: two of the captures this file reads are
    a shell script and a YAML file served from GitHub raw under a .html name
    (hashbang_clean_lurkers, hashbang_limits). Tag-stripping a shell script eats
    every `<...>` redirection and mangles the lines between them, so a verbatim
    quote from the script stops matching and reads as a fabrication. The tell is
    cheap and reliable: real HTML from these vendors has a <html or <!doctype,
    and a script or a YAML document has neither.

    The check is on the CONTENT, not on the extension, so renaming a capture
    cannot change the verdict.
    """
    head = html_text[:4096].lower()
    if "<html" not in head and "<!doctype" not in head and "<body" not in head:
        return html_text
    text = _DROP_TAGS.sub(" ", html_text)
    text = _ANY_TAG.sub(" ", text)
    text = html.unescape(text)
    for bad, good in _GLYPH_FOLDS:
        text = text.replace(bad, good)
    return text


def flat(text):
    """The comparable form: collapsed whitespace, lowercased.

    This is verify/claim.py's normal form. A quote matches a capture when its
    flat form is a contiguous run of the capture's flat form.
    """
    return _WS.sub(" ", _flatten(text)).strip().lower()


def folded(text):
    """flat() with EVERY space removed.

    Needed, and admitted rather than hidden: stripping tags puts a space where
    an element boundary was, so "us-west1</span><span>." flattens to
    "us-west1 ." and a correctly transcribed "us-west1." stops matching. Four
    of the shipped quotes differ from their capture by that artefact alone
    (gcp-e2-micro.quote, oracle-a1-alwaysfree.quote,
    oracle-e2-micro-alwaysfree.quote, hf-spaces-zerogpu.quote), and without
    this they would read as fabrications. Whitespace is the only thing forgiven
    - no word, digit or mark is dropped - so a fabricated sentence still
    matches nothing. A quote that clears the bar this way is reported as
    FOLDED rather than VERBATIM so a reader knows it was not a contiguous run.
    """
    return _WS.sub("", _flatten(text)).lower()


# Whitespace-forgiveness is not a licence to quote three letters. Measured on
# the shipped corpus: `a b c` folds to `abc` and was ACCEPTED inside `gitlabci`
# in cf_workers_limits, and `to to` folds to `toto` and was ACCEPTED inside
# `backtotop` in blinkenshell_limits. Two of twelve invented quotes passed
# because of it. Every shipped FOLDED quote is long, so this floor changes no
# verdict on real data and closes the hole.
#
# 32 characters with no whitespace is roughly four words, which is below the
# 4-gram rule this same file applies to contiguous text and above the 3-word
# table-cell fragments that legitimately have no whitespace.
FOLDED_MIN_CHARS = 32

# A quote shorter than this is not accepted as VERBATIM on a substring hit
# alone. Same measurement, different route: `to to` is a contiguous substring of
# `backtotop` in blinkenshell_limits, so it matched VERBATIM and the fold floor
# could not see it. Two floors, because there are two routes in.
#
# The real defence against a short quote is having a real quote: every shipped
# counted row's primary quote is far longer than this, so no real row is
# affected. What it removes is the ability to certify a two-word string.
VERBATIM_MIN_CHARS = 24


def _fragments(text, splitter):
    """Every fragment of a spliced quote, and whether any is long enough to
    count as evidence on its own.

    Both halves are load-bearing. Every fragment must be checked, not only the
    long ones: a quote of "Account plan | 15 GB-month | CPU time 10 ms" has one
    four-word fragment that sits happily on Cloudflare's limits page, and a
    rule that only inspected it would let the other two be invented. But a
    one- or two-word fragment is a coincidence every page has ('free', 'per
    month'), so at least one long fragment is required before an empty
    fragment set can be read as a pass.
    """
    parts = [f.strip() for f in splitter.split(text) if f.strip()]
    has_long = any(len(p.split()) >= 3 for p in parts)
    return parts, has_long


def _reconstruction_parts(quote_flat, splitter):
    """The fragments of a spliced quote, or None if this splitter does not
    actually split it.

    None matters: if the quote contains no ' ... ' then the elision splitter
    returns the whole quote as one fragment, whose containment test is just
    the verbatim test again. That is not wrong, it is 33 redundant substring
    scans per quote, and it would report a verbatim quote as an "elision".
    """
    parts, has_long = _fragments(quote_flat, splitter)
    if len(parts) < 2 or not has_long:
        return None
    return parts


def match_quote(quote, captures):
    """Return (capture_name, strategy) or (None, None).

    Strategies, in the order they are tried across every capture, strongest
    first, so a quote that IS verbatim somewhere is reported as verbatim:

      VERBATIM  contiguous run of one capture's flat text
      TABLE     ' | ' reconstruction, EVERY fragment in the SAME capture
      ELISION   ' ... ' marked jump, both sides in the SAME capture
      FOLDED    contiguous after whitespace is ignored (see folded())

    TABLE and ELISION deliberately require every fragment in one capture. That
    is what makes the modelscope-studio row a finding rather than a pass: its
    quote splices modelscope_hw and modelscope_ai_hw into one string, so no
    single capture contains it and no single page said it.
    """
    if not isinstance(quote, str) or not quote.strip():
        return None, None
    fq = flat(quote)
    # A short quote can be a substring of an unrelated word - `to to` is a
    # contiguous run inside `backtotop` - so a short string is not accepted as
    # VERBATIM on containment alone. Every shipped counted row's primary quote is
    # far longer than this, so no real row is affected.
    if len(fq) >= VERBATIM_MIN_CHARS:
        for name, body in captures.items():
            if fq in body["flat"]:
                return name, "verbatim"
    for splitter, strategy in ((_TABLE_SPLIT, "table"), (_ELISION, "elision")):
        parts = _reconstruction_parts(fq, splitter)
        if not parts:
            continue
        for name, body in captures.items():
            if all(p in body["flat"] for p in parts):
                return name, strategy
    fold_q = folded(quote)
    # The floor is checked here rather than inside folded(), because folded() is
    # also used to normalise the CAPTURES, where a short body legitimately folds
    # to a short string. Only the quote side is held to the floor.
    if fold_q and len(fold_q) >= FOLDED_MIN_CHARS:
        for name, body in captures.items():
            if fold_q in body["folded"]:
                return name, "folded"
    return None, None


_CAPTURES = None


def captures():
    """Normalised text of every capture in verify/pages/, loaded once."""
    global _CAPTURES
    if _CAPTURES is None:
        _CAPTURES = {}
        if os.path.isdir(PAGES):
            for entry in sorted(os.listdir(PAGES)):
                if not entry.endswith(".html"):
                    continue
                name = entry[: -len(".html")]
                path = os.path.join(PAGES, entry)
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        raw = fh.read()
                except OSError:
                    continue
                _CAPTURES[name] = {"flat": flat(raw), "folded": folded(raw)}
    return _CAPTURES


def capture_names_on_disk():
    if not os.path.isdir(PAGES):
        return set()
    return {e[: -len(".html")] for e in os.listdir(PAGES) if e.endswith(".html")}


# --- clause 1: quote fidelity -------------------------------------------
QUOTE_FIELDS = ("quote", "quote2", "quote3")


def _url_key(url):
    """Scheme, query, fragment and trailing slash off, so a row's source and
    fetch.py's registry entry for the same page compare equal."""
    if not isinstance(url, str):
        return None
    s = url.strip().lower()
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s)
    s = s.split("#", 1)[0].split("?", 1)[0]
    return s[:-1] if s.endswith("/") else s


SOURCE_KEYS = {_url_key(u): k for k, u in URLS.items()}
SOURCE_HOSTS = {}
for _name, _url in URLS.items():
    _host = (_url_key(_url) or "").split("/")[0]
    SOURCE_HOSTS.setdefault(_host, _name)


def source_captures(row):
    """Captures registered for this row's own source page: the exact URL match
    first, then - only for a row that claims first-hand - any capture sharing
    the source's host.

    The host fallback exists because blinkenshell's source is
    blinkenshell.org/wiki/ while the registered capture is blinkenshell.org/
    wiki/FAQ. Without it that row would be excused as 'nothing to check', when
    in fact the quote it ships is in none of its three captures. It is offered
    ONLY to first-hand rows: a research pass that names no capture and points
    at a page nothing was ever fetched for has honestly said so.
    """
    found = []
    exact = SOURCE_KEYS.get(_url_key(row.get("source")))
    if exact:
        found.append(exact)
    if BASE.provenance(row) == "read":
        host = (_url_key(row.get("source")) or "").split("/")[0]
        by_host = SOURCE_HOSTS.get(host)
        if by_host and by_host not in found:
            found.append(by_host)
    return found


def capture_names_named(row):
    """Capture names the row's verified_by points at, in every form the census
    uses them: 'verify/pages/<name>.html', 'under verify/pages/ as a, b, c',
    and a bare '<name>.html' or key."""
    vb = row.get("verified_by")
    if not isinstance(vb, str):
        return set()
    names = set(RE_CAPTURE_PATH.findall(vb))
    for blob in RE_CAPTURE_LIST.findall(vb):
        for part in blob.split(","):
            part = part.strip()
            if part and re.fullmatch(r"[A-Za-z0-9_.-]+", part):
                names.add(part)
    for key in URLS:
        if re.search(r"(?<![\w./-])" + re.escape(key) + r"(?![\w-])", vb):
            names.add(key)
    return names


def quote_faults(row, caps, on_disk):
    """Clause 1. Returns (failures, unverifiable notes, trace lines)."""
    fails, notes, traces = [], [], []
    rid = row.get("id", "<no id>")

    present = [f for f in QUOTE_FIELDS if isinstance(row.get(f), str) and row[f].strip()]
    if not present:
        # Nothing quoted at all. The base guard already fails a COUNTED row for
        # this; what it cannot see is a first-hand DEAD or UNVERIFIED row whose
        # own verified_by says the bytes were read, where the absence of any
        # quote means the evidence the row points at is never put on the page.
        named = [n for n in capture_names_named(row) if n in on_disk]
        if named:
            fails.append(
                f"{rid}: names capture {', '.join(sorted(named))} but carries no "
                f"quote in {', '.join(QUOTE_FIELDS)} to check against it"
            )
        return fails, notes, traces

    # Is there a capture to check this row against at all? Named first-hand
    # evidence, or the page its own source points at.
    on_disk_named = [n for n in capture_names_named(row) if n in on_disk]
    on_disk_source = [n for n in source_captures(row) if n in on_disk]
    checkable = on_disk_named + [n for n in on_disk_source if n not in on_disk_named]

    for field in present:
        # A row that HAS its own captures is held to them. Searching the union
        # of all 35 captures and accepting any hit is how Oracle's A1 sentence
        # ended up quoted under "Google Cloud Free Tier - Compute Engine
        # e2-micro", with every gate green: the quote was found, just in the
        # wrong provider's page. Measured as an attack and NOT caught before
        # this clause.
        #
        # The rule is therefore: own captures first, and a hit outside them is
        # a finding that names the foreign capture. Where the row has no
        # capture of its own - a research-pass row with none, which is honestly
        # labelled - the union search still runs and a hit is still a hit,
        # because there is nothing to hold it to and failing it would fail an
        # honestly-carried row for someone else's evidence.
        own = {n: caps[n] for n in checkable if n in caps}
        name, strategy = match_quote(row[field], own)
        if name:
            traces.append(f"{rid}.{field} -> {name} ({strategy})")
            continue
        foreign, how = match_quote(row[field], caps)
        if foreign and foreign not in own:
            fails.append(
                f"{rid}.{field}: the quote is traceable only to "
                f"verify/pages/{foreign}.html, which is NOT this row's capture "
                f"(its own is {', '.join(sorted(own)) or 'none on disk'}); it "
                f"matches by {how}, so the row is quoting another provider's page"
            )
            traces.append(f"{rid}.{field} -> {foreign} ({how}) FOREIGN")
            continue
        if foreign:
            traces.append(f"{rid}.{field} -> {foreign} ({how})")
            continue
        if not checkable:
            notes.append(
                f"{rid}.{field}: no capture for this row in verify/pages/ "
                f"(verified_by: {(row.get('verified_by') or '')[:60]}...)"
            )
            continue
        fails.append(
            f"{rid}.{field}: quote is not traceable to any capture in "
            f"verify/pages/ (checked {len(caps)} captures: verbatim, ' | ' table "
            f"reconstruction, ' ... ' elision, whitespace-folded); {checkable[0]} "
            f"is this row's own capture and does not contain it"
        )
    return fails, notes, traces


# --- clause 2: tier integrity -------------------------------------------
# T1 is defined in the file as "No idle sleep, no hard session cap, no
# expiry. It just runs." A T1 row naming any of those contradicts the tier it
# is filed under, whichever one the author meant.
#
# EXPIRY is the account-lifetime class of wall. QUOTA is the usage-metered
# class. They are separate lists because they are separate arguments: a T1 row
# has no business having either, but only QUOTA carries the tier_note argument
# ("a relay ... cannot defeat QUOTA walls") that makes it fatal to a counted
# row without a hard_wall.
#
# The QUOTA list is the brief's list plus the units it names by a different
# spelling in the same two families: "CU-hr"/"CU-hrs", "core-hours",
# "CPU-minutes", "instance-hours", "GB-month", "hrs/", "hours per month",
# "$/mo credit", and "OCPU-h" (Oracle's own spelling, spec line of
# oracle-a1-alwaysfree). A first version of this file failed any counted row
# naming a quota unit, which failed oracle-a1-alwaysfree (1,500 OCPU-h) and
# render (750 instance-hours). Both FIT: 2 OCPU x 744 h = 1,488 against 1,500,
# and the longest month is 744 h against 750. quota_arithmetic() now checks the
# numbers instead of the vocabulary, and neither row fails on shipped data. An
# earlier comment here said oracle failed this clause; it does not.
EXPIRY_PHRASES = re.compile(
    r"expir|retention|archiv|purge|self-clos|login[- ]expir|account[- ]clos", re.I
)
QUOTA_UNITS = re.compile(
    r"hrs/|hours?\s*(?:per|/|a\s+)\s*(?:day|month|week|year)|"
    r"cu-?hrs?\b|core[- ]hours?\b|cpu[- ]minutes?\b|instance[- ]hours?\b|"
    r"gb[- ]?months?\b|ocpu[- ]h\b|\$/mo\s*credit",
    re.I,
)

# A row that spells out the arithmetic showing its quota FITS is exempt from the
# unit rule even when the numbers are not parseable here. "1,488 against 1,500",
# "744 h against 750" are the sentences a reader uses to check the claim, and
# requiring this file to re-derive them from prose is asking for the wrong kind
# of trust.
QUOTA_FITS_NOTE = re.compile(
    r"\b\d[\d,]*\s*(?:ocpu[- ]?h|core[- ]?hours?|cu[- ]?hrs?|instance[- ]?hours?"
    r"|gb[- ]?hours?|hours?)\b[^.]{0,80}?\bagainst\b|\bagainst\b[^.]{0,80}?"
    r"\b\d[\d,]*\s*(?:ocpu[- ]?h|core[- ]?hours?|cu[- ]?hrs?|instance[- ]?hours?"
    r"|gb[- ]?hours?|hours?)\b|"
    r"\bexactly one (?:fits|service fits|instance fits)\b|\bone always-on\b",
    re.I,
)

# Longest month, in hours. A month of wall-clock time is at most 31 days, so
# any allowance stated in instance-hours above this cannot be exhausted by one
# always-on instance.
HOURS_IN_LONGEST_MONTH = 31 * 24

_ALLOWANCE = {
    "oracle": 1500,          # OCPU-hours per month, quoted from the vendor
    "render": 750,           # free instance-hours per workspace per month
    "supabase": None,
}


def quota_arithmetic(row):
    """Return (usage_hours, allowance_hours) when this row's own text states both.

    Deliberately narrow. It recognises exactly the two shapes that actually
    decide a quota wall - an OCPU-hour allowance against an instance's own
    OCPU count, and an instance-hour allowance against a calendar month - and
    returns (None, None) for anything else so the caller falls back rather than
    guessing. A wider net here would be a regex pretending to be arithmetic.
    """
    blob = " ".join(str(row.get(k) or "") for k in ("spec", "caveats", "quote",
                                                     "idle_or_session_limit"))
    rid = row.get("id", "")
    low = blob.lower()

    # OCPU-hour allowance vs the instance's own OCPU count.
    m_allow = re.search(r"([\d,]+)\s*ocpu[- ]?h", low)
    m_count = re.search(r"(\d+(?:\.\d+)?)\s*ocpu\b(?!\s*-?\s*h)", low)
    if m_allow and m_count:
        allowance = float(m_allow.group(1).replace(",", ""))
        ocpus = float(m_count.group(1))
        return round(ocpus * HOURS_IN_LONGEST_MONTH, 1), allowance

    # Instance-hour allowance vs a calendar month.
    m_inst = re.search(r"([\d,]+)\s*instance[- ]hours?", low)
    if m_inst:
        allowance = float(m_inst.group(1).replace(",", ""))
        return float(HOURS_IN_LONGEST_MONTH), allowance

    return None, None
# "no login expiry found", "none documented", "not a session cap". A T1 row
# stating it has NO wall must not be failed for the words it denies.
#
# The scope is deliberately three words and word-characters only. The first
# version allowed any 40 characters, which meant the row
#     "none, but the account expires 12 months after signup"
# was excused because the word "none," appeared earlier in the same sentence -
# a negation guard wide enough to swallow its own contradiction is worse than
# no guard, because it reads as coverage. A comma also ends the negation: "no
# idle limit, but the account expires" is a contradiction, not a denial.
_NEGATED = re.compile(
    r"\b(?:no|not|never|without|none|cannot|isn'?t|doesn'?t|nothing)\s+"
    r"(?:\w+\s+){0,3}$",
    re.I,
)


def walls_in(field_text, pattern):
    """Wall phrases in a row's own words, ignoring ones the row is denying."""
    if not isinstance(field_text, str):
        return []
    out = []
    for m in pattern.finditer(field_text):
        if _NEGATED.search(field_text[max(0, m.start() - 60):m.start()]):
            continue
        if m.group(0).lower() not in {w.lower() for w in out}:
            out.append(m.group(0))
    return out


def tier_faults(row):
    """Clause 2."""
    fails = []
    rid = row.get("id", "<no id>")
    tier = row.get("tier")
    if tier not in COUNTABLE and tier != "DEAD":
        return fails

    if tier == "DEAD":
        # hard_wall is where a DEAD row is required to say what nothing fixes.
        # If it also names a keepalive or a relay it is contradicting itself:
        # one of those two would have been tried, and one of them is named as
        # the thing the wall is NOT.
        if row.get("keepalive"):
            fails.append(
                f"{rid}: DEAD row carries a keepalive "
                f"({str(row['keepalive'])[:60]}...) - hard_wall says nothing a "
                f"keepalive fixes, so the two cannot both be true"
            )
        if row.get("relay"):
            fails.append(
                f"{rid}: DEAD row carries a relay ({str(row['relay'])[:60]}...) - "
                f"hard_wall says nothing a relay fixes, so the two cannot both be true"
            )
        # A DEAD verdict is a claim too. It excludes a provider from the count,
        # so it is the cheapest place in the file to assert something with no
        # evidence: a row nobody bothered to quote cannot be checked, and the
        # reader has no way to tell "excluded on the vendor's own wording" from
        # "excluded and never looked at". A DEAD row that CLAIMS a capture must
        # show a quote from it. Rows labelled `research pass` with no capture
        # stay UNVERIFIABLE and exit 0 - that is honest labelling, not silence.
        if BASE.provenance(row) == "read" and not any(
                row.get(q) for q in ("quote", "quote2", "quote3")):
            fails.append(
                f"{rid}: DEAD row claims first-hand verification but carries no "
                f"quote in quote, quote2 or quote3, so the bytes it says it read "
                f"produce no evidence here either"
            )
        return fails

    if tier == "T1":
        if row.get("keepalive"):
            fails.append(
                f"{rid}: tier T1 is always-on as-is but names a keepalive "
                f"({str(row['keepalive'])[:60]}...) - a keepalive means it needs one"
            )
        expiries = walls_in(row.get("idle_or_session_limit"), EXPIRY_PHRASES)
        if expiries:
            fails.append(
                f"{rid}: tier T1 says no expiry, but idle_or_session_limit carries "
                f"the expiry/retention phrase(s) {', '.join(repr(e) for e in expiries)}"
            )

    # A quota UNIT is not a quota WALL. The first version failed any counted row
    # whose text contained a quota unit, which failed two rows that are correct:
    #
    #   oracle-a1-alwaysfree  1,500 OCPU-h allowance; 2 OCPU x 744 h = 1,488
    #   render-free-web-service 750 instance-hours; the longest month is 744 h
    #
    # Both fit with hours to spare, so neither is a wall, and a guard that fails
    # them is noise that trains a reader to skip it. A unit only becomes a wall
    # when the stated allowance is SMALLER than the stated usage, so this checks
    # the arithmetic where the row states both numbers, and falls back to the
    # unit match only when it cannot tell.
    usage_h, allowance_h = quota_arithmetic(row)
    if usage_h is not None and allowance_h is not None:
        if usage_h > allowance_h:
            fails.append(
                f"{rid}: counted as tier {tier} but its own numbers make the "
                f"quota a wall: {usage_h} h of use against a {allowance_h} h "
                f"allowance, and tier_note says a relay cannot defeat a quota "
                f"wall"
            )
    else:
        quota = (walls_in(row.get("spec"), QUOTA_UNITS)
                 + walls_in(row.get("idle_or_session_limit"), QUOTA_UNITS))
        if quota and not row.get("hard_wall") and not QUOTA_FITS_NOTE.search(
                " ".join(str(row.get(k) or "") for k in ("spec", "idle_or_session_limit",
                                                         "caveats", "keepalive"))):
            # tier_note: "A relay defeats LIVENESS walls ... but cannot defeat
            # QUOTA walls (120 core-hours, 24h caps, trial clocks, PRO gates)."
            fails.append(
                f"{rid}: counted as tier {tier} but names a quota unit "
                f"({', '.join(sorted(set(quota)))}) with no hard_wall, and states "
                f"no allowance that covers it; tier_note says a relay cannot "
                f"defeat a quota wall"
            )
    return fails


# --- clause 3: provenance honesty ---------------------------------------
def provenance_faults(row, on_disk, notes=None):
    """Clause 3. verified_by is a claim about evidence. A first-hand claim must
    resolve to something re-fetchable: verify/fetch.py's urls dict is that
    registry, so a name absent from it can never be regenerated.

    `notes` collects conditions that are true of THIS HOST rather than of the
    row, so they can be reported without failing. Kept as an argument rather
    than a module global because the mutation suite calls this directly.
    """
    fails = []
    if notes is None:
        notes = []
    rid = row.get("id", "<no id>")
    vb = row.get("verified_by")
    if not isinstance(vb, str) or not vb.strip():
        return fails
    named = sorted(capture_names_named(row))

    for name in named:
        if name not in URLS:
            key = sorted(k for k in URLS if name in k or k in name)
            fails.append(
                f"{rid}: verified_by names a capture that is not a fetchable key: "
                f"verify/pages/{name}.html (fetch.py has "
                f"{', '.join(key) if key else 'no similar key'})"
            )
        elif name not in on_disk:
            # A capture that is missing because this host cannot reach the
            # vendor is a DIFFERENT fact from one that is missing because the
            # row names a key nobody ever fetched. sdf.org returns 502/504
            # through some egress proxies, so on those hosts its captures cannot
            # exist; failing the census on that says the row was fabricated,
            # which is a different and false accusation.
            #
            # verify/fetch.py's KNOWN_UNREACHABLE block is the record of which
            # pages are known to be unreachable from some hosts. A row naming
            # one of those is reported as UNVERIFIABLE-HERE, counted, and exits
            # 0 - the row's own verified_by is required to SAY that the bytes
            # are not re-fetchable from every host, so the claim cannot be used
            # to launder a capture that simply was never taken.
            unreachable = UNREACHABLE
            if name in unreachable:
                notes.append(
                    f"{rid}: verified_by names verify/pages/{name}.html, absent "
                    f"here because {unreachable[name]}; this is a property of "
                    f"this host, not of the row"
                )
                if not RE_UNREACHABLE_DISCLOSED.search(vb or ""):
                    fails.append(
                        f"{rid}: names verify/pages/{name}.html, which is absent "
                        f"here ({unreachable[name]}), but verified_by does not "
                        f"disclose that the bytes are not re-fetchable from every "
                        f"host"
                    )
                continue
            fails.append(
                f"{rid}: verified_by names verify/pages/{name}.html, which is a "
                f"key in verify/fetch.py but has NO capture on disk - the bytes it "
                f"says it read are not in this repo"
            )

    if BASE.provenance(row) == "read" and not named:
        fails.append(
            f"{rid}: claims first-hand verification but names no capture in "
            f"verify/pages/, so the bytes it says it read cannot be re-read"
        )
    return fails


# --- clause 4: source plausibility --------------------------------------
PLACEHOLDER_HOSTS = {
    "example.com", "example.org", "example.net", "example",
    "localhost", "127.0.0.1", "0.0.0.0", "test", "invalid",
    "yourdomain.com", "my-site.com", "site.com", "domain.com",
}
PLACEHOLDER_WORDS = re.compile(
    r"placeholder|example\.(com|org|net)|your-?domain|change-?me|\bTODO\b|\bTBD\b|\bXXX\b",
    re.I,
)


def source_faults(row):
    """Clause 4. Returns (failures, host lines)."""
    fails = []
    rid = row.get("id", "<no id>")
    src = row.get("source")
    if not isinstance(src, str) or not src.strip():
        return fails, []  # the base guard already fails a counted row here
    if not re.match(r"^https?://", src.strip(), re.I):
        fails.append(f"{rid}: source is not an http(s) URL: {src!r}")
        return fails, []
    host = src.strip().split("//", 1)[1].split("/", 1)[0].split(":", 1)[0].lower()
    if host in PLACEHOLDER_HOSTS or host.endswith(".example") or ".invalid" in host:
        fails.append(
            f"{rid}: source host {host!r} is a reserved placeholder host, not a "
            f"citable page: {src!r}"
        )
    elif PLACEHOLDER_WORDS.search(src):
        fails.append(f"{rid}: source looks like a placeholder: {src!r}")
    return fails, [f"{rid}: {host}"]


# --- clause 5: row inventory --------------------------------------------
def inventory_faults(rows):
    """Clause 5. Deleting rows is invisible to every other clause unless the
    declared counts are left stale, and a mutation makes them consistent."""
    fails = []
    ids = [r.get("id") for r in rows]
    seen = set()
    for rid in ids:
        if rid in MANIFEST or rid in seen:
            continue
        seen.add(rid)
        fails.append(f"{rid}: row id is in the data but NOT in the committed manifest")
    for rid in sorted(MANIFEST - set(ids)):
        fails.append(
            f"{rid}: manifest row id is missing from the rows array "
            f"({len(MANIFEST) - len(MANIFEST - set(ids))} of {len(MANIFEST)} present)"
        )
    return fails


# --- the driver ----------------------------------------------------------
def scan(doc):
    """Return (failures, unverifiable notes, trace lines, host lines).

    The base guard runs FIRST and its failures are returned unchanged, so this
    module can only ever add a failure. check() is failures-only, so a caller
    importing it sees exactly what fails and nothing else; the notes are what
    the human needs and are printed by main().

    rows is shape-checked BEFORE BASE.check() is called, because the base guard
    does `r.get("id")` on every element and raises AttributeError if the array
    holds anything that is not an object. A guard that crashes on malformed
    input reports nothing at all, which is the state this repo's own commit
    4cfca5b is about. The base file is left byte-identical: the guard against
    its crash lives here, where it costs one isinstance.
    """
    notes, traces, hosts = [], [], []
    if not isinstance(doc, dict):
        return ([f"the census is a {type(doc).__name__}, not an object; "
                 f"no clause can be evaluated"], notes, traces, hosts)
    rows = doc.get("rows")
    if isinstance(rows, list) and any(not isinstance(r, dict) for r in rows):
        bad = [repr(r)[:60] for r in rows if not isinstance(r, dict)]
        return ([f"data has {len(bad)} row(s) that are not objects: "
                 f"{'; '.join(bad)}; no clause can be evaluated"], notes, traces, hosts)

    fails = list(BASE.check(doc))

    if not isinstance(rows, list):
        fails.append("data has no 'rows' list; the extended checks cannot run")
        return fails, notes, traces, hosts

    caps = captures()
    on_disk = capture_names_on_disk()

    fails.extend(inventory_faults(rows))
    for r in rows:
        f, n, t = quote_faults(r, caps, on_disk)
        fails.extend(f)
        notes.extend(n)
        traces.extend(t)
        fails.extend(tier_faults(r))
        fails.extend(provenance_faults(r, on_disk, notes))
        sf, h = source_faults(r)
        fails.extend(sf)
        if r.get("tier") in COUNTABLE:
            hosts.extend(h)
    return fails, notes, traces, hosts


def check(doc):
    """The failures only. Deliberately narrow: an importing caller must not
    have to tell a real failure apart from an honest limitation."""
    return scan(doc)[0]


# --- mutations -----------------------------------------------------------
# Every mutation is arranged so that the declared counts stay consistent and
# the row keeps its source, tier and quotes unless that is the defect, so the
# ONLY thing that can fire is the clause the mutation names. A mutation caught
# by a neighbouring clause proves nothing, so each is asserted against the
# clause's own distinctive substring AND against the set of failures that were
# not already present on the shipped file - otherwise a mutation "caught" by a
# pre-existing finding would look like a pass.

def _row(d, rid):
    return next(r for r in d["rows"] if r["id"] == rid)


def _recount(d):
    from collections import Counter
    c = Counter(r.get("tier") for r in d["rows"])
    d["counts"] = {t: c[t] for t in sorted(BASE.TIERS)}


def _m_fabricated_quote(d):
    _row(d, "oracle-a1-alwaysfree")["quote"] = (
        "Four thousand OCPU hours and 96 GB, unlimited, forever."
    )


def _m_spliced_quote(d):
    """Join bytes from two DIFFERENT captures with ' | '. The same-capture rule
    is the whole point: a quote stitched out of two pages quotes nothing."""
    _row(d, "github-codespaces")["quote"] = (
        "Account plan | 15 GB-month | 100,000/day | CPU time 10 ms"
    )


def _m_promote_t2_to_t1(d):
    r = _row(d, "render-free-web-service")
    r["tier"] = "T1"          # keepalive deliberately kept
    _recount(d)


def _m_quota_on_clean_row(d):
    _row(d, "supabase-free-project")["spec"] = (
        "Shared CPU, 500 MB RAM, 100 CU-hrs/month of compute"
    )


def _m_dead_with_keepalive(d):
    _row(d, "railway-free-vm")["keepalive"] = "an hourly ping to the box"


def _m_t1_expiry(d):
    _row(d, "northflank-sandbox")["idle_or_session_limit"] = (
        "none, but the account expires 12 months after signup"
    )


def _m_provenance_unknown_key(d):
    _row(d, "gcp-e2-micro")["verified_by"] = (
        "me, 2026-10-06 - page fetched HTTP 200, quote read from fetched bytes "
        "at verify/pages/gcp_free_v2.html"
    )


def _m_provenance_missing_capture(d):
    """A re-fetchable name whose bytes are simply not in the repo.

    The mutation adds a key to verify/fetch.py's URLS table that has no
    capture, rather than pointing at an existing key. That is because after the
    fetch.py fix there is no such key left to point at: every URL in the table
    either has a capture or is in KNOWN_UNREACHABLE, because a fetch that fails
    now DELETES its stale capture. So the state this clause exists to catch -
    "a row cites a capture that does not exist" - is only reachable by
    introducing a new citation, which is exactly what the mutation does.

    Aiming it at sdf_members05 instead made it test the host-dependence clause
    rather than this one, and aiming it at a key that HAS a capture made it
    invisible. A mutation caught by a neighbouring clause proves nothing, and a
    mutation that changes nothing proves less.
    """
    URLS["_mutation_absent_capture"] = "https://example.invalid/absent"
    _row(d, "supabase-free-project")["verified_by"] = (
        "me, 2026-10-06 - page fetched HTTP 200, quote read from fetched bytes "
        "at verify/pages/_mutation_absent_capture.html"
    )


def _m_provenance_names_nothing(d):
    _row(d, "koyeb-free-instance")["verified_by"] = (
        "me, 2026-10-06 - I fetched it and confirmed the scale-to-zero rule"
    )


def _m_source_placeholder(d):
    _row(d, "gcp-e2-micro")["source"] = "https://example.com/not-a-real-page"


def _m_source_not_http(d):
    _row(d, "supabase-free-project")["source"] = "ftp://supabase.com/pricing"


def _m_delete_dead_rows(d):
    d["rows"] = [r for r in d["rows"] if r.get("tier") != "DEAD"]
    _recount(d)


def _m_invent_row(d):
    clone = copy.deepcopy(_row(d, "gcp-e2-micro"))
    clone["id"] = "gcp-e2-micro-mirror"
    d["rows"].append(clone)
    _recount(d)


def _m_null_quote(d):
    """A DEAD row that says it read a capture but shows no quote for it. The
    base guard reads `quote` only on COUNTED rows, so this is silent today."""
    _row(d, "google-cloud-shell")["quote"] = None


# Module-level state a mutation is allowed to touch, snapshotted so --mutate can
# put it back. A mutation that changes shared state and is not undone makes every
# LATER mutation's verdict depend on it, which is how a suite passes for the
# wrong reason.
_MODULE_RESTORE = [
    ("URLS", dict(URLS)),
    ("UNREACHABLE", dict(UNREACHABLE)),
]

MUTATIONS = [
    ("clause 1: replace a verified quote with a fabricated sentence",
     _m_fabricated_quote, "quote is not traceable to any capture"),
    ("clause 1: splice two different captures into one ' | ' quote",
     _m_spliced_quote, "quote is not traceable to any capture"),
    ("clause 1: null the quote of a row that names its own capture",
     _m_null_quote, "carries no quote in quote, quote2, quote3"),
    ("clause 2: promote a T2 row to T1 and keep its keepalive",
     _m_promote_t2_to_t1, "tier T1 is always-on as-is but names a keepalive"),
    ("clause 2: give a counted row a quota unit and no hard_wall",
     _m_quota_on_clean_row, "names a quota unit"),
    ("clause 2: put a keepalive on a DEAD row",
     _m_dead_with_keepalive, "DEAD row carries a keepalive"),
    ("clause 2: put an expiry phrase in a T1 row's idle limit",
     _m_t1_expiry, "tier T1 says no expiry"),
    ("clause 3: name a capture that is not a key in verify/fetch.py",
     _m_provenance_unknown_key, "not a fetchable key"),
    ("clause 3: name a fetchable key whose capture is not on disk",
     _m_provenance_missing_capture, "NO capture on disk"),
    ("clause 3: claim first-hand verification naming no capture at all",
     _m_provenance_names_nothing, "names no capture in verify/pages/"),
    ("clause 4: point a counted row's source at example.com",
     _m_source_placeholder, "reserved placeholder host"),
    ("clause 4: give a counted row a non-http source",
     _m_source_not_http, "source is not an http(s) URL"),
    ("clause 5: delete every DEAD row, counts made consistent",
     _m_delete_dead_rows, "manifest row id is missing from the rows array"),
    ("clause 5: invent a row id that is not in the manifest",
     _m_invent_row, "NOT in the committed manifest"),
]


def _no_false_failures(doc):
    """Prove the rule the module's docstring promises: a row that says 'a
    research pass carried this' and ships no capture is REPORTED, never
    failed.

    Each such row is judged on the failures attributable to its own id, with
    the whole census still loaded. Checking a single-row document instead
    would fail the census-wide clauses - the row floor, the counts, and the
    40-id manifest - for rows that are perfectly correct, which is exactly
    the sort of false failure this function exists to detect and would have
    manufactured instead.
    """
    caps = captures()
    on_disk = capture_names_on_disk()
    carried = []
    for r in doc["rows"]:
        if not isinstance(r, dict):
            continue
        if BASE.provenance(r) != "carried":
            continue
        named = [n for n in capture_names_named(r) if n in on_disk]
        sourced = [n for n in source_captures(r) if n in on_disk]
        if named or sourced:
            continue  # it does have bytes; it is judged on them, not excused
        rid = r["id"]
        probe = copy.deepcopy(r)
        probe["quote"] = None
        for extra in ("quote2", "quote3"):
            probe.pop(extra, None)
        doc_without = copy.deepcopy(doc)
        doc_without["rows"] = [probe if x["id"] == rid else x for x in doc_without["rows"]]
        _f, notes, _t, _h = scan(doc_without)
        mine = [f for f in check(doc) if f.startswith(f"{rid}.")]
        mine += [f for f in check(doc) if f.startswith(f"{rid}:")]
        carried.append((rid, len(notes), mine))
    return carried


def main():
    with open(DATA, encoding="utf-8") as fh:
        doc = json.load(fh)

    if "--mutate" in sys.argv:
        base_fails = check(doc)
        rows = doc["rows"]
        counted = sum(1 for r in rows if r.get("tier") in COUNTABLE)
        print(f"baseline: {len(rows)} rows, {counted} counted, "
              f"{len(captures())} captures, {len(MANIFEST)} manifest ids, "
              f"{len(base_fails)} pre-existing failure(s)")
        print("a mutation is only CAUGHT if its clause's substring is among the "
              "failures the mutation ADDS\n")
        caught = wrong_clause = 0
        for name, mutate, expect in MUTATIONS:
            trial = copy.deepcopy(doc)
            mutate(trial)
            got = check(trial)
            added = [g for g in got if g not in base_fails]
            # Some mutations have to change module state to reach the state they
            # are about (the one above adds a key to verify/fetch.py's URLS
            # table). Undo whatever they touched, or the next mutation inherits
            # it and a suite that passes for the wrong reason still passes.
            for attr, restore in _MODULE_RESTORE:
                setattr(sys.modules[__name__], attr, restore)
            if not added:
                print(f"  MISSED        {name}")
                print("                 <-- nothing new fails; this mutation is invisible")
                continue
            caught += 1
            if any(expect in g for g in added):
                print(f"  CAUGHT        {name}")
            else:
                wrong_clause += 1
                print(f"  WRONG-REASON  {name}")
                print(f"                expected a NEW failure containing {expect!r}")
                for g in added:
                    print(f"                got: {g}")

        print()
        carried = _no_false_failures(doc)
        false_pos = 0
        for rid, notes, fails in carried:
            if fails:
                false_pos += 1
                print(f"  FALSE-FAILURE {rid}: an honestly-carried row with no "
                      f"capture must be reported, not failed")
                for f in fails:
                    print(f"                {f}")
            else:
                print(f"  NO-FALSE-FAIL {rid}: no capture, reported UNVERIFIABLE "
                      f"({notes} note(s)), zero failures")

        total = len(MUTATIONS)
        print(f"\n{caught}/{total} mutations caught, "
              f"{caught - wrong_clause} by the clause they name")
        print(f"{len(carried)} honestly-carried rows checked for false failures, "
              f"{false_pos} failed one")
        return 0 if (caught == total and wrong_clause == 0 and false_pos == 0) else 1

    fails, notes, traces, hosts = scan(doc)
    rows = doc["rows"]
    counted = sum(1 for r in rows if r.get("tier") in COUNTABLE)
    print(f"always-on free compute census - EXTENDED guard - {len(rows)} rows, "
          f"{counted} counted, {len(captures())} captures, "
          f"{len(URLS)} fetchable keys, {len(MANIFEST)} manifest ids")
    print(f"built on tools/check-always-on-free.py, which is run first and "
          f"cannot be weakened here ({sum(1 for f in fails if f in BASE.check(doc))} "
          f"of the failures below are its)")

    print(f"\nFAIL ({len(fails)})")
    for f in fails:
        print(" -", f)

    print(f"\nUNVERIFIABLE ({len(notes)}) - honestly-labelled rows with no capture "
          f"in verify/pages/ to check against. Counted and reported, exit 0.")
    for n in notes:
        print(" -", n)

    print(f"\nQUOTE TRACE ({len(traces)}) - each quote that IS in a capture, and "
          f"where. 'folded' = matched after ignoring whitespace only.")
    for t in traces:
        print(" -", t)

    print(f"\nSOURCE HOSTS ({len(hosts)}) - every counted row's citation host, for "
          f"a human to eyeball")
    for h in hosts:
        print(" -", h)

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())