# Deep reviews R21-R25: the anonymous-VM census and the relay SSH path

Scope, 2026-10-02, against the branch that added `docs/ANONYMOUS-VMS.md`,
`data/anonymous-vms.json`, `tools/ssh-relay-check.sh` and
`research/verification/ssh-relay-2026-10-02.md`.

Each review names what it attacked, what it found, and what changed. Where
nothing changed, that is stated. Three of the five **removed rows**, which is
the opposite of what a review pass that only adds looks like.

The headline before this pass: 26 rows, 17 free-or-anonymous machines that
answer SSH, 7 dialled and banner-verified, 1 genuinely anonymous. After it:
**26 rows, 15 that answer SSH, 6 banner-verified, 1 anonymous, 24 of 24 quotes
verified against the page each one cites.**

---

## R21 — the headline number was the weakest claim on the page

**Attacked:** the sentence "17 rows below are a free or anonymous machine you
can reach over SSH."

**Finding:** the row count and the reachability count were different numbers and
the page used one where the reader would assume the other. Of the 17:

| | count |
|---|---|
| dialled from this host, SSH banner read | 7 |
| the provider documents it, no public endpoint to dial | 8 |
| the provider claims it and **this host could not reach it** | 2 |
| **reachable AND logged in to, from this host** | **0** |

So the sentence claimed 17 reachable machines when the strongest evidence in
the file supported 7, and 2 of the 17 were hosts that answered nothing at all.
The 2 were named nowhere in the prose; a reader had to open the JSON to learn
that `Blinkenshell` and `alwaysdata` were unreachable from here.

**What changed:** the count sentence is now "a free or anonymous machine that
some provider says answers SSH", immediately followed by the four-way table
above it, with the zero stated rather than left to be inferred. The two
unreachable hosts are named in the reachability section, as a fact about this
host and this network rather than a verdict on the services. Every number is
still computed by the renderer from the JSON.

## R22 — a free row was resting on nothing but a live SSH banner

**Attacked:** every row carrying `class: free-account` or `free-tier-card`,
specifically whether the word "free" was supported by anything.

**Finding:** `tilde.zone` was classed `free-account`, `cost_usd: 0`, with an
**empty quote**, and the only evidence behind it was that the relay dialled
`tilde.zone:22` and read `SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4`. Fetched
first-party, `https://tilde.zone/` is a **Mastodon instance** requiring
JavaScript. It mentions no shell, no signup, no free account, and none of its
outbound links identify a shell operator. A host answering SSH is evidence of a
**host**, not of a **free shell**.

