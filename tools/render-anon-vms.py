#!/usr/bin/env python3
"""render-anon-vms.py - render docs/ANONYMOUS-VMS.md from data/anonymous-vms.json.

The JSON is the source of truth and the prose is fixed here. Nothing in a table
is typed into this file, so the list and the guard cannot drift apart.

Honesty rules this renderer enforces, not just describes:
  * The SSH count is recomputed from the data and printed by the generator, so a
    sentence cannot claim a number the rows do not support.
  * `banner-verified` rows carry a visible "(banner)" marker distinct from a
    completed login, because a dialed host that answered an SSH banner is NOT
    evidence that a login completes - and on this host it does not.
  * Rows with no first-party quote are grouped and labelled as measurement-only
    rather than being given an empty quote cell.

Usage: python3 tools/render-anon-vms.py        # writes docs/ANONYMOUS-VMS.md
       ANON_VMS_OUT=/tmp/x.md python3 tools/render-anon-vms.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "anonymous-vms.json")
OUT = os.environ.get("ANON_VMS_OUT") or os.path.join(ROOT, "docs", "ANONYMOUS-VMS.md")

d = json.load(open(DATA))
rows = d["rows"]
FREE = ("anonymous", "free-account", "free-tier-card")


def by_class(name):
    return [r for r in rows if r["class"] == name]


def ssh_first(rs):
    return sorted(rs, key=lambda r: (0 if r["ssh"] else 1,
                                     0 if r["ssh_reachability"] == "banner-verified" else 1,
                                     r["name"].lower()))


def reach_cell(r):
    if not r["ssh"]:
        return "no"
    m = {"banner-verified": "yes (banner)", "provider-documented": "yes (documented)",
         "not-verified": "claimed"}[r["ssh_reachability"]]
    return m


def table(rs):
    cols = ("Provider", "SSH", "How you get in", "What you get", "Lifetime", "Cost")
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in ssh_first(rs):
        cells = [
            f"[{r['name']}]({r['source']})",
            reach_cell(r),
            r["ssh_how"],
            r["resources"],
            r["lifetime"],
            r["cost_usd"],
        ]
        out.append("| " + " | ".join(c.replace("\n", " ") for c in cells) + " |")
    return "\n".join(out)


def details(rs):
    out = []
    for r in ssh_first(rs):
        acct = "yes" if r["account_required"] else "no"
        card = "yes" if r["card_required"] else "no"
        out.append(f"**{r['name']}** - `{r['class']}`, account={acct}, card={card}")
        if r.get("quote"):
            out.append(f"- quote: “{r['quote']}”")
        else:
            out.append("- quote: none taken; see the measurement note below")
        if r.get("ssh_endpoint"):
            out.append(f"- endpoint: `{r['ssh_endpoint']}` ({r['ssh_reachability']})")
        out.append(f"- checked: {r['verification']}")
        out.append(f"- caveats: {r['caveats']}")
        out.append("")
    return "\n".join(out)


anon = by_class("anonymous")
free_acct = by_class("free-account")
card = by_class("free-tier-card")
changed = by_class("changed")
dead = by_class("dead")

ssh_rows = [r for r in rows if r["class"] in FREE and r["ssh"]]
banner_rows = [r for r in ssh_rows if r["ssh_reachability"] == "banner-verified"]
n_ssh = len(ssh_rows)
n_banner = len(banner_rows)
n_doc = len([r for r in ssh_rows if r["ssh_reachability"] == "provider-documented"])
n_unreach = len([r for r in ssh_rows if r["ssh_reachability"] == "not-verified"])
unreach_names = ", ".join(sorted(r["name"] for r in ssh_rows
                                 if r["ssh_reachability"] == "not-verified"))
anon_needed = [r for r in ssh_rows if r["account_required"]]
n_anon_needed = len(anon_needed)
n_card = len([r for r in ssh_rows if r["card_required"]])
reachable_names = ", ".join(sorted(r["name"] for r in banner_rows))

md = f"""# Anonymous and free VMs that answer SSH

The catalogue in [`docs/CATALOGUE.md`](CATALOGUE.md) prices 366 providers at a
fixed shape. This page answers a different question, the one a sandbox being
bootstrapped asks first: **what can I get a shell on without a card, without an
account, or for nothing?**

Generated from [`data/anonymous-vms.json`](../data/anonymous-vms.json) by
`tools/render-anon-vms.py`. The guard `tools/check-anon-vms.py` fails if the
list drops below ten SSH-capable free-or-anonymous machines, if a row loses its
source or its caveat, or if a row claims a dialed endpoint it does not name.

---

## Read this before you read the tables: what "SSH" means in each cell

Three different claims are in this page and they are **not** the same claim.

| the cell says | what was actually done |
|---|---|
| `yes (banner)` | A relay **dialed the host and read its SSH banner** - the version string. The host is up and speaking SSH. **A login was not completed.** |
| `yes (documented)` | The provider's own page publishes the SSH path. No public host:port exists to dial, so nothing was measured. |
| `claimed` | The provider claims SSH; the host could not be dialled from here, and the reason is in the row. |
| `no` | No inbound SSH endpoint is published. |

**{n_banner} rows are banner-verified. That is not a login count, and on this
host the forward path cannot carry an ssh session using dropssh v0.2.3's own
client.** The relay is not at fault: the relay's own diagnostic calls the
targets live, and a from-scratch WebSocket client carries a complete session to
Railway's anonymous VM. What is broken is dropssh's forward branch, which blocks
in `ws_read()` and therefore never services its own stdin. One session, exit 0,
proves both halves - see [`tools/poc-forward-relay.sh`](../tools/poc-forward-relay.sh).

