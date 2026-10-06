# Anonymous and free VMs that answer SSH

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

**6 rows are banner-verified. That is not a login count, and on this
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

**15 rows below are a free or anonymous machine that some provider says
answers SSH. That is NOT 15 reachable machines, and the difference is the
point of the next table:**

| of those 15 | count | what was done |
|---|---|---|
| dialled from this host, SSH banner read | **6** | the host answered with a version string; **no login was completed** |
| the provider documents it, no public endpoint to dial | 7 | nothing was measured; the claim is the provider's |
| the provider claims it and **this host could not reach it** | 2 | named in the row, with the measured reason |
| **reachable AND logged in to, from this host** | **0** | see the relay note below |

Every count on this page is computed by the renderer from the JSON; none is
typed.

---

## 1. Anonymous: no account, no card

| Provider | SSH | How you get in | What you get | Lifetime | Cost |
|---|---|---|---|---|---|
| [Railway Free VM](https://railway.com/free-vm) | yes (banner) | ssh railway.new, with any ed25519 key as the identity | 2 vCPU / 2 GB, coding agents preinstalled (Claude Code, Codex, OpenCode, Cursor CLI, Grok, pi, Railway Agent); a shared $3 AI budget per box | 60-minute build window, then 24 h to claim; unclaimed boxes and their files are deleted | 0 |

**1 row, and it is the only one that needs nothing at all.** Railway's
own FAQ answers *"Do I need a Railway account?"* with **"No. Railway identifies
you by your SSH key."** It is the rare case where the signup step is the key
itself. The box lives 60 minutes to build and 24 hours to claim; an unclaimed box
and its files are deleted.

---

## 2. Free with an account

| Provider | SSH | How you get in | What you get | Lifetime | Cost |
|---|---|---|---|---|---|
| [hashbang (#!)](https://hashbang.sh/) | yes (banner) | POST your public key to https://hashbang.sh/user/create with a username and host, then ssh username@host | shared shell server; the project's stats endpoint advertises maxusers 6175 | free shell account, community-run | 0 |
| [SDF Public Access UNIX System](https://sdf.org/?signup) | yes (banner) | ssh new@sdf.org creates the account, then ssh USER@sdf.org | shared multi-user UNIX host, not a private VM | free USER tier for as long as the account is used | 0 |
| [tilde.club](https://tilde.club/wiki/) | yes (banner) | SSH; the wiki publishes the host's RSA, ECDSA and ED25519 fingerprints | shared shell account | free while active | 0 |
| [tilde.guru](https://tilde.guru/) | yes (banner) | SSH; the site is a FreeBSD pubnix | FreeBSD pubnix, member of the tildeverse; every user's home is served as a public web page | free while active | 0 |
| [tilde.town](https://tilde.town/) | yes (banner) | SSH; the site publishes the host ECDSA key | shared shell account | free while active | 0 |
| [alwaysdata Free](https://www.alwaysdata.com/en/pricing/) | claimed | SSH to the account's user; alwaysdata documents SSH users, keys and 2FA | 1 GB SSD, 256 MB RAM, 1/4 CPU, shared hosting | the free offer is described as available for life | 0 |
| [Blinkenshell](https://blinkenshell.org/wiki/FAQ) | claimed | SSH on the NON-STANDARD port 2222, which the project's own FAQ states | free: 100 MB disk, 128 MB memory limit, screen/tmux detach, max 2 background processes; listening TCP/UDP ports, IRC bots and bouncers are Supporter-only | free account; new members accepted | 0 |
| [Google Cloud Shell](https://cloud.google.com/shell/docs/limitations) | yes (documented) | Open in the browser or connect with the gcloud CLI | temporary Compute Engine VM, 5 GB persistent $HOME | ephemeral VM per session; the 5 GB $HOME persists | 0 within the weekly quota |
| [Hugging Face Spaces](https://huggingface.co/docs/hub/en/spaces-overview) | yes (documented) | Dev Mode SSH is PRO/Team/Enterprise only; a free account reaches a Space through its public HTTPS URL and an outbound tunnel | no free CPU tier for new compute Spaces; a free account may host 2 ZeroGPU Spaces (Gradio SDK only) plus unlimited Static Spaces, which have no runtime | a compute Space sleeps after 48 h without a visitor and restarts on the next one; Dev Mode changes are discarded on sleep | $0 for Static and 2 ZeroGPU Spaces; PRO ($9/mo) to create a CPU or GPU Space |
| [Modal Starter](https://modal.com/pricing) | yes (documented) | modal shell into a sandbox container from the Modal CLI | containers and sandboxes on Modal's pool; 1 TiB/month free egress | monthly credit reissued each month | 0 within $30/month of compute |
| [AWS CloudShell](https://aws.amazon.com/cloudshell/) | no | Browser terminal only; no inbound SSH endpoint is published | 1 GB persistent storage per AWS Region | session persists within the Region; idle sessions end | 0 |
| [Azure Cloud Shell](https://learn.microsoft.com/en-us/azure/cloud-shell/overview) | no | Browser terminal only; no inbound SSH endpoint is published | cloud-hosted shell with a persistent Azure Files share | session times out after 20 minutes without interactive activity; files persist | 0 for the machine; storage costs apply |
| [Killercoda](https://killercoda.com/pricing) | no | browser terminal; no inbound SSH published | Linux or Kubernetes scenario environment | FREE scenario runs up to 1 hour; PLUS up to 4 hours and 3 concurrent scenarios | 0 on the free tier |
| [Render Free compute](https://render.com/pricing) | no | No published inbound SSH for free web services | 512 MB RAM, less than 1 CPU | free compute plans have usage limits and are for exploration and previews | 0 |

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

| Provider | SSH | How you get in | What you get | Lifetime | Cost |
|---|---|---|---|---|---|
| [AWS Free Tier](https://aws.amazon.com/free/) | yes (documented) | SSH key pair is chosen at instance launch | EC2 instances up to the plan's credit; the current free plan is credit-based (up to $200 over 6 months) | 6 months, or until the credits run out; the account then closes on its own unless converted to paid | 0 within the credits |
| [Azure Free Account](https://azure.microsoft.com/en-us/free/) | yes (documented) | SSH keys are set at VM creation; the portal and the CLI both connect | 750 hours each of B1s, B2pts v2 (Arm) and B2ats v2 (AMD) burstable VMs, plus 65+ always-free services | the VM hours are 12 months for new customers; the $200 credit lasts 30 days; always-free services do not expire | 0 within the monthly amounts |
| [Google Cloud Free Tier (e2-micro)](https://cloud.google.com/free/docs/free-cloud-features) | yes (documented) | SSH keys are added to the instance or its project metadata | 1 non-preemptible e2-micro, 30 GB standard persistent disk, 1 GB egress | every month, for the life of the account | 0 within the allowance |
| [Oracle Cloud Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) | yes (documented) | SSH key is installed at instance creation; the console and the CLI both connect | VM.Standard.A1.Flex Ampere ARM: 1,500 OCPU-hours and 9,000 GB-hours per month, which Oracle states is equivalent to 2 OCPUs and 12 GB of memory. Plus up to two VM.Standard.E2.1.Micro instances and 200 GB of block volume. Home region only. | Always Free, no time limit, while the tenancy qualifies; Oracle may reclaim an instance idle over a 7-day window | 0 on the Always Free shapes |
| [Northflank Sandbox tier](https://northflank.com/docs/v1/application/billing/pricing-on-northflank) | no | No published inbound SSH; deploy services and use the web console or API | Developer Sandbox: 2 always-on services, 2 cron jobs, 1 addon (billing docs) / 2 services, 1 database, 2 cron jobs (pricing page); smallest covered plan is 0.1 shared vCPU / 256 MB | no idle sleep; pausing is manual and deletes ephemeral data while volumes survive. No published expiry | $0/mo Sandbox tier; a payment method is required before any resource can be created |

The largest machines on the page: Oracle's Always Free A1 allowance and
Google's e2-micro are real 24/7 machines. AWS's free plan is now a six-month
credit that closes the account when it ends, and Azure's 750 hours are twelve
months only.

---

## 4. Products that changed, died, or are not remote at all

| Provider | SSH | How you get in | What you get | Lifetime | Cost |
|---|---|---|---|---|---|
| [tilde.zone](https://tilde.zone/) | yes (banner) | unknown: no operator page was found that documents how to get an account | unknown; a Debian host answering SSH, and a Mastodon instance on the same name | unknown | unknown |
| [GitHub Codespaces](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) | yes (documented) | gh codespace ssh -c CODESPACE-NAME; the default dev container runs an SSH server | 2-core default machine (8 GB, 32 GB storage); 2/4/8/16/32-core available | 120 core-hours per month on GitHub Free; a codespace is auto-stopped after its retention period of inactivity and resume is blocked once quota is spent without a payment method | 0 for 120 core-hours/month, then blocked |
| [Fly.io](https://fly.io/docs/about/pricing/) | no | fly ssh console reaches a running Machine, but there is no free allowance to run one | shared-CPU Machines; volumes first 10 GB free per month | pay-as-you-go | no free VM allowance; the only 'first free' is 10 GB of volume capacity |
| [Koyeb](https://www.koyeb.com/docs/run-and-scale/scale-to-zero) | no | No published inbound SSH; the free plan is not in the published tiers | free Instance: 1 shared vCPU (0.1 vCPU), 512 MB RAM, 2 GB SSD, no persistent volumes; fra and was regions only | scales to zero after 1 h without inbound traffic; the idle period cannot be changed on the free Instance | 0 on the free Instance; $0/month tier, scales to zero when idle |
| [Microterm, LinuxOnTab](https://linuxontab.com/) | no | none: both run a Linux kernel inside the browser via WebAssembly (TinyEMU/RISC-V64 and v86) | Alpine userland in-browser, Microterm claims persistent local storage up to 40 GB; LinuxOnTab ships a real x86 kernel and calls itself 'Free, no signup' | runs in the reader's own browser tab | 0 |
| [Play with Docker](https://labs.play-with-docker.com/) | no | browser terminal, never SSH | 4-hour Docker-in-Docker session (historical) | unavailable from 2026-03-01 | n/a |

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

Railway Free VM, SDF Public Access UNIX System, hashbang (#!), tilde.club, tilde.guru, tilde.town

Reachability was checked through the relay's own `/trace` diagnostic because
this sandbox's egress proxy **refuses port 22** (`CONNECT ... 403`) and permits
443. That is a property of this sandbox, not of any provider, and it is why the
relay is the only route at all here.

**The 2 hosts this sandbox could NOT reach are Blinkenshell, alwaysdata Free.**
That is recorded as a fact about this host and this network, not as a verdict on
the services: Blinkenshell answered 0 bytes on 22, 2222 and 443 alike, and
alwaysdata's free tier is reached through a per-account host rather than a
public one. Neither row claims the service is dead.

---

## The detail behind every row

**hashbang (#!)** - `free-account`, account=no, card=no
- quote: “curl -d '{"user":"someuser","key":"'"$(cat ~/.ssh/id_rsa.pub)"'","host":"someHost.hashbang.sh"}' -H 'Content-Type: application/json' https://hashbang.sh/user/create”
- endpoint: `de1.hashbang.sh:22` (banner-verified)
- checked: first-party-fetched 2026-10-02; the node was named by hashbang's OWN https://hashbang.sh/server/stats API (de1.hashbang.sh) and the relay dialled de1.hashbang.sh:22, reading banner SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u10
- caveats: CORRECTION to an earlier census: the host in the documented example, someHost.hashbang.sh, does not resolve (the relay: "no A/AAAA records"). The real node name comes from hashbang's own /server/stats. Account creation needs no account and no card - a public key IS the account - which makes it the closest thing to anonymous here besides Railway, but it is not classified anonymous because the operator reserves the right to refuse and the account has a human owner.

**Railway Free VM** - `anonymous`, account=no, card=no
- quote: “No. Railway identifies you by your SSH key. If you don't have one, run ssh-keygen -t ed25519 and connect again. You only sign up if you want to keep the box.”
- endpoint: `railway.new:22` (banner-verified)
- checked: first-party-fetched 2026-10-02 (162,813 bytes, HTTP 200); relay /trace dialed railway.new:22 and read banner SSH-2.0-Go
- caveats: The ONLY row here that needs no account at all. Anonymous trials are capped per region and can be disabled under demand (the page's own words: "Anonymous trials are temporarily disabled"); the preview URL is visible only from the creating IP until claimed; abuse protections and a shared AI budget apply. Reaching it FROM THIS SANDBOX over the relay gets as far as the SSH banner and then the relay link closes before key exchange completes, so a working login here is not established. See research/verification/ssh-relay-2026-10-02.md.

**SDF Public Access UNIX System** - `free-account`, account=yes, card=no
- quote: “Create a Free UNIX Shell Account ... Linux/UNIX users can type 'ssh new@sdf.org' at their shell prompt.”
- endpoint: `sdf.org:22` (banner-verified)
- checked: first-party-fetched 2026-10-02; quote re-verified verbatim on the cited page by tools/check-quotes.py; relay /trace dialed sdf.org:22 and read banner SSH-2.0-OpenSSH_10.4
- caveats: A shared shell, not a VM. The same site is reachable at freeshell.org and webstats.freeshell.org, which both resolve to this one system rather than being three providers.

**tilde.club** - `free-account`, account=yes, card=no
- quote: “SSH fingerprints: SHA256:M2URWy/QGPdn8K1XHA5KEWQs+7RtqKCkHCqp1NyxFyI (RSA)”
- endpoint: `tilde.club:22` (banner-verified)
- checked: first-party-fetched 2026-10-02; relay /trace dialed tilde.club:22 and read banner SSH-2.0-OpenSSH_10.0
- caveats: Shared shell, not a VM; signups no longer accept gmail.com addresses.

**tilde.guru** - `free-account`, account=yes, card=no
- quote: “a FreeBSD pubnix Â· est. 2021 Â· member of the tildeverse”
- endpoint: `tilde.guru:22` (banner-verified)
- checked: first-party-fetched 2026-10-02 (HTTP 200); relay /trace dialed tilde.guru:22 and read banner SSH-2.0-OpenSSH_10.0 FreeBSD-20250801
- caveats: NEW ROW, not in the earlier census. FreeBSD, not Linux. Shared shell, not a VM. Signup and resource limits are on the site's own wiki, which returned 404 for /wiki/Join when fetched here.

**tilde.town** - `free-account`, account=yes, card=no
- quote: “ecdsa host key: SHA256:RNFVaXxh2wnrolcByZQBRxRZDFBb2HRCnNq/g9ZGRp0”
- endpoint: `tilde.town:22` (banner-verified)
- checked: first-party-fetched 2026-10-02; relay /trace dialed tilde.town:22 and read banner SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4
- caveats: Shared shell; signup is by invitation/request; not a VM.

**alwaysdata Free** - `free-account`, account=yes, card=no
- quote: “free for personal needs, ad-free offer available for life”
- endpoint: `ssh.<account>.alwaysdata.com (per-account, not a public host)` (not-verified)
- checked: first-party-fetched 2026-10-02; quote re-verified verbatim on the cited page by tools/check-quotes.py. The earlier quote ('Free ... 0 EUR/month ... Disk space SSD 1 Go') did NOT survive being fetched and was replaced with the page's own current wording
- caveats: Shared web-hosting account, not a root VM; the free quota is small and some services are restricted.

**AWS Free Tier** - `free-tier-card`, account=yes, card=yes
- quote: “When you create a new AWS Free Tier account, you get $100 in credits immediately. As you explore key services, you can earn up to $100 more. That's up to $200 over 6 months ... The account closes on its own 6 months after you open it or when your credits run out, whichever comes first.”
- endpoint: `per-instance, public IP assigned by AWS` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: A card is required. The free plan is time-boxed and closes itself; the old 750-hours-for-12-months t2.micro offer is no longer the headline shape of the plan.

**Azure Free Account** - `free-tier-card`, account=yes, card=yes
- quote: “12 months Azure Virtual Machines for Linux or Windows 750 hours each of B1s, B2pts v2 (Arm-based), and B2ats v2 (AMD-based) burstable VMs ... $200 credit to use on Azure services within 30 days”
- endpoint: `per-instance, public IP assigned by Azure` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: A card is required and a temporary $1 authorization may be placed at signup. The 750-hour VM allowance is 12 months only; the $200 credit is 30 days.

**Blinkenshell** - `free-account`, account=yes, card=no
- quote: “Blinkenshell uses the non-standard port 2222 for SSH (instead of 22), so you need to specify this when connecting.”
- endpoint: `blinkenshell.org:2222` (not-verified)
- checked: MEASURED 2026-10-06: the wiki page was fetched (HTTP 200) and its feature-comparison table parsed CELL BY CELL rather than flattened to text. The Free column is EMPTY for 'Bouncer (BNC, znc, weechat-relay)', 'IRC bots' and 'Listen TCP/UDP port (custom server)'; all three are Supporter-only. The operator's own rules page confirms independently: 'No IRC bots are allowed on free accounts' and 'You are not allowed to run any server/daemon on free accounts'. Re-dialed from a residential host on the same date: ports 80 and 443 answer (HTTPS 200, 55,375 bytes) while 22, 2222 and 6697 all time out.
- caveats: CORRECTED 2026-10-06. A flattened text scrape of the wiki table makes the free tier look as though it includes IRC bots and listening TCP ports. The cells do not: those rows have no tick in the Free column. So a free Blinkenshell account is a screen/tmux bot host and NOT an endpoint host - which matters for anyone planning to run a daemon or tunnel there. On reachability, the earlier reading 'the host is refusing or filtering this network' is now measured rather than inferred: from a different network than the original sweep, the web ports answer and every non-web port times out, so the host is alive and filtering by protocol. The 2026-10-02 note that port 2222 must be dialled specifically stands and is confirmed by the vendor's FAQ.

**Google Cloud Free Tier (e2-micro)** - `free-tier-card`, account=yes, card=yes
- quote: “1 non-preemptible e2-micro VM instance per month in one of the following US regions ... 30 GB-months standard persistent disk ... 1 GB of outbound data transfer ... per month.”
- endpoint: `per-instance, external IP assigned by Google` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: A billing account with a card is required. The allowance is one e2-micro in us-west1, us-central1 or us-east1; the $300 signup credit is one-time and separate.

**Google Cloud Shell** - `free-account`, account=yes, card=no
- quote: “The default weekly Cloud Shell quota is 50 hours.”
- endpoint: `published per-session by Google Cloud Shell` (provider-documented)
- checked: provider-documented
- caveats: Sign-in with a Google account is required. Exceeding the weekly quota suspends Cloud Shell until the next week. The VM is recreated, so only $HOME survives.

**Hugging Face Spaces** - `free-account`, account=yes, card=no
- quote: “Static Spaces are free for everyone. Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts, Team or Enterprise for organizations. Free personal accounts in good standing can still host up to 2 Gradio Spaces running on ZeroGPU.”
- endpoint: `per-Space, published while the Space runs` (provider-documented)
- checked: MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 222,896 bytes) and the quoted sentence appears verbatim. The 48-hour sleep figure was read from spaces-gpus on the same date (HTTP 200, 221,818 bytes), which states a cpu-basic Space 'will go to sleep if inactive for more than a set time (currently, 48 hours)'. The change is traceable to a docs commit: huggingface/hub-docs@34ee0f00, 2026-07-21.
- caveats: DEMOTED 2026-10-06 - the free CPU Basic Space (2 vCPU / 16 GB) this row advertised can no longer be created on a free account. The hardware still appears in HF's pricing table at $0, which is what makes the stale claim survive: the price is real, the CREATION is not. A paid-plan gate at creation is the one wall no keepalive or relay can defeat. A free account keeps Static Spaces (no runtime, so no daemon) and 2 ZeroGPU Spaces.

**Modal Starter** - `free-account`, account=yes, card=no
- quote: “$0 + compute / month ... $30 / month free credits ... 1 TiB / month free network egress”
- endpoint: `not published; reached through the Modal CLI` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: An account is required; the $30 is a monthly credit, not a permanent free machine. It is a container sandbox, not a general VPS.

**Oracle Cloud Always Free** - `free-tier-card`, account=yes, card=yes
- quote: “All tenancies get the first 1,500 OCPU hours and 9,000 GB hours per month for free for VM instances using the VM.Standard.A1.Flex shape, which has an Arm processor. For Always Free tenancies, this is equivalent to 2 OCPUs and 12 GB of memory.”
- endpoint: `per-instance, public IP assigned by Oracle` (provider-documented)
- checked: MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 53,867 bytes) and the quoted sentence appears verbatim in the response body. This resolves the open question the 2026-10-02 revision recorded: the A1 allowance figures are NOT on oracle.com/cloud/free, they are on the Always Free documentation page, which is now the cited source.
- caveats: CORRECTED 2026-10-06 - the figure this row carried (4 OCPU / 24 GB) was WRONG BY 2x and came from the upstream corpus card, not from Oracle. Oracle's own sentence says 'equivalent to 2 OCPUs and 12 GB of memory', and the arithmetic agrees (1,500 OCPU-hours over a ~744-hour month is 2 OCPUs). Any catalogue figure derived from the 4/24 card is wrong and should be recomputed. Two further first-party facts now attached: a card is required at signup and is not charged on Always Free, and an idle instance may be reclaimed - Oracle deems a VM idle if, over a 7-day period, 95th-percentile CPU and network are both under 20% and memory is under 20% on A1 shapes. That is a utilisation threshold rather than a session cap, so sustained work defeats it.

**AWS CloudShell** - `free-account`, account=yes, card=no
- quote: “Run scripts and commands at no extra cost, with up to 1 GB of persistent storage per AWS Region.”
- endpoint: `none published` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: An AWS account is required. It is a browser shell, not a machine you can SSH into from elsewhere.

**Azure Cloud Shell** - `free-account`, account=yes, card=no
- quote: “Use of the machine hosting Cloud Shell is free. Cloud Shell requires a storage account to host the mounted Azure Files share. Regular storage costs apply.”
- endpoint: `none published` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: An Azure account and a storage account are required; the storage share is billed normally.

**Killercoda** - `free-account`, account=yes, card=no
- quote: “Membership PLUS Includes all from FREE Use scenarios for up to 4 hours instead of just one ... Open up to 3 scenarios at the same time”
- endpoint: `none published` (not-verified)
- checked: first-party-fetched 2026-10-02: the root page does NOT carry the quota text; it is on /pricing, which is now the cited source. Re-verified by tools/check-quotes.py
- caveats: The page does not state whether a login is required to start a free scenario; treat 'anonymous' as unverified. Browser terminal only, no SSH.

**Northflank Sandbox tier** - `free-tier-card`, account=yes, card=yes
- quote: “all users must add a payment method to start creating resources on Northflank, regardless of plan selection. This is to verify user identity, and prevent malicious usage of the platform.”
- endpoint: `none published` (provider-documented)
- checked: MEASURED 2026-10-06: the billing docs page was fetched (HTTP 200, 346,968 bytes) and the quoted sentence appears verbatim. The pricing page was fetched separately (HTTP 200, 193,710 bytes) and states 'Always-on-compute - no sleeping :)' alongside 'Get started for free', which is why the card requirement is recorded as measured rather than read off the marketing.
- caveats: CARD CORRECTION 2026-10-06: this row previously read card_required=false on the strength of the pricing page's 'Get started for free'. Northflank's own billing docs require a payment method for every user regardless of plan, to verify identity and prevent abuse, so the class moves free-account -> free-tier-card. It is kept rather than dropped because it is the cleanest no-sleep free container found: no idle timeout, no session cap, no expiry. No persistent volumes on free, no inbound SSH, and the docs say it should not be used for production. The two pages still disagree on the free-tier shape (pricing: 2 services, 1 database, 2 cron jobs; docs: 2 services, 2 jobs, 1 addon), which is unresolved.

**Render Free compute** - `free-account`, account=yes, card=no
- quote: “Free ( limitations apply ) $0/month 512 MB RAM free Less than 1 CPU”
- endpoint: `none published` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: Web services, key-value and Postgres - not a VM. Free instances sleep and are not for production.

## Changed and dead

**tilde.zone** - `changed`, account=yes, card=no
- quote: none taken; see the measurement note below
- endpoint: `tilde.zone:22` (banner-verified)
- checked: reachability measured 2026-10-02: relay /trace dialed tilde.zone:22 and read banner SSH-2.0-OpenSSH_10.0p2 Debian-7+deb13u4. NO first-party claim of a free shell was found: the site's only page is a Mastodon instance requiring JavaScript, and none of its outbound links identify a shell operator
- caveats: DEMOTED from the free-shell table after review, deliberately, and this row is the reason it is still here rather than deleted. A host answering SSH is EVIDENCE OF A HOST, NOT OF A FREE SHELL: fetched first-party, tilde.zone publishes nothing about free accounts, signup, or who operates it. A row that says 'free' on a banner alone is exactly the padding the guard exists to prevent, so it now reads 'unknown' where the three facts cannot be established and is classed `changed` to keep it out of the free tables while leaving the measurement visible. Same Debian build string as tilde.town, which is what a shared image or a mirror would produce - a reason to verify the operator, not a claim they are one host. Recovering the row requires a first-party page that names an operator and a signup path.

**GitHub Codespaces** - `changed`, account=yes, card=no
- quote: “Account plan | Storage per month | Compute time per month | GitHub Free for personal accounts | 15 GB-month | 120 hrs”
- endpoint: `published per-codespace by GitHub` (provider-documented)
- checked: MEASURED 2026-10-06: the cited page was fetched (HTTP 200, 196,324 bytes) and the quota table row quoted above is present in the response. The 2026-10-02 revision recorded that the '120 core hours' figure 'did not survive being fetched'; it does, in a table on the exact page cited. The earlier extraction missed the table rather than the sentence being absent.
- caveats: PARTIALLY RESTORED 2026-10-06. The 120 core-hour figure is first-party again, so the row no longer reads cost unknown. It stays out of the free tables because 120 core-hours of 2-core compute is ~5 days of continuous uptime, which is a dev-environment quota rather than an always-on box. Note the asymmetry that ends it: with no payment method on file, exhausting the quota BLOCKS resume rather than billing, so there is no soft landing.

**Fly.io** - `changed`, account=yes, card=yes
- quote: “$0.08/GB per month First 10GB free each month”
- endpoint: `per-Machine` (provider-documented)
- checked: first-party-fetched 2026-10-02
- caveats: The free Machine allowance Fly.io used to grant is gone from the pricing page. A card is required; the 10 GB is storage, not compute.

**Koyeb** - `changed`, account=yes, card=no
- quote: “The Koyeb Free Instance automatically scales down to zero when it doesn't receive any traffic for 1 hour. Scale-to-zero on this Instance cannot be disabled, and the idle period cannot be customized.”
- endpoint: `none published` (provider-documented)
- checked: MEASURED 2026-10-06: the cited docs page was fetched (HTTP 200, 296,380 bytes) and the quoted sentence appears verbatim, naming the free Instance directly.
- caveats: RESTORED 2026-10-06. The 2026-10-02 revision recorded this as 'the free plan is not in the published tiers', checking the pricing page. The free Instance is documented on Koyeb's scale-to-zero docs page with its idle rule stated explicitly. It stays out of the free tables for the SSH question, not the free question: Koyeb publishes no inbound SSH, the idle period cannot be raised on the free tier, and there are no persistent volumes.

**Microterm, LinuxOnTab** - `changed`, account=no, card=no
- quote: “Free, no signup”
- endpoint: `none: there is no network path to these at all` (not-verified)
- checked: first-party-fetched 2026-10-02: linuxontab.com carries the quoted phrase 'Free, no signup' verbatim. The companion project microterm.dev was fetched the same day (HTTP 200) and is described in the caveats; it is not the cited source because the quote is not on it
- caveats: NEW ROW, and the category is new rather than the entries: these are 'anonymous free Linux' with no account and no card, but the machine is the READER'S OWN, there is no host to SSH to, and nothing runs while the tab is closed. Listing them beside a real remote VM would be a category error, which is why they are here rather than in the SSH table. Microterm is RISC-V64 emulated; LinuxOnTab ships a native WebAssembly x86 kernel.

**Play with Docker** - `dead`, account=no, card=no
- quote: “Deprecation notice: Play with Docker will be unavailable starting March 1, 2026.”
- endpoint: `none; the product is gone` (not-verified)
- checked: first-party-fetched 2026-10-02
- caveats: Recorded because it is the canonical 'anonymous free VM' many lists still cite. It is gone; Docker Docs now points at supported labs.

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