Worse, the guard accepted it: `tools/check-anon-vms.py` required a quote or a
measurement note, and the row carried a measurement note ("reachability
measured"), which satisfied the clause. The guard was checking the wrong thing.

**What changed:** three things.

1. The row is demoted to `changed`, with `cost_usd: "unknown"` and an explicit
   statement of what would recover it. It is kept rather than deleted because
   the measurement is real and deleting it would lose the evidence.
2. **A new guard clause:** a row in a free class may not rest on a banner. It
   must carry a first-party quote, i.e. words its provider wrote. Reintroducing
   R22's exact mistake now fails with `tilde-zone: free class with no
   first-party quote. A banner proves a host, not a free shell`.
3. That clause was checked in both directions: the mistake fails, and adding a
   quote lets the row back in, so the clause is a rule and not a blanket
   refusal.

## R23 — six quotes did not survive being fetched

**Attacked:** every `quote` in the census, checked by fetching each row's
`source` and searching the rendered page text. This check did not exist, which
is how two bad citations got in.

**Finding:** six rows, with two distinct causes.

*Wrong page cited — the quote is real, the citation does not carry it:*

| row | defect |
|---|---|
| `blinkenshell` | verbatim on `/wiki/FAQ`, absent from the cited root page. A reader following the citation would not find the sentence. |
| `killercoda` | the quota text is on `/pricing`, not the root page at all. |
| `browser-only-labs` | `source` held **two URLs in one field**, so no checker could fetch it. |

*Quote not on any page fetched:*

| row | defect |
|---|---|
| `github-codespaces` | "120 core hours or 60 hours" appears on none of the four GitHub pages fetched to chase it. |
| `oracle-always-free` | see R24; this one is bigger than a citation slip. |

*Quotes that were near-misses rather than absent:* `tilde.guru` used an em dash
where the page has a hyphen; `northflank` used `2x` where the page has `2×`;
`koyeb` used `Pro $29` where the page renders `pro $ 29`; `alwaysdata` used
`Free ... 0 €/month ...` where the live page now says "free for personal needs,
ad-free offer available for life".

**What changed:** the citations were repointed to the pages that carry the
words, and every quote was rewritten from the fetched text rather than from
memory: SDF, tilde.guru, alwaysdata, northflank, koyeb and killercoda all have
new quotes that verify verbatim. `github-codespaces` is demoted to `changed`
with `cost_usd: unknown` — the free-tier **size** is no longer supportable, and
the row leaves the free tables rather than publishing an unverified number.
The SSH mechanism, which is GitHub's own documented `gh codespace ssh`, is
untouched: this is not a claim that the free tier is gone.

**And the checker that found them is itself the second half of this review.**
`tools/check-quotes.py` took three versions before it was correct, and each
failure was silent and in a different direction — see the file's own header. It
now has 11 known-answer cases in `tests/selftest-check-quotes.py`.

## R24 — Oracle: the 403 excuse stopped being true, and the quote was never on the page

**Attacked:** `oracle-always-free`, and the justification its row carried for
being an unverified figure.

**Finding:** the row said the figure was "carried from research/verification/...
the oracle.com domain returns 403 to this host". Fetched 2026-10-02,
`https://www.oracle.com/cloud/free/` **returns HTTP 200 with 79,448 bytes.** The
403 no longer happens, so the carried-figure excuse no longer applies — and
having fetched it, the strings `1,500`, `OCPU` and `9,000` **do not occur
anywhere in the response.** The page is client-rendered; the only
customer-visible text is its meta description, which is now the row's quote.

So the largest single understatement in the main catalogue — Oracle's Always
Free A1 allowance, which prices the comparison shape at $0 rather than $7.41 —
rests on a figure that is not on the page this row cites.

**What changed:** the row carries the page's own sentence, its `resources`
field says the A1 allowance is **not stated on this page**, its verification
note records the measured 200 and the measured absence of the OCPU strings, and
its caveats say plainly that the allowance remains carried from the corpus card
and must not be read as confirmed here. The row is demoted to `changed`.

This is a finding about the main catalogue, not a fix to it: `docs/FINDINGS.md`
and `docs/CATALOGUE.md` still carry the A1 figures, and this review did not
re-derive them. They stay as they were, sourced as they were sourced.

## R25 — "the forward path cannot do SSH" was too narrow, and the missing control found it

**Attacked:** the note's own conclusion about the relay's forward path, which
read: "The relay's FORWARD path is not usable for SSH from this host, and no
argument I found fixes it."

**Finding:** true, and too narrow to be worth anything. The control that was
missing is a **protocol with nothing to do with SSH**: a plain HTTP/1.1 `GET`
through the same forward path.

| probe | result |
|---|---|
| `example.com:80`, HTTP GET | **0 bytes back**, write fails with a broken pipe |
| `neverssl.com:80`, HTTP GET | **0 bytes back**, write fails with a broken pipe |
| `example.com:443`, HTTPS GET | **0 bytes back** |
| `sdf.org:22`, SSH | banner, then stall at `KEX_ECDH_REPLY` |
| `git.sr.ht:22`, SSH | banner, then the same stall |
| `railway.new:22`, SSH | banner, then a broken pipe on the client's first burst |

No SSH anywhere in the failing probes. So the real statement is: **this host
opens a forward session, reads the target's first bytes, and cannot get its own
bytes delivered past that point, for any protocol.** Railway resetting an early
burst and GitHub not doing so is two server behaviours behind one symptom, and
"SSH does not complete" was the wrong frame for both.

Also tested and changed nothing: `-o KexAlgorithms=curve25519-sha256`,
`diffie-hellman-group14-sha256`, `-o PubkeyAcceptedAlgorithms=ssh-ed25519`,
`-o Ciphers=aes128-ctr`; `?precheck=0`; `?family=4`; `?dial=lazy` (returns
nothing at all).

**What changed:** the note and the rendered page now say the cause is not SSH,
and both say **which end is at fault is not established** — reads of
`src/connect.c` do not discriminate, because its forward branch writes bare
binary frames, which is also correct for a reverse session. The note names what
would settle it: the same HTTP probe from a host whose client is not dropssh
v0.2.3. The reverse path, which is the path a sealed sandbox uses for its own
server, is unaffected and still passes.

## What this pass did not establish

- **Whether the forward path's fault is dropssh's client or the relay.** R25
  gives the discriminating experiment; it needs a second host.
- **Whether the A1 allowance in the main catalogue is right.** R24 only
  established that the census's citation for it does not carry it. The
  catalogue was not re-derived.
- **That the demoted rows are wrong.** `github-codespaces`, `oracle-always-free`
  and `tilde.zone` lost their place in the free tables because this host could
  not confirm the specific claim, which is different from the claim being false.
  `oracle.com` in particular served a real page today.
- **Whether the 15 remaining SSH rows are reachable from anywhere.** 6 were
  dialled and read a banner; 9 rest on their provider's documentation. Zero were
  logged in to from this host.
- **Whether the quote checker is a substitute for reading.** It proves a string
  is on a page today. It cannot tell you the string means what the row says it
  means, and it says so by checking words rather than claims.

## The gate after this pass

```sh
python3 tools/check-anon-vms.py                 # 26 rows, 15 SSH, 6 banner, 1 anonymous
python3 tools/check-quotes.py                   # 24 verified, 0 failed
python3 tests/selftest-check-quotes.py          # 11/11
python3 tests/selftest-check-quotes.py --mutate # naive splitter caught
python3 tools/render-anon-vms.py                # rewrites docs/ANONYMOUS-VMS.md
sh tests/ssh-relay-regressions.sh               # 11 clauses
```

Seven gates, all exit 0. The quote checker has been seen failing: a forged
quote on `railway-free-vm` (20% of the words present) and a repointed
`blinkenshell` source (0%), each restored afterwards.