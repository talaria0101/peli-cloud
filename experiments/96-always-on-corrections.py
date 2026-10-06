#!/usr/bin/env python3
"""Apply the 2026-10-06 always-on-free corrections to data/anonymous-vms.json.

Idempotent. Run from the repo root:

    python3 experiments/96-always-on-corrections.py
    python3 tools/check-anon-vms.py     # the census guard must still pass

Every change here is a correction to a row that the previous revision got
wrong, verified against a first-party page fetched on 2026-10-06 from a
residential host (not the sandbox, whose egress proxy refuses port 22).

The corrections, and what each one is:

  1. oracle-always-free   4 OCPU / 24 GB  ->  2 OCPU / 12 GB. Oracle's own
     docs page states the equivalent explicitly. The corpus card that seeded
     the old figure was wrong by 2x.
  2. github-codespaces    RESTORED. The previous revision demoted this row for
     a quote that "did not survive being fetched". It IS on the cited page,
     in a table. The demotion was the error.
  3. huggingface-spaces   free CPU Spaces now require PRO. The free tier that
     remains is Static (no runtime) plus 2 ZeroGPU Spaces.
  4. koyeb                RESTORED. A free Instance IS published and documented,
     with an explicit, uncustomisable scale-to-zero rule.
  5. blinkenshell         free tier does NOT allow listening ports, IRC bots or
     bouncers. A flattened scrape of the wiki table reads as if it does; the
     cells say otherwise.
  6. northflank           ADDED. Requires a payment method for all users; the
     pricing page's "Get started for free" is not the whole story.

Nothing here re-prices the catalogue. These rows are the free/anonymous census.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "anonymous-vms.json")

with open(DATA, encoding="utf-8") as fh:
    doc = json.load(fh)

rows = {r["id"]: r for r in doc["rows"]}
applied = []


def patch(rid, **fields):
    r = rows[rid]
    changed = {k: v for k, v in fields.items() if r.get(k) != v}
    if changed:
        r.update(fields)
        applied.append(f"{rid}: {', '.join(sorted(changed))}")


# --- 1. Oracle A1: the shape is half what this census said -------------
patch(
    "oracle-always-free",
    name="Oracle Cloud Always Free",
    resources=(
        "VM.Standard.A1.Flex Ampere ARM: 1,500 OCPU-hours and 9,000 GB-hours per "
        "month, which Oracle states is equivalent to 2 OCPUs and 12 GB of memory. "
        "Plus up to two VM.Standard.E2.1.Micro instances and 200 GB of block volume. "
        "Home region only."
    ),
    lifetime=(
        "Always Free, no time limit, while the tenancy qualifies; Oracle may "
        "reclaim an instance idle over a 7-day window"
    ),
    cost_usd="0 on the Always Free shapes",
    source=(
        "https://docs.oracle.com/en-us/iaas/Content/FreeTier/"
        "freetier_topic-Always_Free_Resources.htm"
    ),
    quote=(
        "All tenancies get the first 1,500 OCPU hours and 9,000 GB hours per month "
        "for free for VM instances using the VM.Standard.A1.Flex shape, which has an "
        "Arm processor. For Always Free tenancies, this is equivalent to 2 OCPUs and "
        "12 GB of memory."
    ),
    verification=(
        "MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 53,867 "
        "bytes) and the quoted sentence appears verbatim in the response body. This "
        "resolves the open question the 2026-10-02 revision recorded: the A1 "
        "allowance figures are NOT on oracle.com/cloud/free, they are on the "
        "Always Free documentation page, which is now the cited source."
    ),
    caveats=(
        "CORRECTED 2026-10-06 - the figure this row carried (4 OCPU / 24 GB) was "
        "WRONG BY 2x and came from the upstream corpus card, not from Oracle. "
        "Oracle's own sentence says 'equivalent to 2 OCPUs and 12 GB of memory', and "
        "the arithmetic agrees (1,500 OCPU-hours over a ~744-hour month is 2 OCPUs). "
        "Any catalogue figure derived from the 4/24 card is wrong and should be "
        "recomputed. Two further first-party facts now attached: a card is required "
        "at signup and is not charged on Always Free, and an idle instance may be "
        "reclaimed - Oracle deems a VM idle if, over a 7-day period, 95th-percentile "
        "CPU and network are both under 20% and memory is under 20% on A1 shapes. "
        "That is a utilisation threshold rather than a session cap, so sustained "
        "work defeats it."
    ),
)

# --- 2. Codespaces: the demotion was the error --------------------------
patch(
    "github-codespaces",
    resources="2-core default machine (8 GB, 32 GB storage); 2/4/8/16/32-core available",
    lifetime=(
        "120 core-hours per month on GitHub Free; a codespace is auto-stopped after "
        "its retention period of inactivity and resume is blocked once quota is spent "
        "without a payment method"
    ),
    cost_usd="0 for 120 core-hours/month, then blocked",
    quote=(
        "Account plan | Storage per month | Compute time per month | GitHub Free for "
        "personal accounts | 15 GB-month | 120 hrs"
    ),
    verification=(
        "MEASURED 2026-10-06: the cited page was fetched (HTTP 200, 196,324 bytes) "
        "and the quota table row quoted above is present in the response. The "
        "2026-10-02 revision recorded that the '120 core hours' figure 'did not "
        "survive being fetched'; it does, in a table on the exact page cited. The "
        "earlier extraction missed the table rather than the sentence being absent."
    ),
    caveats=(
        "PARTIALLY RESTORED 2026-10-06. The 120 core-hour figure is first-party "
        "again, so the row no longer reads cost unknown. It stays out of the free "
        "tables because 120 core-hours of 2-core compute is ~5 days of continuous "
        "uptime, which is a dev-environment quota rather than an always-on box. Note "
        "the asymmetry that ends it: with no payment method on file, exhausting the "
        "quota BLOCKS resume rather than billing, so there is no soft landing."
    ),
)
rows["github-codespaces"]["class"] = "changed"

# --- 3. Hugging Face: free CPU Spaces moved behind PRO -------------------
patch(
    "huggingface-spaces",
    name="Hugging Face Spaces",
    resources=(
        "no free CPU tier for new compute Spaces; a free account may host 2 ZeroGPU "
        "Spaces (Gradio SDK only) plus unlimited Static Spaces, which have no runtime"
    ),
    ssh_how=(
        "Dev Mode SSH is PRO/Team/Enterprise only; a free account reaches a Space "
        "through its public HTTPS URL and an outbound tunnel"
    ),
    lifetime=(
        "a compute Space sleeps after 48 h without a visitor and restarts on the next "
        "one; Dev Mode changes are discarded on sleep"
    ),
    cost_usd="$0 for Static and 2 ZeroGPU Spaces; PRO ($9/mo) to create a CPU or GPU Space",
    source="https://huggingface.co/docs/hub/en/spaces-overview",
    quote=(
        "Static Spaces are free for everyone. Gradio and Docker Spaces run on "
        "compute and require a paid plan to create: PRO for personal accounts, Team "
        "or Enterprise for organizations. Free personal accounts in good standing "
        "can still host up to 2 Gradio Spaces running on ZeroGPU."
    ),
    verification=(
        "MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 222,896 "
        "bytes) and the quoted sentence appears verbatim. The 48-hour sleep figure "
        "was read from spaces-gpus on the same date (HTTP 200, 221,818 bytes), which "
        "states a cpu-basic Space 'will go to sleep if inactive for more than a set "
        "time (currently, 48 hours)'. The change is traceable to a docs commit: "
        "huggingface/hub-docs@34ee0f00, 2026-07-21."
    ),
    caveats=(
        "DEMOTED 2026-10-06 - the free CPU Basic Space (2 vCPU / 16 GB) this row "
        "advertised can no longer be created on a free account. The hardware still "
        "appears in HF's pricing table at $0, which is what makes the stale claim "
        "survive: the price is real, the CREATION is not. A paid-plan gate at "
        "creation is the one wall no keepalive or relay can defeat. A free account "
        "keeps Static Spaces (no runtime, so no daemon) and 2 ZeroGPU Spaces."
    ),
)

# --- 4. Koyeb: the free Instance is real and documented ------------------
patch(
    "koyeb",
    resources=(
        "free Instance: 1 shared vCPU (0.1 vCPU), 512 MB RAM, 2 GB SSD, no "
        "persistent volumes; fra and was regions only"
    ),
    lifetime=(
        "scales to zero after 1 h without inbound traffic; the idle period cannot be "
        "changed on the free Instance"
    ),
    cost_usd="0 on the free Instance; $0/month tier, scales to zero when idle",
    source="https://www.koyeb.com/docs/run-and-scale/scale-to-zero",
    quote=(
        "The Koyeb Free Instance automatically scales down to zero when it doesn't "
        "receive any traffic for 1 hour. Scale-to-zero on this Instance cannot be "
        "disabled, and the idle period cannot be customized."
    ),
    verification=(
        "MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 296,380 "
        "bytes) and the quoted sentence appears verbatim, naming the free Instance "
        "directly."
    ),
    caveats=(
        "RESTORED 2026-10-06. The 2026-10-02 revision recorded this as 'the free "
        "plan is not in the published tiers', checking the pricing page. The free "
        "Instance is documented on Koyeb's scale-to-zero docs page with its idle rule "
        "stated explicitly. It stays out of the free tables for the SSH question, "
        "not the free question: Koyeb publishes no inbound SSH, the idle period "
        "cannot be raised on the free tier, and there are no persistent volumes."
    ),
)

# --- 5. Blinkenshell: free tier excludes the listening features ----------
patch(
    "blinkenshell",
    resources=(
        "free: 100 MB disk, 128 MB memory limit, screen/tmux detach, max 2 background "
        "processes; listening TCP/UDP ports, IRC bots and bouncers are Supporter-only"
    ),
    verification=(
        "MEASURED 2026-10-06: the wiki page was fetched (HTTP 200) and its "
        "feature-comparison table parsed CELL BY CELL rather than flattened to text. "
        "The Free column is EMPTY for 'Bouncer (BNC, znc, weechat-relay)', 'IRC bots' "
        "and 'Listen TCP/UDP port (custom server)'; all three are Supporter-only. "
        "The operator's own rules page confirms independently: 'No IRC bots are "
        "allowed on free accounts' and 'You are not allowed to run any "
        "server/daemon on free accounts'. Re-dialed from a residential host on the "
        "same date: ports 80 and 443 answer (HTTPS 200, 55,375 bytes) while 22, 2222 "
        "and 6697 all time out."
    ),
    caveats=(
        "CORRECTED 2026-10-06. A flattened text scrape of the wiki table makes the "
        "free tier look as though it includes IRC bots and listening TCP ports. The "
        "cells do not: those rows have no tick in the Free column. So a free "
        "Blinkenshell account is a screen/tmux bot host and NOT an endpoint host - "
        "which matters for anyone planning to run a daemon or tunnel there. On "
        "reachability, the earlier reading 'the host is refusing or filtering this "
        "network' is now measured rather than inferred: from a different network "
        "than the original sweep, the web ports answer and every non-web port times "
        "out, so the host is alive and filtering by protocol. The 2026-10-02 note "
        "that port 2222 must be dialled specifically stands and is confirmed by the "
        "vendor's FAQ."
    ),
)

# --- 6. Northflank: correct the EXISTING row's card claim ---------------
# The census already carries a `northflank-sandbox` row classed free-account
# with card_required=false. Northflank's own billing docs require a payment
# method for every user regardless of plan, so the existing row is corrected in
# place. A second row for the same provider would be padding.
patch(
    "northflank-sandbox",
    name="Northflank Sandbox tier",
    card_required=True,
    resources=(
        "Developer Sandbox: 2 always-on services, 2 cron jobs, 1 addon (billing docs) "
        "/ 2 services, 1 database, 2 cron jobs (pricing page); smallest covered plan "
        "is 0.1 shared vCPU / 256 MB"
    ),
    lifetime=(
        "no idle sleep; pausing is manual and deletes ephemeral data while volumes "
        "survive. No published expiry"
    ),
    cost_usd=(
        "$0/mo Sandbox tier; a payment method is required before any resource can be "
        "created"
    ),
    source="https://northflank.com/docs/v1/application/billing/pricing-on-northflank",
    quote=(
        "all users must add a payment method to start creating resources on "
        "Northflank, regardless of plan selection. This is to verify user identity, "
        "and prevent malicious usage of the platform."
    ),
    verification=(
        "MEASURED 2026-10-06: the billing docs page was fetched (HTTP 200, 346,968 "
        "bytes) and the quoted sentence appears verbatim. The pricing page was "
        "fetched separately (HTTP 200, 193,710 bytes) and states 'Always-on-compute "
        "- no sleeping :)' alongside 'Get started for free', which is why the card "
        "requirement is recorded as measured rather than read off the marketing."
    ),
    caveats=(
        "CARD CORRECTION 2026-10-06: this row previously read card_required=false on "
        "the strength of the pricing page's 'Get started for free'. Northflank's own "
        "billing docs require a payment method for every user regardless of plan, to "
        "verify identity and prevent abuse, so the class moves free-account -> "
        "free-tier-card. It is kept rather than dropped because it is the cleanest "
        "no-sleep free container found: no idle timeout, no session cap, no expiry. "
        "No persistent volumes on free, no inbound SSH, and the docs say it should not "
        "be used for production. The two pages still disagree on the free-tier shape "
        "(pricing: 2 services, 1 database, 2 cron jobs; docs: 2 services, 2 jobs, 1 "
        "addon), which is unresolved."
    ),
)
rows["northflank-sandbox"]["class"] = "free-tier-card"

doc["generated"] = "2026-10-06"
doc["corrections_applied"] = [
    "oracle-always-free: 4 OCPU / 24 GB -> 2 OCPU / 12 GB, per Oracle's Always Free "
    "documentation page (the corpus card that seeded the old figure was wrong by 2x)",
    "github-codespaces: RESTORED. The '120 core hours' figure IS on the cited page; "
    "the 2026-10-02 demotion was the error, not the quote",
    "huggingface-spaces: DEMOTED. Free CPU Spaces require PRO as of "
    "huggingface/hub-docs@34ee0f00 (2026-07-21)",
    "koyeb: RESTORED. The free Instance is documented, with an explicit "
    "scale-to-zero rule that cannot be disabled",
    "blinkenshell: the free tier does NOT include listening ports, IRC bots or "
    "bouncers; a flattened scrape of the wiki table reads as if it does",
    "northflank-sandbox: card_required false -> true and free-account -> free-tier-card; "
    "the vendor requires a payment method for all users regardless of plan",
]

with open(DATA, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print(f"wrote {os.path.relpath(DATA, ROOT)}")
for line in applied:
    print(f"  {line}")
print(f"{len(applied)} changes applied")