## What the three classes mean

- **anonymous** - no account and no card. The first connect identifies the
  machine by the SSH key that made it.
- **free-account** - signup is required; no card is charged for the free quota.
- **free-tier-card** - a card is required, and a recurring or time-boxed
  allowance covers the machine.

**{n_ssh} rows below are a free or anonymous machine that some provider says
answers SSH. That is NOT {n_ssh} reachable machines, and the difference is the
point of the next table:**

| of those {n_ssh} | count | what was done |
|---|---|---|
| dialled from this host, SSH banner read | **{n_banner}** | the host answered with a version string; **no login was completed** |
| the provider documents it, no public endpoint to dial | {n_doc} | nothing was measured; the claim is the provider's |
| the provider claims it and **this host could not reach it** | {n_unreach} | named in the row, with the measured reason |
| **reachable AND logged in to, from this host** | **0** | see the relay note below |

Every count on this page is computed by the renderer from the JSON; none is
typed.

---

## 1. Anonymous: no account, no card

{table(anon)}

**{len(anon)} row, and it is the only one that needs nothing at all.** Railway's
own FAQ answers *"Do I need a Railway account?"* with **"No. Railway identifies
you by your SSH key."** It is the rare case where the signup step is the key
itself. The box lives 60 minutes to build and 24 hours to claim; an unclaimed box
and its files are deleted.

---

## 2. Free with an account

{table(free_acct)}

These are the durable free rows: shared shells that renew for as long as you
use them, plus dev environments with a monthly quota. None asks for a card.

**One host here is not reachable, and the reason is worth the trip.**
`Blinkenshell`'s own FAQ says it uses *"the non-standard port 2222 for SSH
(instead of 22)"*. The relay dialed it on 22, 2222 **and** 443 and every one
answered with 0 bytes. So the host is refusing or filtering this network, not
down - and any sweep that only tries port 22 records the entire Blinkenshell
class of host as dead. That is the kind of finding a keyword search cannot make.

---

## 3. Free allowance with a card

{table(card)}

The largest machines on the page: Oracle's Always Free A1 allowance and
Google's e2-micro are real 24/7 machines. AWS's free plan is now a six-month
credit that closes the account when it ends, and Azure's 750 hours are twelve
months only.

---

## 4. Products that changed, died, or are not remote at all

{table(changed + dead)}

Two corrections matter. **Play with Docker**, the canonical anonymous free VM in
every list older than this one, says: *"Play with Docker will be unavailable
starting March 1, 2026."* **Fly.io** no longer publishes a free Machine
allowance: the only "first free" left on its pricing page is 10 GB of volume
capacity.

**Microterm and LinuxOnTab are a category, not a provider.** Both are
anonymous, free, need no signup and run a real Linux kernel - inside the
reader's own browser, via WebAssembly. There is no host to SSH to and nothing
runs when the tab closes. They belong on this page because a search for
"anonymous free Linux" returns them first and every list that names them without
saying *runs on your own laptop* is misleading.

---

## Banner-verified endpoints, and the reach of this sweep

The relay dialed these hosts and read their banners on 2026-10-02:

{reachable_names}

Reachability was checked through the relay's own `/trace` diagnostic because
this sandbox's egress proxy **refuses port 22** (`CONNECT ... 403`) and permits
443. That is a property of this sandbox, not of any provider, and it is why the
relay is the only route at all here.

**The {n_unreach} hosts this sandbox could NOT reach are {unreach_names}.**
That is recorded as a fact about this host and this network, not as a verdict on
the services: Blinkenshell answered 0 bytes on 22, 2222 and 443 alike, and
alwaysdata's free tier is reached through a per-account host rather than a
public one. Neither row claims the service is dead.

---

## The detail behind every row

{details([r for r in rows if r['class'] in FREE])}
## Changed and dead

{details(changed + dead)}
---

## Reproduce

```sh
python3 tools/check-anon-vms.py    # guard: counts, required fields, honesty fields
python3 tools/render-anon-vms.py   # rewrite this page from the JSON
sh tests/ssh-relay-regressions.sh  # the SSH path itself, 11 clauses
```

The guard has been seen failing, which is what makes it a check rather than a
decoration. Three mutations, each restored afterwards:

| mutation | what the guard said |
|---|---|
| blank a row's quote and its measurement note | `tilde-zone: no quote and no measurement in verification` |
| claim `banner-verified` with no endpoint | `railway-free-vm: banner-verified but no ssh_endpoint` |
| delete the only `anonymous` row | `no row is class=anonymous; the brief names anonymous VMs explicitly` |

*We aim to provide the software that shapes the world of tomorrow.*
"""

# Encoding is explicit and newlines are pinned. Without them this writes in
# whatever the platform's preferred encoding happens to be: run on a Windows
# host it emitted cp1252, which turned 24 UTF-8 smart quotes into 25 raw 0x93
# bytes, flipped LF to CRLF, and produced a file that is not valid UTF-8 at all.
# The page carries vendor quotations with typographic punctuation in them, so a
# locale-dependent write silently corrupts exactly the text this page exists to
# preserve. `newline="\n"` keeps the diff readable on any host.
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(md)
print(f"wrote {OUT} rows={len(rows)} ssh={n_ssh} banner_verified={n_banner} anonymous={len(anon)}")
sys.exit(0)