# peli-cloud — every provider, cheapest first, at every period

**Generated 2026-10-02T03:39:36Z** from the corpus at `f6a71ab09fef`. Every row links to the provider's own page and to the card the number was read from.

## How to read this

A cloud sandbox is not a VPS. It bills while it runs, and most of them stop billing when they are stopped. So **the price is a function of how long you hold it**, and one monthly number cannot rank the market: the cheapest provider at 2 hours/day is not the cheapest provider at 24/7, and often not even the same list.

Every table below is priced at three shapes and four duty cycles:

| shape | vCPU / RAM | what it is for |
|---|---|---|
| `tiny` | 1 vCPU / 1 GiB | a shell, a build step, a short tool call |
| `agent` | 2 vCPU / 4 GiB | the normal agent sandbox |
| `devbox` | 4 vCPU / 8 GiB | a developer box you keep around |

| duty cycle | hours/day | billed hours/month (at 30 days) |
|---|---|---|
| `1h` | 1 h/day | 30 |
| `4h` | 4 h/day | 120 |
| `10h` | 10 h/day | 300 |
| `24h` | 24 h/day | 720 |

`keep` is the fraction of wall-clock time the provider bills for. `1.00` means billed for uptime no matter what the machine is doing; `0.00` means it suspends on idle. It is read from the card's published features, and a provider that publishes no suspension feature is recorded as `1.00`, because a plain VM is billed for uptime. Unknown is never assumed to be the cheap case.

---

## A. Free tier — what costs nothing right now

### A1. Recurring credit — free every month, until it runs out

13 providers publish a credit that recurs. **This is the complete list; there is no large free tier in this market.** The biggest is $30/month.

| # | provider | category | credit / month | what that buys at the `agent` rate | keep | link |
|---|---|---|---|---|---|---|
| 1 | [Modal](https://modal.com/pricing) | agent-sandbox | $30 | 79 machine-hours (2.6 h/day for a month) | 1.00 | `modal` |
| 2 | [Freestyle](https://www.freestyle.sh/pricing) | agent-sandbox | $18.38 | 139 machine-hours (4.6 h/day for a month) | 1.00 | `freestyle` |
| 3 | [Run Cloud](https://docs.run.cloud/sandboxes/index.md) | agent-sandbox | $15 | 322 machine-hours (10.7 h/day for a month) | 1.00 | `run-cloud` |
| 4 | [Blacksmith (GitHub Actions runners)](https://www.blacksmith.sh/pricing) | macos | $12 | 80 machine-hours (2.7 h/day for a month) | 1.00 | `blacksmith` |
| 5 | [InsForge (InstaCloud)](https://www.instacloud.com/pricing) | paas | $10 | 90 machine-hours (3.0 h/day for a month) | 1.00 | `insforge-instacloud` |
| 6 | [Bright Data Browser API](https://brightdata.com/pricing/scraping-browser) | browser | $7.5 | - | 0.00 | `bright-data-browser` |
| 7 | [AWS Lambda](https://aws.amazon.com/lambda/pricing/) | hyperscaler | $6.87 | 43 machine-hours (1.4 h/day for a month) | 1.00 | `aws-lambda` |
| 8 | [CodeSandbox SDK](https://codesandbox.io/docs/sdk/pricing) | agent-sandbox | $5.944 | 40 machine-hours (1.3 h/day for a month) | 1.00 | `codesandbox-sdk` |
| 9 | [Azure Container Apps (Consumption, Dedicated, Dynamic Sessions)](https://azure.microsoft.com/en-us/pricing/details/container-apps/) | hyperscaler | $5.4 | 25 machine-hours (0.8 h/day for a month) | 1.00 | `azure-container-apps` |
| 10 | [Google Cloud Run](https://cloud.google.com/run/pricing) | hyperscaler | $5.22 | 176 machine-hours (5.9 h/day for a month) | 1.00 | `google-cloud-run` |
| 11 | [Kedge](https://kedge.dev/docs/billing) | agent-sandbox | $5 | 73 machine-hours (2.4 h/day for a month) | 1.00 | `kedge` |
| 12 | [Sail Research (Sailboxes)](https://docs.sailresearch.com/pricing) | agent-sandbox | $5 | 81 machine-hours (2.7 h/day for a month) | 1.00 | `sail` |
| 13 | [Scrapeless Agent Browser](https://www.scrapeless.com/en/pricing) | browser | $0.09 | - | 0.00 | `scrapeless` |

### A2. One-time credit — free exactly once

81 providers publish a signup credit. It is worth its face value once and never renews.

| # | provider | category | one-time credit | what that buys at the `agent` rate | link |
|---|---|---|---|---|---|
| 1 | [Run Cloud](https://docs.run.cloud/sandboxes/index.md) | agent-sandbox | $5 | 107 machine-hours (4 h/day for a month) | `run-cloud` |
| 2 | [AWS Lambda](https://aws.amazon.com/lambda/pricing/) | hyperscaler | $200 | 1250 machine-hours (42 h/day for a month) | `aws-lambda` |
| 3 | [Azure Container Apps (Consumption, Dedicated, Dynamic Sessions)](https://azure.microsoft.com/en-us/pricing/details/container-apps/) | hyperscaler | $200 | 926 machine-hours (31 h/day for a month) | `azure-container-apps` |
| 4 | [Google Cloud Run](https://cloud.google.com/run/pricing) | hyperscaler | $300 | 10089 machine-hours (336 h/day for a month) | `google-cloud-run` |
| 5 | [Google Compute Engine (Linux VMs)](https://cloud.google.com/products/compute/pricing/general-purpose) | hyperscaler | $300 | 4477 machine-hours (149 h/day for a month) | `gcp-compute` |
| 6 | [Google Compute Engine (Windows Server)](https://cloud.google.com/compute/disks-image-pricing#windows_server_pricing) | windows | $300 | 8954 machine-hours (298 h/day for a month) | `gcp-windows` |
| 7 | [GKE Agent Sandbox](https://cloud.google.com/kubernetes-engine/docs/concepts/agent-sandbox) | hyperscaler | $300 | 2760 machine-hours (92 h/day for a month) | `gke-agent-sandbox` |
| 8 | [Google Colab](https://developers.google.com/colab) | dev-env | $300 | 4519 machine-hours (151 h/day for a month) | `google-colab` |
| 9 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | hyperscaler | $300 | 32877 machine-hours (1096 h/day for a month) | `oracle-cloud` |
| 10 | [Google Agent Platform Sandbox (Code Execution / Shell / Computer Use)](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) | agent-sandbox | $300 | 1456 machine-hours (49 h/day for a month) | `vertex-computer-use` |
| 11 | [Open Telekom Cloud / T Cloud Public](https://www.open-telekom-cloud.com/en/prices) | hyperscaler | $284.45 | 2173 machine-hours (72 h/day for a month) | `open-telekom-cloud` |
| 12 | [Samsung SDS Cloud Platform](https://cloud.samsungsds.com/serviceportal/pricing.html) | hyperscaler | $260 | 2902 machine-hours (97 h/day for a month) | `samsung-cloud` |
| 13 | [Civo Compute](https://www.civo.com/pricing) | hyperscaler | $250 | 8400 machine-hours (280 h/day for a month) | `civo` |
| 14 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | hyperscaler | $220.92 | 6787 machine-hours (226 h/day for a month) | `kakao-cloud` |
| 15 | [AWS Lambda MicroVMs](https://aws.amazon.com/lambda/pricing/) | hyperscaler | $200 | 793 machine-hours (26 h/day for a month) | `aws-lambda-microvms` |
| 16 | [Amazon WorkSpaces Personal (Windows)](https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/) | windows | $200 | 4710 machine-hours (157 h/day for a month) | `aws-workspaces` |
| 17 | [Azure Container Apps Sandboxes](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-overview) | hyperscaler | $200 | 926 machine-hours (31 h/day for a month) | `azure-container-apps-sandboxes` |
| 18 | [Microsoft Foundry hosted agents (East US)](https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/) | hyperscaler | $200 | 813 machine-hours (27 h/day for a month) | `azure-foundry-agents` |
| 19 | [Azure Virtual Machines (Linux)](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/) | hyperscaler | $200 | 5319 machine-hours (177 h/day for a month) | `azure-vm` |
| 20 | [Azure Virtual Machines (Windows Server)](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/windows/) | windows | $200 | 4808 machine-hours (160 h/day for a month) | `azure-windows` |
| 21 | [Blaxel](https://blaxel.ai/pricing) | agent-sandbox | $200 | 1208 machine-hours (40 h/day for a month) | `blaxel` |
| 22 | [Daytona (Windows sandboxes)](https://www.daytona.io/pricing) | windows | $200 | 1208 machine-hours (40 h/day for a month) | `daytona-windows` |
| 23 | [Daytona](https://www.daytona.io/pricing) | agent-sandbox | $200 | 1208 machine-hours (40 h/day for a month) | `daytona` |
| 24 | [Hopx](https://hopx.ai/pricing) | agent-sandbox | $200 | 1208 machine-hours (40 h/day for a month) | `hopx` |
| 25 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | hyperscaler | $200 | 6103 machine-hours (203 h/day for a month) | `ibm-cloud-vpc` |
| 26 | [OVHcloud GPU instances](https://www.ovhcloud.com/en/public-cloud/prices/) | gpu-cloud | $200 | - | `ovh-gpu` |
| 27 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | hyperscaler | $200 | 7812 machine-hours (260 h/day for a month) | `ovhcloud` |
| 28 | [Replicas](https://replicas.dev) | agent-sandbox | $120 | 250 machine-hours (8 h/day for a month) | `replicas` |
| 29 | [Amazon Bedrock AgentCore (Runtime / Code Interpreter / Browser)](https://aws.amazon.com/bedrock/agentcore/pricing/) | hyperscaler | $100 | 461 machine-hours (15 h/day for a month) | `aws-agentcore` |
| 30 | [AWS EC2 Mac (Dedicated Host)](https://aws.amazon.com/ec2/instance-types/mac/) | macos | $100 | 154 machine-hours (5 h/day for a month) | `aws-ec2-mac` |
| 31 | [AWS EC2 (Windows Server)](https://aws.amazon.com/ec2/pricing/on-demand/) | windows | $100 | 1667 machine-hours (56 h/day for a month) | `aws-ec2-windows` |
| 32 | [AWS EC2 (reference VMs)](https://aws.amazon.com/ec2/pricing/on-demand/) | hyperscaler | $100 | 2037 machine-hours (68 h/day for a month) | `aws-ec2` |
| 33 | [AWS Fargate](https://aws.amazon.com/fargate/pricing/) | hyperscaler | $100 | 1721 machine-hours (57 h/day for a month) | `aws-fargate` |
| 34 | [Declaw](https://docs.declaw.ai/platform/billing) | agent-sandbox | $100 | 604 machine-hours (20 h/day for a month) | `declaw` |
| 35 | [E2B](https://e2b.dev/pricing) | agent-sandbox | $100 | 604 machine-hours (20 h/day for a month) | `e2b` |
| 36 | [Kamatera](https://www.kamatera.com/pricing/) | hyperscaler | $100 | 3650 machine-hours (122 h/day for a month) | `kamatera` |
| 37 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | hyperscaler | $100 | 2778 machine-hours (93 h/day for a month) | `linode` |
| 38 | [Novita AI Agent Sandbox](https://docs.novita.ai/guides/sandbox-pricing) | agent-sandbox | $100 | 857 machine-hours (29 h/day for a month) | `novita` |
| 39 | [smol machines](https://smolmachines.com/pricing) | agent-sandbox | $100 | 607 machine-hours (20 h/day for a month) | `smol-machines` |
| 40 | [Superserve](https://superserve.ai/pricing) | agent-sandbox | $100 | 604 machine-hours (20 h/day for a month) | `superserve` |
| 41 | [Tenki Sandbox](https://tenki.cloud/pricing) | agent-sandbox | $100 | 604 machine-hours (20 h/day for a month) | `tenki` |
| 42 | [use.computer](https://use.computer/) | macos | $100 | 222 machine-hours (7 h/day for a month) | `use-computer` |
| 43 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | hyperscaler | $90 | 5070 machine-hours (169 h/day for a month) | `alibaba-ecs` |
| 44 | [InstaVM](https://instavm.io/pricing) | agent-sandbox | $50 | 302 machine-hours (10 h/day for a month) | `instavm` |
| 45 | [Isorun](https://docs.isorun.ai/getting-started/pricing) | agent-sandbox | $50 | 455 machine-hours (15 h/day for a month) | `isorun` |
| 46 | [Runloop](https://www.runloop.ai/pricing) | agent-sandbox | $50 | 158 machine-hours (5 h/day for a month) | `runloop` |
| 47 | [Runta](https://runta.com/pricing/) | agent-sandbox | $50 | 302 machine-hours (10 h/day for a month) | `runta` |
| 48 | [boxd](https://boxd.sh/pricing) | agent-sandbox | $30 | 158 machine-hours (5 h/day for a month) | `boxd` |
| 49 | [Lightning AI](https://lightning.ai/pricing) | dev-env | $30 | 59 machine-hours (2 h/day for a month) | `lightning-ai` |
| 50 | [Prized](https://prized.dev/docs/billing) | dev-env | $30 | 876 machine-hours (29 h/day for a month) | `prized` |
| 51 | [Sprites (Fly.io)](https://fly.io/pricing) | agent-sandbox | $30 | 183 machine-hours (6 h/day for a month) | `sprites` |
| 52 | [Steel.dev](https://docs.steel.dev/overview/pricinglimits) | browser (browser product, not a machine) | $30 | - | `steel` |
| 53 | [orkestr Sandboxes](https://orkestr.eu/sandboxes) | agent-sandbox | $28.445 | 167 machine-hours (6 h/day for a month) | `orkestr` |
| 54 | [Cube Computer](https://cube.computer/) | dev-env | $25 | 1011 machine-hours (34 h/day for a month) | `cube` |
| 55 | [Docker Cloud Sandboxes](https://www.docker.com/blog/introducing-cloud-sandboxes-start-on-your-laptop-finish-in-the-cloud/) | agent-sandbox | $25 | 179 machine-hours (6 h/day for a month) | `docker-cloud-sandboxes` |
| 56 | [zipbox](https://zipbox.ai/pricing) | agent-sandbox | $25 | 1825 machine-hours (61 h/day for a month) | `zipbox` |
| 57 | [Flow Swiss Mac Bare Metal](https://doc.flow.swiss/platform/pricing/mac-bare-metal) | macos | $24.17 | 74 machine-hours (2 h/day for a month) | `flow-swiss-mac` |
| 58 | [Dedalus Labs](https://www.dedaluslabs.ai/pricing) | agent-sandbox | $20 | 134 machine-hours (4 h/day for a month) | `dedalus-labs` |
| 59 | [Buildkite hosted agents](https://buildkite.com/pricing) | macos | $16 | 33 machine-hours (1 h/day for a month) | `buildkite-hosted` |
| 60 | [UCloud Agent Sandbox](https://astraflow.ucloud.cn/docs/agent-sandbox) | agent-sandbox | $15.4504 | 240 machine-hours (8 h/day for a month) | `ucloud` |
| 61 | [Browser Use Cloud](https://browser-use.com/pricing) | browser (browser product, not a machine) | $15 | - | `browser-use` |
| 62 | [Lizard](https://lizard.build/pricing) | agent-sandbox | $10 | 1111 machine-hours (37 h/day for a month) | `lizard` |
| 63 | [MIOSA](https://miosa.ai/pricing) | agent-sandbox | $10 | 64 machine-hours (2 h/day for a month) | `miosa` |
| 64 | [Notte](https://www.notte.cc/pricing) | browser (browser product, not a machine) | $10 | - | `notte` |
| 65 | [OpenComputer](https://opencomputer.dev/sandboxes) | agent-sandbox | $10 | 26 machine-hours (1 h/day for a month) | `opencomputer` |
| 66 | [TinyFish](https://www.tinyfish.ai/pricing) | browser (browser product, not a machine) | $8 | - | `tinyfish` |
| 67 | [Buddy Sandboxes](https://buddy.works/pricing) | agent-sandbox | $5 | 58 machine-hours (2 h/day for a month) | `buddy` |
| 68 | [CreateOS Sandbox (NodeOps)](https://createos.sh/products/sandbox) | agent-sandbox | $5 | 42 machine-hours (1 h/day for a month) | `createos` |
| 69 | [DigitalOcean GPU Droplets](https://www.digitalocean.com/pricing/gpu-droplets) | gpu-cloud | $5 | - | `digitalocean-gpu` |
| 70 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | hyperscaler | $5 | 140 machine-hours (5 h/day for a month) | `digitalocean` |
| 71 | [Hyperbrowser](https://www.hyperbrowser.ai/pricing) | browser (browser product, not a machine) | $5 | - | `hyperbrowser` |
| 72 | [Railway](https://railway.com/pricing) | agent-sandbox | $5 | 45 machine-hours (1 h/day for a month) | `railway` |
| 73 | [RunAnywhere](https://www.runanywhere.ai/) | inference-api (browser product, not a machine) | $5 | - | `runanywhere` |
| 74 | [Sandbox as a Service](https://sandbox-as-a-service.com/pricing) | agent-sandbox | $5 | 56 machine-hours (2 h/day for a month) | `sandbox-as-a-service` |
| 75 | [Smooth](https://www.smooth.sh/pricing) | browser (browser product, not a machine) | $5 | - | `smooth` |
| 76 | [Huawei Cloud AgentArts](https://support.huaweicloud.com/price-agentarts/agentarts-price-pdf.pdf) | agent-sandbox | $3.31064 | 8 machine-hours (0 h/day for a month) | `huawei-cloud` |
| 77 | [Tencent Cloud Studio](https://cloud.tencent.cn/document/product/1039/131894) | dev-env | $2.98 | 80 machine-hours (3 h/day for a month) | `tencent-cloud-studio` |
| 78 | [Agent 37](https://www.agent37.com/pricing) | agent-sandbox | $1 | 166 machine-hours (6 h/day for a month) | `agent-37` |
| 79 | [boat.dev](https://docs.boat.dev/pricing) | agent-sandbox | $0.9 | 50 machine-hours (2 h/day for a month) | `boat` |
| 80 | [BrowserAct](https://www.browseract.com/pricing) | browser (browser product, not a machine) | $0.32 | - | `browseract` |
| 81 | [Scrapfly Cloud Browser](https://scrapfly.io/pricing) | browser (browser product, not a machine) | $0.15 | - | `scrapfly` |

### A3. $0 entry tier, no credit published — unknown, not free

116 cards sell a plan whose fee is $0 but publish no credit, no quota and no cap. Whether that is a usable free tier or an unpriced meter is **not in the card**. They are listed here rather than in the paid tables because a $0 fee is not evidence that the machine is free.

| # | provider | category | $/hour | 24h/day month | link |
|---|---|---|---|---|---|
| 1 | [Contabo](https://contabo.com/en-us/pricing/) | hyperscaler | 0.0090 | 6.51 | `contabo` |
| 2 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | hyperscaler | 0.0104 | 7.49 | `hetzner-cloud` |
| 3 | [Upstash Box](https://upstash.com/pricing/box) | agent-sandbox | 0.0110 | 7.89 | `upstash-box` |
| 4 | [netcup VPS](https://www.netcup.com/en/server/vps) | hyperscaler | 0.0117 | 8.39 | `netcup` |
| 5 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | hyperscaler | 0.0148 | 10.65 | `ionos` |
| 6 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | hyperscaler | 0.0193 | 13.92 | `gcore` |
| 7 | [shellbox](https://shellbox.dev/) | agent-sandbox | 0.0200 | 14.40 | `shellbox` |
| 8 | [UpCloud](https://upcloud.com/pricing/) | hyperscaler | 0.0208 | 15.00 | `upcloud` |
| 9 | [Zeabur](https://zeabur.com/pricing) | paas | 0.0055 | 8.95 | `zeabur` |
| 10 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | hyperscaler | 0.0230 | 16.54 | `scaleway` |
| 11 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | gpu-cloud | 0.0240 | 17.28 | `verda` |
| 12 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | hyperscaler | 0.0298 | 21.46 | `vultr` |
| 13 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | hyperscaler | 0.0312 | 22.46 | `ubicloud` |
| 14 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | hyperscaler | 0.0335 | 24.15 | `hostinger-vps` |
| 15 | [Fly.io Machines](https://fly.io/pricing) | paas | 0.0353 | 25.40 | `fly-machines` |
| 16 | [Nebius](https://docs.nebius.com/compute/resources/pricing) | gpu-cloud | 0.0368 | 26.50 | `nebius` |
| 17 | [Hugging Face Jobs (hf-sandbox backend)](https://huggingface.co/docs/hub/en/jobs-pricing) | paas | 0.0100 | 16.20 | `huggingface-jobs` |
| 18 | [Manus Cloud Computer](https://help.manus.im/en/articles/15392078-understanding-cloud-computer-plans-and-billing) | agent-sandbox | 0.0411 | 29.59 | `manus-cloud-computer` |
| 19 | [E2E Networks](https://www.e2enetworks.com/pricing) | hyperscaler | 0.0440 | 31.68 | `e2e-networks` |
| 20 | [tama](https://tama.computer/) | agent-sandbox | 0.0454 | 32.70 | `tama` |
| 21 | [Exoscale](https://www.exoscale.com/pricing/) | hyperscaler | 0.0467 | 33.60 | `exoscale` |
| 22 | [HostMyApple](https://hostmyapple.com/mac-vps-hosting) | macos | 0.0479 | 34.51 | `hostmyapple` |
| 23 | [STACKIT Compute Engine](https://pim.api.stackit.cloud/v1/skus) | hyperscaler | 0.0493 | 35.46 | `stackit` |
| 24 | [Windows 365 Cloud PC (Business / Enterprise)](https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing) | windows | 0.0493 | 35.51 | `windows-365` |
| 25 | [Claude Managed Agents](https://platform.claude.com/docs/en/about-claude/pricing#claude-managed-agents-pricing) | agent-sandbox | 0.0500 | 36.00 | `claude-managed-agents` |
| 26 | [Jarvislabs](https://jarvislabs.ai/pricing) | gpu-cloud | 0.0500 | 36.00 | `jarvislabs` |
| 27 | [Mosaic Sandbox](https://sandbox.mosaicos.com/) | agent-sandbox | 0.0500 | 36.00 | `mosaic` |
| 28 | [machine0](https://machine0.io/) | agent-sandbox | 0.0520 | 37.44 | `machine0` |
| 29 | [Alibaba Cloud Agent Sandbox / FC / AgentRun](https://help.aliyun.com/zh/agent-sandbox/product-overview/billing-overview) | agent-sandbox | 0.0549 | 39.55 | `alibaba-agentrun` |
| 30 | [Celesto Cloud](https://celesto.ai/pricing) | agent-sandbox | 0.0600 | 43.20 | `celesto` |
| 31 | [Runpod](https://www.runpod.io/pricing) | gpu-cloud | 0.0600 | 43.20 | `runpod` |
| 32 | [Sandbox0](https://sandbox0.ai/pricing) | agent-sandbox | 0.0600 | 43.20 | `sandbox0` |
| 33 | [PPIO Agent Sandbox](https://ppio.com/docs/sandbox/pricing.md) | agent-sandbox | 0.0644 | 46.35 | `ppio-sandbox` |
| 34 | [Volcano Engine AgentKit / veFaaS sandbox](https://docs.volcengine.com/docs/agentkit/Billing_items?lang=zh) | agent-sandbox | 0.0653 | 47.05 | `volcengine-agentkit` |
| 35 | [Paperspace](https://docs.digitalocean.com/products/paperspace/pricing/) | gpu-cloud | 0.0400 | 36.80 | `paperspace` |
| 36 | [Northflank Sandboxes](https://northflank.com/pricing) | agent-sandbox | 0.0667 | 48.02 | `northflank` |
| 37 | [AWS CodeBuild](https://aws.amazon.com/codebuild/pricing/) | paas | 0.0720 | 51.84 | `aws-codebuild` |
| 38 | [Vultr Cloud Compute (Windows Server)](https://docs.vultr.com/support/platform/billing/is-a-windows-license-included-in-the-monthly-price) | windows | 0.0774 | 55.71 | `vultr-windows` |
| 39 | [Crusoe](https://www.crusoe.ai/cloud/pricing) | gpu-cloud | 0.0800 | 57.60 | `crusoe` |
| 40 | [Runtime (withruntime.com)](https://withruntime.com/pricing) | agent-sandbox | 0.0800 | 57.60 | `withruntime` |
| 41 | [MacinCloud](https://www.macincloud.com/pages/dedicated.html) | macos | 0.0808 | 58.19 | `macincloud` |
| 42 | [Red Hat OpenShift (Harbor backend)](https://www.redhat.com/en/technologies/cloud-computing/openshift/pricing) | paas | 0.0855 | 61.56 | `openshift` |
| 43 | [Prime Intellect Sandboxes](https://www.primeintellect.ai/sandboxes) | agent-sandbox | 0.0900 | 64.80 | `prime-intellect` |
| 44 | [Clever Cloud](https://www.clever.cloud/pricing/) | paas | 0.0918 | 66.12 | `clever-cloud` |
| 45 | [Green Mini host](https://portal.greenmini.host/checkout/order) | macos | 0.0946 | 68.08 | `greenmini` |
| 46 | [Baseten](https://docs.baseten.co/deployment/resources) | gpu-cloud | 0.1038 | 74.74 | `baseten` |
| 47 | [exe.dev](https://exe.dev/pricing) | dev-env | 0.1050 | 75.60 | `exe-dev` |
| 48 | [Hetzner Dedicated AX / EX](https://www.hetzner.com/dedicated-rootserver/) | hyperscaler | 0.1075 | 77.40 | `hetzner-dedicated` |
| 49 | [OakHost](https://www.oakhost.com/mac-mini-hosting) | macos | 0.1122 | 80.78 | `oakhost` |
| 50 | [Scaleway Apple silicon (Mac mini)](https://www.scaleway.com/en/pricing/apple-silicon/) | macos | 0.1202 | 86.55 | `scaleway-apple-silicon` |
| 51 | [Koyeb Sandboxes](https://www.koyeb.com/pricing) | agent-sandbox | 0.0288 | 49.74 | `koyeb` |
| 52 | [Collimate](https://collimate.ai/pricing) | agent-sandbox | 0.1280 | 92.16 | `collimate` |
| 53 | [Sakura Internet Cloud](https://cloud.sakura.ad.jp/products/server/) | hyperscaler | 0.1333 | 95.96 | `sakura-cloud` |
| 54 | [Tencent Cloud Agent Runtime — Agent Sandbox](https://cloud.tencent.com/document/product/1814/133249) | agent-sandbox | 0.1406 | 101.20 | `tencent-agent-runtime` |
| 55 | [NAVER Cloud / LINE-NAVER scope](https://www.ncloud.com/product/compute/server) | hyperscaler | 0.1414 | 101.80 | `naver-cloud` |
| 56 | [RentaMac (rentamac.io)](https://rentamac.io/pricing) | macos | 0.1459 | 105.04 | `rentamac` |
| 57 | [Solari](https://docs.getsolari.com/pricing) | agent-sandbox | 0.0798 | 77.46 | `solari` |
| 58 | [Together Code Sandbox](https://www.together.ai/pricing) | agent-sandbox | 0.1488 | 107.14 | `together-code-sandbox` |
| 59 | [MacStadium](https://www.macstadium.com/pricing) | macos | 0.1493 | 107.51 | `macstadium` |
| 60 | [Omnara](https://www.omnara.com/pricing) | agent-sandbox | 0.1656 | 119.23 | `omnara` |

_56 more in `data/period-model.json`._

**The trap in this section.** A one-time credit is free once. A monthly credit is free until it runs out, and the largest in the market is $30/month. The big numbers people quote — $300 from Google, AWS, Azure, Oracle or IBM — are **one-time** credits. They do not renew, and treating one as a free tier is the most expensive mistake in this document.

---

## B. Paid providers by period

Cheapest first within each cell. `$/h` is the published machine rate; the period columns are that rate times the hours you hold it, before any floor.

### 1 vCPU / 1 GiB — tiny

#### 1h per day — 206 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0007 | 0.00 | 0.00 | 0.02 | 0.02 | - | 1.00 | - | yes | `scaleway` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0021 | 0.00 | 0.01 | 0.06 | 0.06 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0031 | 0.00 | 0.02 | 0.09 | 0.09 | - | 1.00 | - | yes | `oracle-cloud` |
| 4 | [UpCloud](https://upcloud.com/pricing/) | 0.0052 | 0.01 | 0.04 | 0.16 | 0.16 | - | 1.00 | - | yes | `upcloud` |
| 5 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0055 | 0.01 | 0.04 | 0.16 | 0.16 | - | 1.00 | - | yes | `kamatera` |
| 6 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0066 | 0.01 | 0.05 | 0.20 | 0.20 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 7 | [zipbox](https://zipbox.ai/pricing) | 0.0068 | 0.01 | 0.05 | 0.20 | 0.20 | - | 1.00 | - | yes | `zipbox` |
| 8 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0074 | 0.01 | 0.05 | 0.22 | 0.22 | - | 1.00 | - | yes | `vultr` |
| 9 | [Civo Compute](https://www.civo.com/pricing) | 0.0074 | 0.01 | 0.05 | 0.22 | 0.22 | - | 1.00 | - | yes | `civo` |
| 10 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0075 | 0.01 | 0.05 | 0.23 | 0.23 | - | 1.00 | - | yes | `linode` |
| 11 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0079 | 0.01 | 0.06 | 0.24 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 12 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0080 | 0.01 | 0.06 | 0.24 | 0.24 | - | 1.00 | - | yes | `ionos` |
| 13 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0082 | 0.01 | 0.06 | 0.25 | 0.25 | - | 1.00 | - | yes | `kakao-cloud` |
| 14 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | 0.0089 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `digitalocean` |
| 15 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | **disputed** | `lizard` |
| 16 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `contabo` |
| 17 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0091 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `gcore` |
| 18 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.01 | 0.07 | 0.31 | 0.31 | - | 1.00 | - | yes | `hetzner-cloud` |
| 19 | [Moonshot Kimi Hosted Agents sandbox](https://platform.kimi.com/docs/pricing/hosted-agents.md) | 0.0107 | 0.01 | 0.08 | 0.32 | 0.32 | - | 1.00 | - | **no** | `moonshot-kimi` |
| 20 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.01 | 0.08 | 0.33 | 0.33 | - | 1.00 | - | yes | `upstash-box` |
| 21 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.01 | 0.08 | 0.35 | 0.35 | - | 1.00 | - | yes | `netcup` |
| 22 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0120 | 0.01 | 0.08 | 0.36 | 0.36 | - | 1.00 | - | yes | `verda` |
| 23 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0129 | 0.01 | 0.09 | 0.39 | 0.39 | - | 1.00 | - | yes | `ovhcloud` |
| 24 | [machine0](https://machine0.io/) | 0.0130 | 0.01 | 0.09 | 0.39 | 0.39 | - | 1.00 | - | yes | `machine0` |
| 25 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0141 | 0.01 | 0.10 | 0.42 | 0.42 | - | 1.00 | - | yes | `alibaba-ecs` |

_181 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 4h per day — 206 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0007 | 0.00 | 0.02 | 0.08 | 0.08 | - | 1.00 | - | yes | `scaleway` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0021 | 0.01 | 0.06 | 0.25 | 0.25 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0031 | 0.01 | 0.09 | 0.37 | 0.37 | - | 1.00 | - | yes | `oracle-cloud` |
| 4 | [UpCloud](https://upcloud.com/pricing/) | 0.0052 | 0.02 | 0.15 | 0.62 | 0.62 | - | 1.00 | - | yes | `upcloud` |
| 5 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0055 | 0.02 | 0.15 | 0.66 | 0.66 | - | 1.00 | - | yes | `kamatera` |
| 6 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0066 | 0.03 | 0.18 | 0.79 | 0.79 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 7 | [zipbox](https://zipbox.ai/pricing) | 0.0068 | 0.03 | 0.19 | 0.82 | 0.82 | - | 1.00 | - | yes | `zipbox` |
| 8 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0074 | 0.03 | 0.21 | 0.89 | 0.89 | - | 1.00 | - | yes | `vultr` |
| 9 | [Civo Compute](https://www.civo.com/pricing) | 0.0074 | 0.03 | 0.21 | 0.89 | 0.89 | - | 1.00 | - | yes | `civo` |
| 10 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0075 | 0.03 | 0.21 | 0.90 | 0.90 | - | 1.00 | - | yes | `linode` |
| 11 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0079 | 0.03 | 0.22 | 0.95 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 12 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0080 | 0.03 | 0.22 | 0.96 | 0.96 | - | 1.00 | - | yes | `ionos` |
| 13 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0082 | 0.03 | 0.23 | 0.98 | 0.98 | - | 1.00 | - | yes | `kakao-cloud` |
| 14 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | 0.0089 | 0.04 | 0.25 | 1.07 | 1.07 | - | 1.00 | - | yes | `digitalocean` |
| 15 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.04 | 0.25 | 1.08 | 1.08 | - | 1.00 | - | **disputed** | `lizard` |
| 16 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.04 | 0.25 | 1.08 | 1.08 | - | 1.00 | - | yes | `contabo` |
| 17 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0091 | 0.04 | 0.25 | 1.09 | 1.09 | - | 1.00 | - | yes | `gcore` |
| 18 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.04 | 0.29 | 1.25 | 1.25 | - | 1.00 | - | yes | `hetzner-cloud` |
| 19 | [Moonshot Kimi Hosted Agents sandbox](https://platform.kimi.com/docs/pricing/hosted-agents.md) | 0.0107 | 0.04 | 0.30 | 1.29 | 1.29 | - | 1.00 | - | **no** | `moonshot-kimi` |
| 20 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.04 | 0.31 | 1.32 | 1.32 | - | 1.00 | - | yes | `upstash-box` |
| 21 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.05 | 0.33 | 1.40 | 1.40 | - | 1.00 | - | yes | `netcup` |
| 22 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0120 | 0.05 | 0.34 | 1.44 | 1.44 | - | 1.00 | - | yes | `verda` |
| 23 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0129 | 0.05 | 0.36 | 1.55 | 1.55 | - | 1.00 | - | yes | `ovhcloud` |
| 24 | [machine0](https://machine0.io/) | 0.0130 | 0.05 | 0.36 | 1.56 | 1.56 | - | 1.00 | - | yes | `machine0` |
| 25 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0141 | 0.06 | 0.39 | 1.69 | 1.69 | - | 1.00 | - | yes | `alibaba-ecs` |

_181 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 10h per day — 206 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0007 | 0.01 | 0.05 | 0.20 | 0.20 | - | 1.00 | - | yes | `scaleway` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0021 | 0.02 | 0.14 | 0.62 | 0.62 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0031 | 0.03 | 0.21 | 0.92 | 0.92 | - | 1.00 | - | yes | `oracle-cloud` |
| 4 | [UpCloud](https://upcloud.com/pricing/) | 0.0052 | 0.05 | 0.36 | 1.56 | 1.56 | - | 1.00 | - | yes | `upcloud` |
| 5 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0055 | 0.05 | 0.38 | 1.64 | 1.64 | - | 1.00 | - | yes | `kamatera` |
| 6 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0066 | 0.07 | 0.46 | 1.97 | 1.97 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 7 | [zipbox](https://zipbox.ai/pricing) | 0.0068 | 0.07 | 0.48 | 2.04 | 2.04 | - | 1.00 | - | yes | `zipbox` |
| 8 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0074 | 0.07 | 0.52 | 2.22 | 2.22 | - | 1.00 | - | yes | `vultr` |
| 9 | [Civo Compute](https://www.civo.com/pricing) | 0.0074 | 0.07 | 0.52 | 2.23 | 2.23 | - | 1.00 | - | yes | `civo` |
| 10 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0075 | 0.07 | 0.53 | 2.25 | 2.25 | - | 1.00 | - | yes | `linode` |
| 11 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0079 | 0.08 | 0.55 | 2.38 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 12 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0080 | 0.08 | 0.56 | 2.39 | 2.39 | - | 1.00 | - | yes | `ionos` |
| 13 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0082 | 0.08 | 0.57 | 2.45 | 2.45 | - | 1.00 | - | yes | `kakao-cloud` |
| 14 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | 0.0089 | 0.09 | 0.63 | 2.68 | 2.68 | - | 1.00 | - | yes | `digitalocean` |
| 15 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.09 | 0.63 | 2.70 | 2.70 | - | 1.00 | - | **disputed** | `lizard` |
| 16 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.09 | 0.63 | 2.71 | 2.71 | - | 1.00 | - | yes | `contabo` |
| 17 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0091 | 0.09 | 0.64 | 2.73 | 2.73 | - | 1.00 | - | yes | `gcore` |
| 18 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.10 | 0.73 | 3.12 | 3.12 | - | 1.00 | - | yes | `hetzner-cloud` |
| 19 | [Moonshot Kimi Hosted Agents sandbox](https://platform.kimi.com/docs/pricing/hosted-agents.md) | 0.0107 | 0.11 | 0.75 | 3.22 | 3.22 | - | 1.00 | - | **no** | `moonshot-kimi` |
| 20 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.11 | 0.77 | 3.29 | 3.29 | - | 1.00 | - | yes | `upstash-box` |
| 21 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.12 | 0.82 | 3.50 | 3.50 | - | 1.00 | - | yes | `netcup` |
| 22 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0120 | 0.12 | 0.84 | 3.60 | 3.60 | - | 1.00 | - | yes | `verda` |
| 23 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0129 | 0.13 | 0.90 | 3.87 | 3.87 | - | 1.00 | - | yes | `ovhcloud` |
| 24 | [machine0](https://machine0.io/) | 0.0130 | 0.13 | 0.91 | 3.90 | 3.90 | - | 1.00 | - | yes | `machine0` |
| 25 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0141 | 0.14 | 0.99 | 4.23 | 4.23 | - | 1.00 | - | yes | `alibaba-ecs` |

_181 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 24h per day — 206 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0007 | 0.02 | 0.11 | 0.49 | 0.49 | - | 1.00 | - | yes | `scaleway` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0021 | 0.05 | 0.35 | 1.48 | 1.48 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0031 | 0.07 | 0.51 | 2.21 | 2.21 | - | 1.00 | - | yes | `oracle-cloud` |
| 4 | [UpCloud](https://upcloud.com/pricing/) | 0.0052 | 0.12 | 0.88 | 3.75 | 3.75 | - | 1.00 | - | yes | `upcloud` |
| 5 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0055 | 0.13 | 0.92 | 3.95 | 3.95 | - | 1.00 | - | yes | `kamatera` |
| 6 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0066 | 0.16 | 1.10 | 4.72 | 4.72 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 7 | [zipbox](https://zipbox.ai/pricing) | 0.0068 | 0.16 | 1.14 | 4.90 | 4.90 | - | 1.00 | - | yes | `zipbox` |
| 8 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0074 | 0.18 | 1.24 | 5.33 | 5.33 | - | 1.00 | - | yes | `vultr` |
| 9 | [Civo Compute](https://www.civo.com/pricing) | 0.0074 | 0.18 | 1.25 | 5.36 | 5.36 | - | 1.00 | - | yes | `civo` |
| 10 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0075 | 0.18 | 1.26 | 5.40 | 5.40 | - | 1.00 | - | yes | `linode` |
| 11 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0079 | 0.19 | 1.33 | 5.70 | 0.48 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 12 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0080 | 0.19 | 1.34 | 5.73 | 5.73 | - | 1.00 | - | yes | `ionos` |
| 13 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0082 | 0.20 | 1.37 | 5.89 | 5.89 | - | 1.00 | - | yes | `kakao-cloud` |
| 14 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | 0.0089 | 0.21 | 1.50 | 6.43 | 6.43 | - | 1.00 | - | yes | `digitalocean` |
| 15 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.22 | 1.51 | 6.48 | 6.48 | - | 1.00 | - | **disputed** | `lizard` |
| 16 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.22 | 1.52 | 6.51 | 6.51 | - | 1.00 | - | yes | `contabo` |
| 17 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0091 | 0.22 | 1.53 | 6.55 | 6.55 | - | 1.00 | - | yes | `gcore` |
| 18 | [Fly.io Machines](https://fly.io/pricing) | 0.0093 | 0.22 | 1.56 | 6.70 | 6.70 | - | 1.00 | $5 | yes | `fly-machines` |
| 19 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.25 | 1.75 | 7.49 | 7.49 | - | 1.00 | - | yes | `hetzner-cloud` |
| 20 | [Moonshot Kimi Hosted Agents sandbox](https://platform.kimi.com/docs/pricing/hosted-agents.md) | 0.0107 | 0.26 | 1.80 | 7.73 | 7.73 | - | 1.00 | - | **no** | `moonshot-kimi` |
| 21 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.26 | 1.84 | 7.89 | 7.89 | - | 1.00 | - | yes | `upstash-box` |
| 22 | [Zeabur](https://zeabur.com/pricing) | 0.0041 | 0.10 | 0.69 | 7.96 | 7.96 | - | 1.00 | - | **no** | `zeabur` |
| 23 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.28 | 1.96 | 8.39 | 8.39 | - | 1.00 | - | yes | `netcup` |
| 24 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0120 | 0.29 | 2.02 | 8.64 | 8.64 | - | 1.00 | - | yes | `verda` |
| 25 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0129 | 0.31 | 2.17 | 9.29 | 9.29 | - | 1.00 | - | yes | `ovhcloud` |

_181 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

### 2 vCPU / 4 GiB — agent

#### 1h per day — 202 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 0.01 | 0.04 | 0.18 | 0.18 | - | 1.00 | - | yes | `agent-37` |
| 2 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | **disputed** | `lizard` |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `contabo` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.01 | 0.07 | 0.31 | 0.31 | - | 1.00 | - | yes | `hetzner-cloud` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.01 | 0.08 | 0.33 | 0.33 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.01 | 0.08 | 0.35 | 0.35 | - | 1.00 | - | yes | `netcup` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 0.01 | 0.10 | 0.41 | 0.41 | - | 1.00 | - | yes | `zipbox` |
| 9 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 0.01 | 0.10 | 0.44 | 0.44 | - | 1.00 | - | yes | `ionos` |
| 10 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0178 | 0.02 | 0.12 | 0.53 | 0.53 | - | 1.00 | - | yes | `alibaba-ecs` |
| 11 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0193 | 0.02 | 0.14 | 0.58 | 0.58 | - | 1.00 | - | yes | `gcore` |
| 12 | [shellbox](https://shellbox.dev/) | 0.0200 | 0.02 | 0.14 | 0.60 | 0.60 | - | 1.00 | - | yes | `shellbox` |
| 13 | [UpCloud](https://upcloud.com/pricing/) | 0.0208 | 0.02 | 0.15 | 0.62 | 0.62 | - | 1.00 | - | yes | `upcloud` |
| 14 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0230 | 0.02 | 0.16 | 0.69 | 0.69 | - | 1.00 | - | yes | `scaleway` |
| 15 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0240 | 0.02 | 0.17 | 0.72 | 0.72 | - | 1.00 | - | yes | `verda` |
| 16 | [Cube Computer](https://cube.computer/) | 0.0247 | 0.02 | 0.17 | 0.74 | 0.74 | - | 1.00 | - | **no** | `cube` |
| 17 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0256 | 0.03 | 0.18 | 0.77 | 0.77 | - | 1.00 | - | yes | `ovhcloud` |
| 18 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0274 | 0.03 | 0.19 | 0.82 | 0.82 | - | 1.00 | - | yes | `kamatera` |
| 19 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0297 | 0.03 | 0.21 | 0.89 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 20 | [Civo Compute](https://www.civo.com/pricing) | 0.0298 | 0.03 | 0.21 | 0.89 | 0.89 | - | 1.00 | - | yes | `civo` |
| 21 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0298 | 0.03 | 0.21 | 0.89 | 0.89 | - | 1.00 | - | yes | `vultr` |
| 22 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | 0.0312 | 0.03 | 0.22 | 0.94 | 0.94 | - | 1.00 | - | yes | `ubicloud` |
| 23 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0326 | 0.03 | 0.23 | 0.98 | 0.98 | - | 1.00 | - | yes | `kakao-cloud` |
| 24 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0328 | 0.03 | 0.23 | 0.98 | 0.98 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 25 | [Google Compute Engine (Windows Server)](https://cloud.google.com/compute/disks-image-pricing#windows_server_pricing) | 0.0335 | 0.03 | 0.23 | 1.01 | 1.01 | - | 1.00 | - | yes | `gcp-windows` |

_177 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 4h per day — 202 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 0.02 | 0.17 | 0.72 | 0.72 | - | 1.00 | - | yes | `agent-37` |
| 2 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.04 | 0.25 | 1.08 | 1.08 | - | 1.00 | - | **disputed** | `lizard` |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.04 | 0.25 | 1.08 | 1.08 | - | 1.00 | - | yes | `contabo` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 0.04 | 0.26 | 1.09 | 1.09 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.04 | 0.29 | 1.25 | 1.25 | - | 1.00 | - | yes | `hetzner-cloud` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.04 | 0.31 | 1.32 | 1.32 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.05 | 0.33 | 1.40 | 1.40 | - | 1.00 | - | yes | `netcup` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 0.05 | 0.38 | 1.64 | 1.64 | - | 1.00 | - | yes | `zipbox` |
| 9 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 0.06 | 0.41 | 1.77 | 1.77 | - | 1.00 | - | yes | `ionos` |
| 10 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0178 | 0.07 | 0.50 | 2.13 | 2.13 | - | 1.00 | - | yes | `alibaba-ecs` |
| 11 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0193 | 0.08 | 0.54 | 2.32 | 2.32 | - | 1.00 | - | yes | `gcore` |
| 12 | [shellbox](https://shellbox.dev/) | 0.0200 | 0.08 | 0.56 | 2.40 | 2.40 | - | 1.00 | - | yes | `shellbox` |
| 13 | [UpCloud](https://upcloud.com/pricing/) | 0.0208 | 0.08 | 0.58 | 2.50 | 2.50 | - | 1.00 | - | yes | `upcloud` |
| 14 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0230 | 0.09 | 0.64 | 2.76 | 2.76 | - | 1.00 | - | yes | `scaleway` |
| 15 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0240 | 0.10 | 0.67 | 2.88 | 2.88 | - | 1.00 | - | yes | `verda` |
| 16 | [Cube Computer](https://cube.computer/) | 0.0247 | 0.10 | 0.69 | 2.97 | 2.97 | - | 1.00 | - | **no** | `cube` |
| 17 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0256 | 0.10 | 0.72 | 3.07 | 3.07 | - | 1.00 | - | yes | `ovhcloud` |
| 18 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0274 | 0.11 | 0.77 | 3.29 | 3.29 | - | 1.00 | - | yes | `kamatera` |
| 19 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0297 | 0.12 | 0.83 | 3.57 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 20 | [Civo Compute](https://www.civo.com/pricing) | 0.0298 | 0.12 | 0.83 | 3.57 | 3.57 | - | 1.00 | - | yes | `civo` |
| 21 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0298 | 0.12 | 0.83 | 3.58 | 3.58 | - | 1.00 | - | yes | `vultr` |
| 22 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | 0.0312 | 0.12 | 0.87 | 3.74 | 3.74 | - | 1.00 | - | yes | `ubicloud` |
| 23 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0326 | 0.13 | 0.91 | 3.91 | 3.91 | - | 1.00 | - | yes | `kakao-cloud` |
| 24 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0328 | 0.13 | 0.92 | 3.93 | 3.93 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 25 | [Google Compute Engine (Windows Server)](https://cloud.google.com/compute/disks-image-pricing#windows_server_pricing) | 0.0335 | 0.13 | 0.94 | 4.02 | 4.02 | - | 1.00 | - | yes | `gcp-windows` |

_177 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 10h per day — 202 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 0.06 | 0.42 | 1.81 | 1.81 | - | 1.00 | - | yes | `agent-37` |
| 2 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.09 | 0.63 | 2.70 | 2.70 | - | 1.00 | - | **disputed** | `lizard` |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.09 | 0.63 | 2.71 | 2.71 | - | 1.00 | - | yes | `contabo` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 0.09 | 0.64 | 2.74 | 2.74 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.10 | 0.73 | 3.12 | 3.12 | - | 1.00 | - | yes | `hetzner-cloud` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.11 | 0.77 | 3.29 | 3.29 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.12 | 0.82 | 3.50 | 3.50 | - | 1.00 | - | yes | `netcup` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 0.14 | 0.96 | 4.11 | 4.11 | - | 1.00 | - | yes | `zipbox` |
| 9 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 0.15 | 1.04 | 4.44 | 4.44 | - | 1.00 | - | yes | `ionos` |
| 10 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0178 | 0.18 | 1.24 | 5.33 | 5.33 | - | 1.00 | - | yes | `alibaba-ecs` |
| 11 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0193 | 0.19 | 1.35 | 5.80 | 5.80 | - | 1.00 | - | yes | `gcore` |
| 12 | [shellbox](https://shellbox.dev/) | 0.0200 | 0.20 | 1.40 | 6.00 | 6.00 | - | 1.00 | - | yes | `shellbox` |
| 13 | [UpCloud](https://upcloud.com/pricing/) | 0.0208 | 0.21 | 1.46 | 6.25 | 6.25 | - | 1.00 | - | yes | `upcloud` |
| 14 | [Zeabur](https://zeabur.com/pricing) | 0.0055 | 0.05 | 0.38 | 6.64 | 6.64 | - | 1.00 | - | **no** | `zeabur` |
| 15 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0230 | 0.23 | 1.61 | 6.89 | 6.89 | - | 1.00 | - | yes | `scaleway` |
| 16 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0240 | 0.24 | 1.68 | 7.20 | 7.20 | - | 1.00 | - | yes | `verda` |
| 17 | [Cube Computer](https://cube.computer/) | 0.0247 | 0.25 | 1.73 | 7.42 | 7.42 | - | 1.00 | - | **no** | `cube` |
| 18 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0256 | 0.26 | 1.79 | 7.68 | 7.68 | - | 1.00 | - | yes | `ovhcloud` |
| 19 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0274 | 0.27 | 1.92 | 8.22 | 8.22 | - | 1.00 | - | yes | `kamatera` |
| 20 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0297 | 0.30 | 2.08 | 8.92 | 3.70 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 21 | [Civo Compute](https://www.civo.com/pricing) | 0.0298 | 0.30 | 2.08 | 8.93 | 8.93 | - | 1.00 | - | yes | `civo` |
| 22 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0298 | 0.30 | 2.09 | 8.94 | 8.94 | - | 1.00 | - | yes | `vultr` |
| 23 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | 0.0312 | 0.31 | 2.18 | 9.36 | 9.36 | - | 1.00 | - | yes | `ubicloud` |
| 24 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | 0.0326 | 0.33 | 2.28 | 9.77 | 9.77 | - | 1.00 | - | yes | `kakao-cloud` |
| 25 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0328 | 0.33 | 2.29 | 9.83 | 9.83 | - | 1.00 | - | yes | `ibm-cloud-vpc` |

_177 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

#### 24h per day — 202 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | 0.0060 | 0.14 | 1.01 | 4.34 | 4.34 | - | 1.00 | - | yes | `agent-37` |
| 2 | [Lizard](https://lizard.build/pricing) | 0.0090 | 0.22 | 1.51 | 6.48 | 6.48 | - | 1.00 | - | **disputed** | `lizard` |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.22 | 1.52 | 6.51 | 6.51 | - | 1.00 | - | yes | `contabo` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0091 | 0.22 | 1.53 | 6.57 | 6.57 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | 0.25 | 1.75 | 7.49 | 7.49 | - | 1.00 | - | yes | `hetzner-cloud` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0110 | 0.26 | 1.84 | 7.89 | 7.89 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | 0.28 | 1.96 | 8.39 | 8.39 | - | 1.00 | - | yes | `netcup` |
| 8 | [Zeabur](https://zeabur.com/pricing) | 0.0055 | 0.13 | 0.92 | 8.95 | 8.95 | - | 1.00 | - | **no** | `zeabur` |
| 9 | [zipbox](https://zipbox.ai/pricing) | 0.0137 | 0.33 | 2.30 | 9.86 | 9.86 | - | 1.00 | - | yes | `zipbox` |
| 10 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0148 | 0.35 | 2.48 | 10.65 | 10.65 | - | 1.00 | - | yes | `ionos` |
| 11 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0178 | 0.43 | 2.98 | 12.78 | 12.78 | - | 1.00 | - | yes | `alibaba-ecs` |
| 12 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0193 | 0.46 | 3.25 | 13.92 | 13.92 | - | 1.00 | - | yes | `gcore` |
| 13 | [shellbox](https://shellbox.dev/) | 0.0200 | 0.48 | 3.36 | 14.40 | 14.40 | - | 1.00 | - | yes | `shellbox` |
| 14 | [UpCloud](https://upcloud.com/pricing/) | 0.0208 | 0.50 | 3.50 | 15.00 | 15.00 | - | 1.00 | - | yes | `upcloud` |
| 15 | [Hugging Face Jobs (hf-sandbox backend)](https://huggingface.co/docs/hub/en/jobs-pricing) | 0.0100 | 0.24 | 1.68 | 16.20 | 16.20 | - | 1.00 | - | **no** | `huggingface-jobs` |
| 16 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0230 | 0.55 | 3.86 | 16.54 | 16.54 | - | 1.00 | - | yes | `scaleway` |
| 17 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0240 | 0.58 | 4.03 | 17.28 | 17.28 | - | 1.00 | - | yes | `verda` |
| 18 | [Cube Computer](https://cube.computer/) | 0.0247 | 0.59 | 4.16 | 17.81 | 17.81 | - | 1.00 | - | **no** | `cube` |
| 19 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0256 | 0.61 | 4.30 | 18.43 | 18.43 | - | 1.00 | - | yes | `ovhcloud` |
| 20 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0274 | 0.66 | 4.60 | 19.73 | 19.73 | - | 1.00 | - | yes | `kamatera` |
| 21 | [boat.dev](https://docs.boat.dev/pricing) | 0.0180 | 0.43 | 3.02 | 20.00 | 20.00 | - | 1.00 | $20 | yes | `boat` |
| 22 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0297 | 0.71 | 5.00 | 21.41 | 16.19 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 23 | [Civo Compute](https://www.civo.com/pricing) | 0.0298 | 0.71 | 5.00 | 21.43 | 21.43 | - | 1.00 | - | yes | `civo` |
| 24 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0298 | 0.72 | 5.01 | 21.46 | 21.46 | - | 1.00 | - | yes | `vultr` |
| 25 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | 0.0312 | 0.75 | 5.24 | 22.46 | 22.46 | - | 1.00 | - | yes | `ubicloud` |

_177 more at this duty cycle; the full rank is table C._

**Rows marked `disputed` are not confirmed prices.** A size the vendor advertises is missing from the corpus card, so the rate here is the vendor's own and the corpus discarded it:

- **Lizard** — Small (2 vCPU / 4 GB RAM) at $0.009/h, advertised on [Lizard](https://lizard.build/pricing): "Small (2 vCPU, 4 GB RAM) at $0.009/hour, Medium (4 vCPU, 8 GB RAM) at $0.018/hour, and Large (8 vCPU, 16 GB RAM) at $0.036/hour. Medium is the default." The card carries only the default size, so the rate was absent from the ranking. Conflict: lizard.build/docs says create options do not change the limits (4 vCPU / 4096 MiB) and gives Medium 4096 MiB rather than 8 GB; the pricing page and the docs disagree and no changelog dates either

### 4 vCPU / 8 GiB — devbox

#### 1h per day — 197 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.01 | 0.06 | 0.27 | 0.27 | - | 1.00 | - | yes | `contabo` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0121 | 0.01 | 0.08 | 0.36 | 0.36 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0160 | 0.02 | 0.11 | 0.48 | 0.48 | - | 1.00 | - | yes | `hetzner-cloud` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0182 | 0.02 | 0.13 | 0.55 | 0.55 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0211 | 0.02 | 0.15 | 0.63 | 0.63 | - | 1.00 | - | yes | `netcup` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0219 | 0.02 | 0.15 | 0.66 | 0.66 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0273 | 0.03 | 0.19 | 0.82 | 0.82 | - | 1.00 | - | yes | `ionos` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0274 | 0.03 | 0.19 | 0.82 | 0.82 | - | 1.00 | - | yes | `zipbox` |
| 9 | [UpCloud](https://upcloud.com/pricing/) | 0.0357 | 0.04 | 0.25 | 1.07 | 1.07 | - | 1.00 | - | yes | `upcloud` |
| 10 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0387 | 0.04 | 0.27 | 1.16 | 1.16 | - | 1.00 | - | yes | `gcore` |
| 11 | [shellbox](https://shellbox.dev/) | 0.0400 | 0.04 | 0.28 | 1.20 | 1.20 | - | 1.00 | - | yes | `shellbox` |
| 12 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0461 | 0.05 | 0.32 | 1.38 | 1.38 | - | 1.00 | - | yes | `ovhcloud` |
| 13 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0480 | 0.05 | 0.34 | 1.44 | 1.44 | - | 1.00 | - | yes | `verda` |
| 14 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0487 | 0.05 | 0.34 | 1.46 | 1.46 | - | 1.00 | - | yes | `scaleway` |
| 15 | [E2E Networks](https://www.e2enetworks.com/pricing) | 0.0490 | 0.05 | 0.34 | 1.47 | 1.47 | - | 1.00 | - | yes | `e2e-networks` |
| 16 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0528 | 0.05 | 0.37 | 1.58 | 1.58 | - | 1.00 | - | yes | `alibaba-ecs` |
| 17 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0548 | 0.05 | 0.38 | 1.64 | 1.64 | - | 1.00 | - | yes | `kamatera` |
| 18 | [Cube Computer](https://cube.computer/) | 0.0560 | 0.06 | 0.39 | 1.68 | 1.68 | - | 1.00 | - | **no** | `cube` |
| 19 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | 0.0589 | 0.06 | 0.41 | 1.77 | 1.77 | - | 1.00 | - | yes | `hostinger-vps` |
| 20 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0595 | 0.06 | 0.42 | 1.78 | 0.00 | **$5.22 covers it** | 1.00 | - | yes | `google-cloud-run` |
| 21 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0595 | 0.06 | 0.42 | 1.78 | 1.78 | - | 1.00 | - | yes | `vultr` |
| 22 | [Civo Compute](https://www.civo.com/pricing) | 0.0595 | 0.06 | 0.42 | 1.79 | 1.79 | - | 1.00 | - | yes | `civo` |
| 23 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0655 | 0.07 | 0.46 | 1.97 | 1.97 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 24 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | 0.0714 | 0.07 | 0.50 | 2.14 | 2.14 | - | 1.00 | - | yes | `digitalocean` |
| 25 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0720 | 0.07 | 0.50 | 2.16 | 2.16 | - | 1.00 | - | yes | `linode` |

_172 more at this duty cycle; the full rank is table C._

#### 4h per day — 197 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.04 | 0.25 | 1.08 | 1.08 | - | 1.00 | - | yes | `contabo` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0121 | 0.05 | 0.34 | 1.45 | 1.45 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0160 | 0.06 | 0.45 | 1.92 | 1.92 | - | 1.00 | - | yes | `hetzner-cloud` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0182 | 0.07 | 0.51 | 2.19 | 2.19 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0211 | 0.08 | 0.59 | 2.53 | 2.53 | - | 1.00 | - | yes | `netcup` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0219 | 0.09 | 0.61 | 2.63 | 2.63 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0273 | 0.11 | 0.76 | 3.28 | 3.28 | - | 1.00 | - | yes | `ionos` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0274 | 0.11 | 0.77 | 3.29 | 3.29 | - | 1.00 | - | yes | `zipbox` |
| 9 | [UpCloud](https://upcloud.com/pricing/) | 0.0357 | 0.14 | 1.00 | 4.29 | 4.29 | - | 1.00 | - | yes | `upcloud` |
| 10 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0387 | 0.15 | 1.08 | 4.64 | 4.64 | - | 1.00 | - | yes | `gcore` |
| 11 | [shellbox](https://shellbox.dev/) | 0.0400 | 0.16 | 1.12 | 4.80 | 4.80 | - | 1.00 | - | yes | `shellbox` |
| 12 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0461 | 0.18 | 1.29 | 5.53 | 5.53 | - | 1.00 | - | yes | `ovhcloud` |
| 13 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0480 | 0.19 | 1.34 | 5.76 | 5.76 | - | 1.00 | - | yes | `verda` |
| 14 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0487 | 0.20 | 1.36 | 5.85 | 5.85 | - | 1.00 | - | yes | `scaleway` |
| 15 | [E2E Networks](https://www.e2enetworks.com/pricing) | 0.0490 | 0.20 | 1.37 | 5.88 | 5.88 | - | 1.00 | - | yes | `e2e-networks` |
| 16 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0528 | 0.21 | 1.48 | 6.34 | 6.34 | - | 1.00 | - | yes | `alibaba-ecs` |
| 17 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0548 | 0.22 | 1.53 | 6.58 | 6.58 | - | 1.00 | - | yes | `kamatera` |
| 18 | [Cube Computer](https://cube.computer/) | 0.0560 | 0.22 | 1.57 | 6.72 | 6.72 | - | 1.00 | - | **no** | `cube` |
| 19 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | 0.0589 | 0.24 | 1.65 | 7.07 | 7.07 | - | 1.00 | - | yes | `hostinger-vps` |
| 20 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0595 | 0.24 | 1.67 | 7.14 | 1.92 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 21 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0595 | 0.24 | 1.67 | 7.14 | 7.14 | - | 1.00 | - | yes | `vultr` |
| 22 | [Civo Compute](https://www.civo.com/pricing) | 0.0595 | 0.24 | 1.67 | 7.14 | 7.14 | - | 1.00 | - | yes | `civo` |
| 23 | [Zeabur](https://zeabur.com/pricing) | 0.0233 | 0.09 | 0.65 | 7.79 | 7.79 | - | 1.00 | - | **no** | `zeabur` |
| 24 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0655 | 0.26 | 1.83 | 7.86 | 7.86 | - | 1.00 | - | yes | `ibm-cloud-vpc` |
| 25 | [Fly.io Machines](https://fly.io/pricing) | 0.0706 | 0.28 | 1.98 | 8.47 | 8.47 | - | 1.00 | $5 | yes | `fly-machines` |

_172 more at this duty cycle; the full rank is table C._

#### 10h per day — 197 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.09 | 0.63 | 2.71 | 2.71 | - | 1.00 | - | yes | `contabo` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0121 | 0.12 | 0.84 | 3.62 | 3.62 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0160 | 0.16 | 1.12 | 4.80 | 4.80 | - | 1.00 | - | yes | `hetzner-cloud` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0182 | 0.18 | 1.28 | 5.47 | 5.47 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0211 | 0.21 | 1.47 | 6.32 | 6.32 | - | 1.00 | - | yes | `netcup` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0219 | 0.22 | 1.53 | 6.58 | 6.58 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0273 | 0.27 | 1.91 | 8.19 | 8.19 | - | 1.00 | - | yes | `ionos` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0274 | 0.27 | 1.92 | 8.22 | 8.22 | - | 1.00 | - | yes | `zipbox` |
| 9 | [UpCloud](https://upcloud.com/pricing/) | 0.0357 | 0.36 | 2.50 | 10.71 | 10.71 | - | 1.00 | - | yes | `upcloud` |
| 10 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0387 | 0.39 | 2.71 | 11.61 | 11.61 | - | 1.00 | - | yes | `gcore` |
| 11 | [Zeabur](https://zeabur.com/pricing) | 0.0233 | 0.23 | 1.63 | 11.99 | 11.99 | - | 1.00 | - | **no** | `zeabur` |
| 12 | [shellbox](https://shellbox.dev/) | 0.0400 | 0.40 | 2.80 | 12.00 | 12.00 | - | 1.00 | - | yes | `shellbox` |
| 13 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0461 | 0.46 | 3.23 | 13.83 | 13.83 | - | 1.00 | - | yes | `ovhcloud` |
| 14 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0480 | 0.48 | 3.36 | 14.40 | 14.40 | - | 1.00 | - | yes | `verda` |
| 15 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0487 | 0.49 | 3.41 | 14.62 | 14.62 | - | 1.00 | - | yes | `scaleway` |
| 16 | [E2E Networks](https://www.e2enetworks.com/pricing) | 0.0490 | 0.49 | 3.43 | 14.70 | 14.70 | - | 1.00 | - | yes | `e2e-networks` |
| 17 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0528 | 0.53 | 3.70 | 15.84 | 15.84 | - | 1.00 | - | yes | `alibaba-ecs` |
| 18 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0548 | 0.55 | 3.84 | 16.44 | 16.44 | - | 1.00 | - | yes | `kamatera` |
| 19 | [Cube Computer](https://cube.computer/) | 0.0560 | 0.56 | 3.92 | 16.81 | 16.81 | - | 1.00 | - | **no** | `cube` |
| 20 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | 0.0589 | 0.59 | 4.12 | 17.67 | 17.67 | - | 1.00 | - | yes | `hostinger-vps` |
| 21 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0595 | 0.59 | 4.16 | 17.84 | 12.62 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 22 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0595 | 0.59 | 4.17 | 17.85 | 17.85 | - | 1.00 | - | yes | `vultr` |
| 23 | [Civo Compute](https://www.civo.com/pricing) | 0.0595 | 0.60 | 4.17 | 17.86 | 17.86 | - | 1.00 | - | yes | `civo` |
| 24 | [Hugging Face Jobs (hf-sandbox backend)](https://huggingface.co/docs/hub/en/jobs-pricing) | 0.0300 | 0.30 | 2.10 | 18.00 | 18.00 | - | 1.00 | - | **no** | `huggingface-jobs` |
| 25 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | 0.0655 | 0.66 | 4.58 | 19.65 | 19.65 | - | 1.00 | - | yes | `ibm-cloud-vpc` |

_172 more at this duty cycle; the full rank is table C._

#### 24h per day — 197 paid providers

| # | provider | $/hour | $/day | $/week | $/month | after credit | credit | keep | floor | buy it? | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | 0.22 | 1.52 | 6.51 | 6.51 | - | 1.00 | - | yes | `contabo` |
| 2 | [Agent 37](https://www.agent37.com/pricing) | 0.0121 | 0.29 | 2.03 | 8.68 | 8.68 | - | 1.00 | - | yes | `agent-37` |
| 3 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0160 | 0.38 | 2.69 | 11.52 | 11.52 | - | 1.00 | - | yes | `hetzner-cloud` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | 0.0182 | 0.44 | 3.07 | 13.14 | 13.14 | - | 1.00 | - | yes | `oracle-cloud` |
| 5 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0211 | 0.51 | 3.54 | 15.16 | 15.16 | - | 1.00 | - | yes | `netcup` |
| 6 | [Upstash Box](https://upstash.com/pricing/box) | 0.0219 | 0.53 | 3.68 | 15.78 | 15.78 | - | 1.00 | - | yes | `upstash-box` |
| 7 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | 0.0273 | 0.66 | 4.59 | 19.66 | 19.66 | - | 1.00 | - | yes | `ionos` |
| 8 | [zipbox](https://zipbox.ai/pricing) | 0.0274 | 0.66 | 4.60 | 19.73 | 19.73 | - | 1.00 | - | yes | `zipbox` |
| 9 | [Zeabur](https://zeabur.com/pricing) | 0.0233 | 0.56 | 3.91 | 21.77 | 21.77 | - | 1.00 | - | **no** | `zeabur` |
| 10 | [UpCloud](https://upcloud.com/pricing/) | 0.0357 | 0.86 | 6.00 | 25.71 | 25.71 | - | 1.00 | - | yes | `upcloud` |
| 11 | [boat.dev](https://docs.boat.dev/pricing) | 0.0360 | 0.86 | 6.05 | 25.92 | 25.92 | - | 1.00 | $20 | yes | `boat` |
| 12 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | 0.0387 | 0.93 | 6.50 | 27.86 | 27.86 | - | 1.00 | - | yes | `gcore` |
| 13 | [shellbox](https://shellbox.dev/) | 0.0400 | 0.96 | 6.72 | 28.80 | 28.80 | - | 1.00 | - | yes | `shellbox` |
| 14 | [Hugging Face Jobs (hf-sandbox backend)](https://huggingface.co/docs/hub/en/jobs-pricing) | 0.0300 | 0.72 | 5.04 | 30.60 | 30.60 | - | 1.00 | - | **no** | `huggingface-jobs` |
| 15 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | 0.0461 | 1.11 | 7.74 | 33.19 | 33.19 | - | 1.00 | - | yes | `ovhcloud` |
| 16 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | 0.0480 | 1.15 | 8.06 | 34.56 | 34.56 | - | 1.00 | - | yes | `verda` |
| 17 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | 0.0487 | 1.17 | 8.19 | 35.10 | 35.10 | - | 1.00 | - | yes | `scaleway` |
| 18 | [E2E Networks](https://www.e2enetworks.com/pricing) | 0.0490 | 1.18 | 8.23 | 35.28 | 35.28 | - | 1.00 | - | yes | `e2e-networks` |
| 19 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0528 | 1.27 | 8.87 | 38.01 | 38.01 | - | 1.00 | - | yes | `alibaba-ecs` |
| 20 | [Kamatera](https://www.kamatera.com/pricing/) | 0.0548 | 1.32 | 9.21 | 39.45 | 39.45 | - | 1.00 | - | yes | `kamatera` |
| 21 | [Cube Computer](https://cube.computer/) | 0.0560 | 1.34 | 9.41 | 40.34 | 40.34 | - | 1.00 | - | **no** | `cube` |
| 22 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | 0.0589 | 1.41 | 9.89 | 42.40 | 42.40 | - | 1.00 | - | yes | `hostinger-vps` |
| 23 | [Google Cloud Run](https://cloud.google.com/run/pricing) | 0.0595 | 1.43 | 9.99 | 42.82 | 37.60 | $5.22 of it | 1.00 | - | yes | `google-cloud-run` |
| 24 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | 0.0595 | 1.43 | 10.00 | 42.84 | 42.84 | - | 1.00 | - | yes | `vultr` |
| 25 | [Civo Compute](https://www.civo.com/pricing) | 0.0595 | 1.43 | 10.00 | 42.86 | 42.86 | - | 1.00 | - | yes | `civo` |

_172 more at this duty cycle; the full rank is table C._

---

## B1. The minimum bill, which a $/hour table hides

A published hourly rate is not what you pay for a short burst. **42 modes in this corpus bill a minimum of one hour** and 9 bill a minimum of one full day. For an agent that starts a sandbox, runs a tool call and starts again, the minimum is the price that actually applies, and every table above hides it.

Two profiles, each compared against the **same** demand so the comparison is like for like:

- **many short sessions**: 20 starts a day of 0.25 h each = 5 h of real demand. This is what an agent running a tool call, reading a result and starting again actually does.
- **few long sessions**: 5 starts a day of 2 h each = 10 h. Every session already exceeds a one-hour minimum, so the minimum never bites here.

**26 of 202 providers are affected.** The worst:

| # | provider | $/hour | same demand, smooth | same demand, bursty | penalty | rounds up to | link |
|---|---|---|---|---|---|---|---|
| 1 | [HostMyApple](https://hostmyapple.com/mac-vps-hosting) | 0.0479 | $7.19/mo | $20706.62/mo | **2880.0x** | min 2.592e+06 s | `hostmyapple` |
| 2 | [AWS EC2 Mac (Dedicated Host)](https://aws.amazon.com/ec2/instance-types/mac/) | 0.6500 | $97.50/mo | $9360.00/mo | **96.0x** | min 86400 s | `aws-ec2-mac` |
| 3 | [Flow Swiss Mac Bare Metal](https://doc.flow.swiss/platform/pricing/mac-bare-metal) | 0.3263 | $48.94/mo | $4698.65/mo | **96.0x** | min 86400 s | `flow-swiss-mac` |
| 4 | [use.computer](https://use.computer/) | 0.4500 | $67.50/mo | $6480.00/mo | **96.0x** | min 86400 s | `use-computer` |
| 5 | [MacStadium](https://www.macstadium.com/pricing) | 0.1493 | $3225.20/mo | $64504.08/mo | **20.0x** | min 2.592e+06 s | `macstadium` |
| 6 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | 0.0178 | $2.66/mo | $10.65/mo | **4.0x** | min 3600 s | `alibaba-ecs` |
| 7 | [Aptible](https://www.aptible.com) | 0.2000 | $30.00/mo | $120.00/mo | **4.0x** | gran 3600 s | `aptible` |
| 8 | [Amazon WorkSpaces Personal (Windows)](https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/) | 0.0425 | $6.37/mo | $25.48/mo | **4.0x** | gran 3600 s | `aws-workspaces` |
| 9 | [Civo Compute](https://www.civo.com/pricing) | 0.0298 | $4.46/mo | $17.86/mo | **4.0x** | min 3600 s | `civo` |
| 10 | [Contabo](https://contabo.com/en-us/pricing/) | 0.0090 | $1.36/mo | $5.42/mo | **4.0x** | min 3600 s | `contabo` |
| 11 | [E2E Networks](https://www.e2enetworks.com/pricing) | 0.0440 | $6.60/mo | $26.40/mo | **4.0x** | gran 3600 s | `e2e-networks` |
| 12 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | 0.0104 | $1.56/mo | $6.24/mo | **4.0x** | min 3600 s | `hetzner-cloud` |
| 13 | [Hetzner Dedicated AX / EX](https://www.hetzner.com/dedicated-rootserver/) | 0.1075 | $16.12/mo | $64.50/mo | **4.0x** | min 3600 s | `hetzner-dedicated` |
| 14 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | 0.0335 | $5.03/mo | $20.13/mo | **4.0x** | min 3600 s | `hostinger-vps` |
| 15 | [Latitude.sh](https://www.latitude.sh/pricing) | 0.1900 | $28.50/mo | $114.00/mo | **4.0x** | gran 3600 s | `latitude-sh` |
| 16 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | 0.0360 | $5.40/mo | $21.60/mo | **4.0x** | min 3600 s | `linode` |
| 17 | [NAVER Cloud / LINE-NAVER scope](https://www.ncloud.com/product/compute/server) | 0.1414 | $21.21/mo | $84.84/mo | **4.0x** | gran 3600 s | `naver-cloud` |
| 18 | [netcup VPS](https://www.netcup.com/en/server/vps) | 0.0117 | $1.75/mo | $7.00/mo | **4.0x** | min 3600 s | `netcup` |
| 19 | [Paperspace](https://docs.digitalocean.com/products/paperspace/pricing/) | 0.0400 | $6.00/mo | $24.00/mo | **4.0x** | gran 3600 s | `paperspace` |
| 20 | [Sakura Internet Cloud](https://cloud.sakura.ad.jp/products/server/) | 0.1333 | $19.99/mo | $79.97/mo | **4.0x** | min 3600 s | `sakura-cloud` |

Read these as bounds, not predictions. `bursty` assumes every session is shorter than the minimum, which is the pessimistic side; a real agent that holds one sandbox for the hour pays once. What the column establishes is which headline rates cannot survive a bursty workload.

**Two different mechanisms, one effect, and the column above keeps them apart.** A *minimum billable unit* charges at least that much per start regardless. A *granularity* rounds any partial hour up to the next step. Both make a 15-minute session cost a full hour, which is why Civo, Hetzner, Scaleway and UpCloud are 4x worse bursty, and why Aptible and Paperspace are too despite publishing no minimum at all.

**The ones that bite hardest are not the expensive ones.** HostMyApple at $0.0479/hour carries a 30-day minimum; a bursty agent would pay $20,706 a month against $7.19 for the same demand smoothed. Hetzner's $0.0104/hour is 4x worse bursty than smooth, and it ranks third in the `agent` table above on the smooth number. The market's cheap providers are disproportionately hourly-rounders, and that is invisible in a rate table.

---

## B2. GPU providers — priced per GPU-hour

A GPU box is billed per GPU-hour, not per vCPU. Ranking one beside a CPU box compares two currencies, so these get their own table. Revision 2 dropped all of them silently; there are 17.

Cheapest published model per provider, with the hour/day/week/month cost of holding ONE of that GPU:

| # | provider | cheapest GPU | $/GPU-hour | $/day | $/week | $/month | spot? | link |
|---|---|---|---|---|---|---|---|---|
| 1 | [Microsoft Azure GPU VMs](https://prices.azure.com/api/retail/prices) | T4 | 0.15 | 0.15 | 1.04 | 4.48 | yes | `azure-gpu` |
| 2 | [Vast.ai](https://github.com/vast-ai/docs/blob/main/guides/pricing.mdx) | RTX-4090 | 0.35 | 0.35 | 2.43 | 10.40 | no | `vast-ai` |
| 3 | [TensorDock](https://www.tensordock.com/) | RTX-4090 | 0.35 | 0.35 | 2.45 | 10.50 | no | `tensordock` |
| 4 | [Thunder Compute](https://www.thundercompute.com/pricing) | RTX-A6000 | 0.35 | 0.35 | 2.45 | 10.50 | no | `thunder-compute` |
| 5 | [Google Compute Engine GPU VMs](https://cloud.google.com/products/compute/pricing/accelerator-optimized) | L4 | 0.42 | 0.42 | 2.97 | 12.72 | yes | `gcp-compute-gpu` |
| 6 | [OVHcloud GPU instances](https://www.ovhcloud.com/en/public-cloud/prices/) | Quadro-RTX-5000 | 0.60 | 0.60 | 4.20 | 18.00 | no | `ovh-gpu` |
| 7 | [Comfy Deploy](https://app.comfydeploy.com/pricing) | T4 | 0.65 | 0.65 | 4.54 | 19.44 | no | `comfy-deploy` |
| 8 | [Lambda](https://lambda.ai/pricing) | Quadro-RTX-6000 | 0.69 | 0.69 | 4.83 | 20.70 | no | `lambda` |
| 9 | [DigitalOcean GPU Droplets](https://www.digitalocean.com/pricing/gpu-droplets) | RTX-4000-Ada | 0.76 | 0.76 | 5.32 | 22.80 | no | `digitalocean-gpu` |
| 10 | [CoreWeave](https://www.coreweave.com/pricing) | L40 | 0.78 | 0.78 | 5.49 | 23.51 | yes | `coreweave` |
| 11 | [Scaleway GPU instances](https://www.scaleway.com/en/pricing/gpu/) | L4 | 0.90 | 0.90 | 6.27 | 26.88 | no | `scaleway-gpu` |
| 12 | [Vultr Cloud GPU](https://api.vultr.com/v2/plans?type=vcg) | L40S | 1.67 | 1.67 | 11.70 | 50.13 | no | `vultr-gpu` |
| 13 | [Together AI](https://www.together.ai/pricing) | H100 | 1.99 | 1.99 | 13.93 | 59.70 | yes | `together-gpu` |
| 14 | [Voltage Park](https://www.voltagepark.com/pricing) | H100 | 1.99 | 1.99 | 13.93 | 59.70 | no | `voltage-park` |
| 15 | [fal](https://fal.ai/pricing) | RTX-PRO-6000 | 2.99 | 2.99 | 20.93 | 89.70 | no | `fal` |
| 16 | [Hyperbolic](https://www.hyperbolic.ai/marketplace) | H100-SXM | 3.19 | 3.19 | 22.33 | 95.70 | no | `hyperbolic` |
| 17 | [Shadeform](https://www.shadeform.ai/) | H100 | 5.99 | 5.99 | 41.93 | 179.70 | no | `shadeform` |

The full per-model price list for each provider is in `data/period-model.json` under `gpu_tiers`. Spot prices are interruptible: the machine can be reclaimed. Every row here is a published rate, none is a negotiated price.

---

## C. Every provider, ranked

Nothing truncated. One row per provider that priced at any shape and period, ordered by its `agent` month at 10 h/day **before credits are applied**, so a provider whose credit happens to cover this month is never presented as the cheapest thing in the market. The period columns after the first are also before credit, except where a credit is shown in the `free/mo` column.

| # | provider | category | isolation | $/h agent | 1h/day | 4h/day | 10h/day | 24h/day | free/mo | floor | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Agent 37](https://www.agent37.com/pricing) | agent-sandbox | gvisor | 0.0060 | 0.18 | 0.72 | 1.81 | 4.34 | - | - | `agent-37` |
| 2 | [Lizard](https://lizard.build/pricing) **(disputed)** | agent-sandbox | container | 0.0090 | 0.27 | 1.08 | 2.70 | 6.48 | - | - | `lizard` |
| 3 | [Contabo](https://contabo.com/en-us/pricing/) | hyperscaler | vm | 0.0090 | 0.27 | 1.08 | 2.71 | 6.51 | - | - | `contabo` |
| 4 | [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/compute/pricing/) | hyperscaler | vm | 0.0091 | 0.27 | 1.09 | 2.74 | 6.57 | - | - | `oracle-cloud` |
| 5 | [Hetzner Cloud](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | hyperscaler | vm | 0.0104 | 0.31 | 1.25 | 3.12 | 7.49 | - | - | `hetzner-cloud` |
| 6 | [Moonshot Kimi Hosted Agents sandbox](https://platform.kimi.com/docs/pricing/hosted-agents.md) | agent-sandbox | - | 0.0107 | 0.32 | 1.29 | 3.22 | 7.73 | - | - | `moonshot-kimi` |
| 7 | [Upstash Box](https://upstash.com/pricing/box) | agent-sandbox | container | 0.0110 | 0.33 | 1.32 | 3.29 | 7.89 | - | - | `upstash-box` |
| 8 | [netcup VPS](https://www.netcup.com/en/server/vps) | hyperscaler | vm | 0.0117 | 0.35 | 1.40 | 3.50 | 8.39 | - | - | `netcup` |
| 9 | [zipbox](https://zipbox.ai/pricing) | agent-sandbox | firecracker | 0.0137 | 0.41 | 1.64 | 4.11 | 9.86 | - | - | `zipbox` |
| 10 | [IONOS Cloud](https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-eur-en) | hyperscaler | vm | 0.0148 | 0.44 | 1.77 | 4.44 | 10.65 | - | - | `ionos` |
| 11 | [Alibaba Cloud ECS International](https://www.alibabacloud.com/en/product/ecs/pricing) | hyperscaler | vm | 0.0178 | 0.53 | 2.13 | 5.33 | 12.78 | - | - | `alibaba-ecs` |
| 12 | [Gcore Cloud / Functions / GPU](https://gcore.com/cloud/virtual-machines) | hyperscaler | vm | 0.0193 | 0.58 | 2.32 | 5.80 | 13.92 | - | - | `gcore` |
| 13 | [shellbox](https://shellbox.dev/) | agent-sandbox | firecracker | 0.0200 | 0.60 | 2.40 | 6.00 | 14.40 | - | - | `shellbox` |
| 14 | [UpCloud](https://upcloud.com/pricing/) | hyperscaler | vm | 0.0208 | 0.62 | 2.50 | 6.25 | 15.00 | - | - | `upcloud` |
| 15 | [Zeabur](https://zeabur.com/pricing) | paas | container | 0.0055 | 5.16 | 5.66 | 6.64 | 8.95 | - | - | `zeabur` |
| 16 | [Scaleway Instances](https://www.scaleway.com/en/pricing/virtual-instances/) | hyperscaler | vm | 0.0230 | 0.69 | 2.76 | 6.89 | 16.54 | - | - | `scaleway` |
| 17 | [Verda (formerly DataCrunch)](https://verda.com/pricing) | gpu-cloud | vm | 0.0240 | 0.72 | 2.88 | 7.20 | 17.28 | - | - | `verda` |
| 18 | [Cube Computer](https://cube.computer/) | dev-env | vm | 0.0247 | 0.74 | 2.97 | 7.42 | 17.81 | - | - | `cube` |
| 19 | [OVHcloud Public Cloud](https://us.ovhcloud.com/public-cloud/prices/) | hyperscaler | vm | 0.0256 | 0.77 | 3.07 | 7.68 | 18.43 | - | - | `ovhcloud` |
| 20 | [Kamatera](https://www.kamatera.com/pricing/) | hyperscaler | vm | 0.0274 | 0.82 | 3.29 | 8.22 | 19.73 | - | - | `kamatera` |
| 21 | [Google Cloud Run](https://cloud.google.com/run/pricing) | hyperscaler | gvisor | 0.0297 | 0.00 | 0.00 | 3.70 | 16.19 | $5.22 | - | `google-cloud-run` |
| 22 | [Civo Compute](https://www.civo.com/pricing) | hyperscaler | vm | 0.0298 | 0.89 | 3.57 | 8.93 | 21.43 | - | - | `civo` |
| 23 | [Vultr Cloud Compute](https://www.vultr.com/pricing/) | hyperscaler | vm | 0.0298 | 0.89 | 3.58 | 8.94 | 21.46 | - | - | `vultr` |
| 24 | [Ubicloud](https://www.ubicloud.com/docs/about/pricing) | hyperscaler | vm | 0.0312 | 0.94 | 3.74 | 9.36 | 22.46 | - | - | `ubicloud` |
| 25 | [KakaoCloud Virtual Machine](https://www.kakaocloud.com/services/virtual-machine/pricing) | hyperscaler | vm | 0.0326 | 0.98 | 3.91 | 9.77 | 23.44 | - | - | `kakao-cloud` |
| 26 | [IBM Cloud VPC](https://www.ibm.com/products/virtual-servers/pricing) | hyperscaler | vm | 0.0328 | 0.98 | 3.93 | 9.83 | 23.59 | - | - | `ibm-cloud-vpc` |
| 27 | [Google Compute Engine (Windows Server)](https://cloud.google.com/compute/disks-image-pricing#windows_server_pricing) | windows | vm | 0.0335 | 1.01 | 4.02 | 10.05 | 24.12 | - | - | `gcp-windows` |
| 28 | [Hostinger VPS](https://www.hostinger.com/vps-hosting) | hyperscaler | vm | 0.0335 | 1.01 | 4.03 | 10.06 | 24.15 | - | - | `hostinger-vps` |
| 29 | [Prized](https://prized.dev/docs/billing) | dev-env | vm | 0.0342 | 10.00 | 10.00 | 10.27 | 24.66 | - | $10 | `prized` |
| 30 | [Fly.io Machines](https://fly.io/pricing) | paas | firecracker | 0.0353 | 5.00 | 5.00 | 10.58 | 25.40 | - | $5 | `fly-machines` |
| 31 | [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets) | hyperscaler | vm | 0.0357 | 1.07 | 4.29 | 10.71 | 25.71 | - | - | `digitalocean` |
| 32 | [Akamai Cloud / Linode](https://www.akamai.com/cloud/pricing) | hyperscaler | vm | 0.0360 | 1.08 | 4.32 | 10.80 | 25.92 | - | - | `linode` |
| 33 | [Nebius](https://docs.nebius.com/compute/resources/pricing) | gpu-cloud | vm | 0.0368 | 1.10 | 4.42 | 11.04 | 26.50 | - | - | `nebius` |
| 34 | [Tencent Cloud Studio](https://cloud.tencent.cn/document/product/1039/131894) | dev-env | container | 0.0373 | 1.12 | 4.47 | 11.18 | 26.82 | - | - | `tencent-cloud-studio` |
| 35 | [Azure Virtual Machines (Linux)](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/) | hyperscaler | vm | 0.0376 | 1.13 | 4.51 | 11.28 | 27.07 | - | - | `azure-vm` |
| 36 | [Hugging Face Jobs (hf-sandbox backend)](https://huggingface.co/docs/hub/en/jobs-pricing) | paas | container | 0.0100 | 9.30 | 10.20 | 12.00 | 16.20 | - | - | `huggingface-jobs` |
| 37 | [Manus Cloud Computer](https://help.manus.im/en/articles/15392078-understanding-cloud-computer-plans-and-billing) | agent-sandbox | vm | 0.0411 | 1.23 | 4.93 | 12.33 | 29.59 | - | - | `manus-cloud-computer` |
| 38 | [Azure Virtual Machines (Windows Server)](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/windows/) | windows | vm | 0.0416 | 1.25 | 4.99 | 12.48 | 29.95 | - | - | `azure-windows` |
| 39 | [Amazon WorkSpaces Personal (Windows)](https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/) | windows | vm | 0.0425 | 1.27 | 5.10 | 12.74 | 30.58 | - | - | `aws-workspaces` |
| 40 | [E2E Networks](https://www.e2enetworks.com/pricing) | hyperscaler | vm | 0.0440 | 1.32 | 5.28 | 13.20 | 31.68 | - | - | `e2e-networks` |
| 41 | [tama](https://tama.computer/) | agent-sandbox | vm | 0.0454 | 1.36 | 5.45 | 13.62 | 32.70 | - | - | `tama` |
| 42 | [Run Cloud](https://docs.run.cloud/sandboxes/index.md) | agent-sandbox | firecracker | 0.0466 | 0.00 | 0.00 | 0.00 | 18.55 | $15 | - | `run-cloud` |
| 43 | [Exoscale](https://www.exoscale.com/pricing/) | hyperscaler | vm | 0.0467 | 1.40 | 5.60 | 14.00 | 33.60 | - | - | `exoscale` |
| 44 | [HostMyApple](https://hostmyapple.com/mac-vps-hosting) | macos | vm | 0.0479 | 1.44 | 5.75 | 14.38 | 34.51 | - | - | `hostmyapple` |
| 45 | [AWS EC2 (reference VMs)](https://aws.amazon.com/ec2/pricing/on-demand/) | hyperscaler | vm | 0.0491 | 1.47 | 5.89 | 14.73 | 35.35 | - | - | `aws-ec2` |
| 46 | [STACKIT Compute Engine](https://pim.api.stackit.cloud/v1/skus) | hyperscaler | vm | 0.0493 | 1.48 | 5.91 | 14.78 | 35.46 | - | - | `stackit` |
| 47 | [Windows 365 Cloud PC (Business / Enterprise)](https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing) | windows | vm | 0.0493 | 1.48 | 5.92 | 14.79 | 35.51 | - | - | `windows-365` |
| 48 | [Claude Managed Agents](https://platform.claude.com/docs/en/about-claude/pricing#claude-managed-agents-pricing) | agent-sandbox | container | 0.0500 | 1.50 | 6.00 | 15.00 | 36.00 | - | - | `claude-managed-agents` |
| 49 | [Jarvislabs](https://jarvislabs.ai/pricing) | gpu-cloud | vm | 0.0500 | 1.50 | 6.00 | 15.00 | 36.00 | - | - | `jarvislabs` |
| 50 | [Mosaic Sandbox](https://sandbox.mosaicos.com/) | agent-sandbox | firecracker | 0.0500 | 1.50 | 6.00 | 15.00 | 36.00 | - | - | `mosaic` |
| 51 | [machine0](https://machine0.io/) | agent-sandbox | vm | 0.0520 | 1.56 | 6.24 | 15.60 | 37.44 | - | - | `machine0` |
| 52 | [Alibaba Cloud Agent Sandbox / FC / AgentRun](https://help.aliyun.com/zh/agent-sandbox/product-overview/billing-overview) | agent-sandbox | - | 0.0549 | 1.65 | 6.59 | 16.48 | 39.55 | - | - | `alibaba-agentrun` |
| 53 | [AWS Fargate](https://aws.amazon.com/fargate/pricing/) | hyperscaler | firecracker | 0.0581 | 1.74 | 6.97 | 17.43 | 41.83 | - | - | `aws-fargate` |
| 54 | [AWS EC2 (Windows Server)](https://aws.amazon.com/ec2/pricing/on-demand/) | windows | vm | 0.0600 | 1.80 | 7.20 | 18.00 | 43.20 | - | - | `aws-ec2-windows` |
| 55 | [Celesto Cloud](https://celesto.ai/pricing) | agent-sandbox | vm | 0.0600 | 1.80 | 7.20 | 18.00 | 43.20 | - | - | `celesto` |
| 56 | [Runpod](https://www.runpod.io/pricing) | gpu-cloud | container | 0.0600 | 1.80 | 7.20 | 18.00 | 43.20 | - | - | `runpod` |
| 57 | [Sandbox0](https://sandbox0.ai/pricing) | agent-sandbox | gvisor | 0.0600 | 1.80 | 7.20 | 18.00 | 43.20 | - | - | `sandbox0` |
| 58 | [UCloud Agent Sandbox](https://astraflow.ucloud.cn/docs/agent-sandbox) | agent-sandbox | firecracker | 0.0644 | 1.93 | 7.73 | 19.31 | 46.35 | - | - | `ucloud` |
| 59 | [PPIO Agent Sandbox](https://ppio.com/docs/sandbox/pricing.md) | agent-sandbox | firecracker | 0.0644 | 1.93 | 7.73 | 19.31 | 46.35 | - | - | `ppio-sandbox` |
| 60 | [Volcano Engine AgentKit / veFaaS sandbox](https://docs.volcengine.com/docs/agentkit/Billing_items?lang=zh) | agent-sandbox | vm | 0.0653 | 1.96 | 7.84 | 19.60 | 47.05 | - | - | `volcengine-agentkit` |
| 61 | [Google Colab](https://developers.google.com/colab) | dev-env | vm | 0.0664 | 1.99 | 7.97 | 19.91 | 47.79 | - | - | `google-colab` |
| 62 | [boat.dev](https://docs.boat.dev/pricing) | agent-sandbox | vm | 0.0180 | 20.00 | 20.00 | 20.00 | 20.00 | - | $20 | `boat` |
| 63 | [Paperspace](https://docs.digitalocean.com/products/paperspace/pricing/) | gpu-cloud | vm | 0.0400 | 9.20 | 12.80 | 20.00 | 36.80 | - | - | `paperspace` |
| 64 | [Northflank Sandboxes](https://northflank.com/pricing) | agent-sandbox | vm | 0.0667 | 2.00 | 8.00 | 20.01 | 48.02 | - | - | `northflank` |
| 65 | [Google Compute Engine (Linux VMs)](https://cloud.google.com/products/compute/pricing/general-purpose) | hyperscaler | vm | 0.0670 | 2.01 | 8.04 | 20.10 | 48.25 | - | - | `gcp-compute` |
| 66 | [Kedge](https://kedge.dev/docs/billing) | agent-sandbox | vm | 0.0685 | 0.00 | 3.22 | 15.55 | 44.32 | $5 | - | `kedge` |
| 67 | [AWS CodeBuild](https://aws.amazon.com/codebuild/pricing/) | paas | container | 0.0720 | 2.16 | 8.64 | 21.60 | 51.84 | - | - | `aws-codebuild` |
| 68 | [Vultr Cloud Compute (Windows Server)](https://docs.vultr.com/support/platform/billing/is-a-windows-license-included-in-the-monthly-price) | windows | vm | 0.0774 | 2.32 | 9.29 | 23.21 | 55.71 | - | - | `vultr-windows` |
| 69 | [Crusoe](https://www.crusoe.ai/cloud/pricing) | gpu-cloud | vm | 0.0800 | 2.40 | 9.60 | 24.00 | 57.60 | - | - | `crusoe` |
| 70 | [Runtime (withruntime.com)](https://withruntime.com/pricing) | agent-sandbox | firecracker | 0.0800 | 2.40 | 9.60 | 24.00 | 57.60 | - | - | `withruntime` |
| 71 | [MacinCloud](https://www.macincloud.com/pages/dedicated.html) | macos | vm | 0.0808 | 2.42 | 9.70 | 24.25 | 58.19 | - | - | `macincloud` |
| 72 | [Red Hat OpenShift (Harbor backend)](https://www.redhat.com/en/technologies/cloud-computing/openshift/pricing) | paas | container | 0.0855 | 2.56 | 10.26 | 25.65 | 61.56 | - | - | `openshift` |
| 73 | [Buddy Sandboxes](https://buddy.works/pricing) | agent-sandbox | vm | 0.0864 | 2.59 | 10.37 | 25.92 | 62.21 | - | - | `buddy` |
| 74 | [Samsung SDS Cloud Platform](https://cloud.samsungsds.com/serviceportal/pricing.html) | hyperscaler | vm | 0.0896 | 2.69 | 10.75 | 26.88 | 64.51 | - | - | `samsung-cloud` |
| 75 | [Prime Intellect Sandboxes](https://www.primeintellect.ai/sandboxes) | agent-sandbox | vm | 0.0900 | 2.70 | 10.80 | 27.00 | 64.80 | - | - | `prime-intellect` |
| 76 | [Sandbox as a Service](https://sandbox-as-a-service.com/pricing) | agent-sandbox | vm | 0.0900 | 2.70 | 10.80 | 27.00 | 64.80 | - | - | `sandbox-as-a-service` |
| 77 | [Clever Cloud](https://www.clever.cloud/pricing/) | paas | vm | 0.0918 | 2.75 | 11.02 | 27.55 | 66.12 | - | - | `clever-cloud` |
| 78 | [Green Mini host](https://portal.greenmini.host/checkout/order) | macos | dedicated-host | 0.0946 | 2.84 | 11.35 | 28.37 | 68.08 | - | - | `greenmini` |
| 79 | [Baseten](https://docs.baseten.co/deployment/resources) | gpu-cloud | container | 0.1038 | 3.11 | 12.46 | 31.14 | 74.74 | - | - | `baseten` |
| 80 | [exe.dev](https://exe.dev/pricing) | dev-env | vm | 0.1050 | 15.00 | 15.00 | 31.50 | 75.60 | - | $15 | `exe-dev` |
| 81 | [Hetzner Dedicated AX / EX](https://www.hetzner.com/dedicated-rootserver/) | hyperscaler | dedicated-host | 0.1075 | 3.23 | 12.90 | 32.25 | 77.40 | - | - | `hetzner-dedicated` |
| 82 | [Isorun](https://docs.isorun.ai/getting-started/pricing) | agent-sandbox | vm | 0.1100 | 3.30 | 13.20 | 33.00 | 79.20 | - | - | `isorun` |
| 83 | [Railway](https://railway.com/pricing) | agent-sandbox | vm | 0.1112 | 5.00 | 13.34 | 33.35 | 80.04 | - | $5 | `railway` |
| 84 | [OakHost](https://www.oakhost.com/mac-mini-hosting) | macos | dedicated-host | 0.1122 | 3.37 | 13.46 | 33.66 | 80.78 | - | - | `oakhost` |
| 85 | [Novita AI Agent Sandbox](https://docs.novita.ai/guides/sandbox-pricing) | agent-sandbox | firecracker | 0.1166 | 3.50 | 14.00 | 34.99 | 83.98 | - | - | `novita` |
| 86 | [CreateOS Sandbox (NodeOps)](https://createos.sh/products/sandbox) | agent-sandbox | firecracker | 0.1187 | 10.00 | 14.24 | 35.61 | 85.46 | - | $10 | `createos` |
| 87 | [Scaleway Apple silicon (Mac mini)](https://www.scaleway.com/en/pricing/apple-silicon/) | macos | dedicated-host | 0.1202 | 3.61 | 14.42 | 36.06 | 86.55 | - | - | `scaleway-apple-silicon` |
| 88 | [Koyeb Sandboxes](https://www.koyeb.com/pricing) | agent-sandbox | vm | 0.0288 | 29.86 | 32.46 | 37.64 | 49.74 | - | - | `koyeb` |
| 89 | [Collimate](https://collimate.ai/pricing) | agent-sandbox | firecracker | 0.1280 | 3.84 | 15.36 | 38.40 | 92.16 | - | - | `collimate` |
| 90 | [Tencent Cloud SCF](https://cloud.tencent.com/document/product/583/17299) | hyperscaler | container | 0.1220 | 5.49 | 16.47 | 38.42 | 89.65 | - | - | `tencent-scf` |
| 91 | [Replit](https://docs.replit.com/billing/deployment-pricing) | paas | vm | 0.0694 | 38.00 | 38.00 | 38.82 | 67.97 | - | $20 | `replit` |
| 92 | [Open Telekom Cloud / T Cloud Public](https://www.open-telekom-cloud.com/en/prices) | hyperscaler | vm | 0.1309 | 3.93 | 15.71 | 39.28 | 94.27 | - | - | `open-telekom-cloud` |
| 93 | [Sakura Internet Cloud](https://cloud.sakura.ad.jp/products/server/) | hyperscaler | vm | 0.1333 | 4.00 | 15.99 | 39.98 | 95.96 | - | - | `sakura-cloud` |
| 94 | [Docker Cloud Sandboxes](https://www.docker.com/blog/introducing-cloud-sandboxes-start-on-your-laptop-finish-in-the-cloud/) | agent-sandbox | vm | 0.1400 | 4.20 | 16.80 | 42.00 | 100.80 | - | - | `docker-cloud-sandboxes` |
| 95 | [Tencent Cloud Agent Runtime — Agent Sandbox](https://cloud.tencent.com/document/product/1814/133249) | agent-sandbox | - | 0.1406 | 4.22 | 16.87 | 42.17 | 101.20 | - | - | `tencent-agent-runtime` |
| 96 | [NAVER Cloud / LINE-NAVER scope](https://www.ncloud.com/product/compute/server) | hyperscaler | vm | 0.1414 | 4.24 | 16.97 | 42.42 | 101.80 | - | - | `naver-cloud` |
| 97 | [RentaMac (rentamac.io)](https://rentamac.io/pricing) | macos | dedicated-host | 0.1459 | 4.38 | 17.51 | 43.77 | 105.04 | - | - | `rentamac` |
| 98 | [Solari](https://docs.getsolari.com/pricing) | agent-sandbox | vm | 0.0798 | 22.39 | 29.58 | 43.94 | 77.46 | - | - | `solari` |
| 99 | [Together Code Sandbox](https://www.together.ai/pricing) | agent-sandbox | firecracker | 0.1488 | 4.46 | 17.86 | 44.64 | 107.14 | - | - | `together-code-sandbox` |
| 100 | [MacStadium](https://www.macstadium.com/pricing) | macos | dedicated-host | 0.1493 | 4.48 | 17.92 | 44.79 | 107.51 | - | - | `macstadium` |
| 101 | [Blacksmith (GitHub Actions runners)](https://www.blacksmith.sh/pricing) | macos | vm | 0.1500 | 0.00 | 6.00 | 33.00 | 96.00 | $12 | - | `blacksmith` |
| 102 | [AWS Lambda](https://aws.amazon.com/lambda/pricing/) | hyperscaler | firecracker | 0.1600 | 0.00 | 12.33 | 41.13 | 108.33 | $6.87 | - | `aws-lambda` |
| 103 | [Cloudflare Workers for Platforms](https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/reference/pricing/) | paas | isolate | 0.1440 | 9.32 | 22.28 | 48.20 | 108.68 | - | - | `cloudflare-workers-for-platforms` |
| 104 | [Blaxel](https://blaxel.ai/pricing) | agent-sandbox | firecracker | 0.1656 | 20.00 | 20.00 | 49.68 | 119.23 | - | $20 | `blaxel` |
| 105 | [Hopx](https://hopx.ai/pricing) | agent-sandbox | firecracker | 0.1656 | 4.97 | 19.87 | 49.68 | 119.23 | - | - | `hopx` |
| 106 | [Omnara](https://www.omnara.com/pricing) | agent-sandbox | - | 0.1656 | 4.97 | 19.87 | 49.68 | 119.23 | - | - | `omnara` |
| 107 | [OpenReward Sandboxes](https://openreward.ai/pricing) | agent-sandbox | container | 0.1656 | 4.97 | 19.87 | 49.68 | 119.23 | - | - | `openreward` |
| 108 | [Runta](https://runta.com/pricing/) | agent-sandbox | vm | 0.1656 | 4.97 | 19.87 | 49.68 | 119.23 | - | - | `runta` |
| 109 | [Superserve](https://superserve.ai/pricing) | agent-sandbox | firecracker | 0.1656 | 4.97 | 19.87 | 49.68 | 119.23 | - | - | `superserve` |
| 110 | [Freestyle](https://www.freestyle.sh/pricing) | agent-sandbox | bare-metal-vm | 0.1322 | 31.62 | 31.62 | 31.62 | 76.83 | $18.38 | $50 | `freestyle` |
| 111 | [orkestr Sandboxes](https://orkestr.eu/sandboxes) | agent-sandbox | vm | 0.1707 | 5.12 | 20.48 | 51.20 | 122.88 | - | - | `orkestr` |
| 112 | [OmniRun](https://omnirun.io/pricing) | agent-sandbox | firecracker | 0.1707 | 21.62 | 21.62 | 51.21 | 122.90 | - | $21.62 | `omnirun` |
| 113 | [PandaStack](https://www.pandastack.ai/pricing/) | agent-sandbox | firecracker | 0.1728 | 20.00 | 20.74 | 51.84 | 124.42 | - | $20 | `pandastack` |
| 114 | [Cua Fleet (Windows Server)](https://cua.ai/pricing) | windows | vm | 0.1785 | 5.36 | 21.42 | 53.55 | 128.52 | - | - | `cua-windows` |
| 115 | [Cua Fleet](https://cua.ai/pricing) | agent-sandbox | vm | 0.1785 | 5.36 | 21.42 | 53.55 | 128.52 | - | - | `cua` |
| 116 | [GitHub Codespaces](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) | dev-env | vm | 0.1800 | 5.40 | 21.60 | 54.00 | 129.60 | - | - | `github-codespaces` |
| 117 | [WarpBuild (GitHub Actions runners)](https://www.warpbuild.com/pricing) | macos | vm | 0.1800 | 5.40 | 21.60 | 54.00 | 129.60 | - | - | `warpbuild` |
| 118 | [Modelence](https://modelence.com) | paas | container | 0.1200 | 23.60 | 34.40 | 56.00 | 106.40 | - | - | `modelence` |
| 119 | [Arker](https://arker.ai/docs/pricing) | agent-sandbox | vm | 0.1877 | 5.63 | 22.53 | 56.32 | 135.17 | - | - | `arker` |
| 120 | [CodeSandbox SDK](https://codesandbox.io/docs/sdk/pricing) | agent-sandbox | firecracker | 0.1486 | 10.51 | 23.89 | 50.64 | 113.05 | $5.944 | - | `codesandbox-sdk` |
| 121 | [boxd](https://boxd.sh/pricing) | agent-sandbox | vm | 0.1900 | 5.70 | 22.80 | 57.00 | 136.80 | - | - | `boxd` |
| 122 | [Latitude.sh](https://www.latitude.sh/pricing) | hyperscaler | dedicated-host | 0.1900 | 5.70 | 22.80 | 57.00 | 136.80 | - | - | `latitude-sh` |
| 123 | [InsForge (InstaCloud)](https://www.instacloud.com/pricing) | paas | vm | 0.1112 | 35.00 | 35.00 | 48.35 | 95.04 | $10 | $20 | `insforge-instacloud` |
| 124 | [Cloudflare Sandbox SDK / Containers](https://developers.cloudflare.com/containers/platform/pricing/) | agent-sandbox | vm | 0.1800 | 10.40 | 26.60 | 59.00 | 134.60 | - | - | `cloudflare-sandbox` |
| 125 | [Bitrise (mobile CI)](https://bitrise.io/pricing) | macos | vm | 0.1320 | 35.00 | 35.84 | 59.60 | 115.04 | - | $15 | `bitrise` |
| 126 | [Render](https://render.com/pricing) | paas | container | 0.1164 | 28.49 | 38.97 | 59.93 | 108.84 | - | - | `render` |
| 127 | [Capy](https://capy.ai) | agent-sandbox | vm | 0.2000 | 6.00 | 24.00 | 60.00 | 144.00 | - | - | `capy` |
| 128 | [Specific](https://specific.dev/pricing) | paas | container | 0.1200 | 28.60 | 39.40 | 61.00 | 111.40 | - | - | `specific` |
| 129 | [RunsOn](https://runs-on.com/pricing/) | paas | vm | 0.1080 | 32.41 | 42.13 | 61.57 | 106.93 | - | - | `runs-on` |
| 130 | [Cirrus Runners](https://cirrus-runners.app/pricing/) | macos | apple-vm | 0.2055 | 6.16 | 24.66 | 61.64 | 147.94 | - | - | `cirrus-runners` |
| 131 | [Google Agent Runtime / Agent Engine](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) | hyperscaler | gvisor | 0.2060 | 6.18 | 24.72 | 61.80 | 148.32 | - | - | `google-agent-engine` |
| 132 | [Google Agent Platform Sandbox (Code Execution / Shell / Computer Use)](https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing) | agent-sandbox | container | 0.2060 | 6.18 | 24.72 | 61.80 | 148.32 | - | - | `vertex-computer-use` |
| 133 | [Dedalus Labs](https://www.dedaluslabs.ai/pricing) | agent-sandbox | vm | 0.1490 | 24.47 | 37.88 | 64.71 | 127.31 | - | - | `dedalus-labs` |
| 134 | [Azure Container Apps (Consumption, Dedicated, Dynamic Sessions)](https://azure.microsoft.com/en-us/pricing/details/container-apps/) | hyperscaler | vm | 0.2160 | 1.08 | 20.52 | 59.40 | 150.12 | $5.4 | - | `azure-container-apps` |
| 135 | [Azure Container Apps Sandboxes](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-overview) | hyperscaler | vm | 0.2160 | 6.48 | 25.92 | 64.80 | 155.52 | - | - | `azure-container-apps-sandboxes` |
| 136 | [Amazon Bedrock AgentCore (Runtime / Code Interpreter / Browser)](https://aws.amazon.com/bedrock/agentcore/pricing/) | hyperscaler | firecracker | 0.2168 | 6.50 | 26.02 | 65.04 | 156.10 | - | - | `aws-agentcore` |
| 137 | [Heroku](https://www.heroku.com/pricing/) | paas | container | 0.2083 | 11.25 | 30.00 | 67.50 | 155.00 | - | - | `heroku` |
| 138 | [Tinfoil](https://tinfoil.sh) | paas | vm | 0.1600 | 24.80 | 39.20 | 68.00 | 135.20 | - | - | `tinfoil` |
| 139 | [Sprites (Fly.io)](https://fly.io/pricing) | agent-sandbox | firecracker | 0.1640 | 24.92 | 39.68 | 69.20 | 138.08 | - | - | `sprites` |
| 140 | [smol machines](https://smolmachines.com/pricing) | agent-sandbox | vm | 0.1648 | 24.94 | 39.78 | 69.44 | 138.66 | - | - | `smol-machines` |
| 141 | [Morph Cloud](https://cloud.morph.so/web/subscribe) | agent-sandbox | vm | 0.1000 | 43.00 | 52.00 | 70.00 | 112.00 | - | - | `morph-cloud` |
| 142 | [Amp Orbs](https://ampcode.com/docs/orbs/sizes-and-costs) | dev-env | vm | 0.1700 | 25.10 | 40.40 | 71.00 | 142.40 | - | - | `amp` |
| 143 | [StarSling](https://starsling.dev/pricing) | dev-env | firecracker | 0.2400 | 7.20 | 28.80 | 72.00 | 172.80 | - | - | `starsling` |
| 144 | [Microsoft Foundry hosted agents (East US)](https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/) | hyperscaler | vm | 0.2460 | 7.38 | 29.52 | 73.80 | 177.12 | - | - | `azure-foundry-agents` |
| 145 | [GitHub Copilot cloud sandboxes](https://docs.github.com/en/billing/concepts/product-billing/cloud-and-local-sandboxes) | hyperscaler | firecracker | 0.2160 | 16.48 | 35.92 | 74.80 | 165.52 | - | - | `github-copilot-cloud-sandboxes` |
| 146 | [Ona (formerly Gitpod)](https://ona.com/pricing) | dev-env | vm | 0.2500 | 20.00 | 30.00 | 75.00 | 180.00 | - | $20 | `ona` |
| 147 | [AWS Lambda MicroVMs](https://aws.amazon.com/lambda/pricing/) | hyperscaler | firecracker | 0.2522 | 7.57 | 30.26 | 75.66 | 181.58 | - | - | `aws-lambda-microvms` |
| 148 | [OpenPond Cloud Sandboxes](https://openpond.ai/pricing) | agent-sandbox | firecracker | 0.2376 | 17.13 | 38.51 | 81.28 | 181.07 | - | - | `openpond` |
| 149 | [Wasmer](https://wasmer.io/pricing) | paas | isolate | 0.2400 | 17.20 | 38.80 | 82.00 | 182.80 | - | - | `wasmer` |
| 150 | [Alibaba Cloud ACK (Harbor backend)](https://www.alibabacloud.com/product/kubernetes) | hyperscaler | container | 0.0693 | 67.78 | 74.01 | 86.48 | 115.57 | - | - | `alibaba-ack` |
| 151 | [Islo](https://islo.dev/pricing) | agent-sandbox | vm | 0.3000 | 50.00 | 50.00 | 90.00 | 216.00 | - | $50 | `islo` |
| 152 | [GitHub Actions hosted runners](https://docs.github.com/en/billing/reference/actions-runner-pricing) | macos | vm | 0.3000 | 13.00 | 40.00 | 94.00 | 220.00 | - | - | `github-actions` |
| 153 | [AgentComputer](https://agentcomputer.ai/pricing) | agent-sandbox | firecracker | 0.3150 | 9.45 | 37.80 | 94.50 | 226.80 | - | - | `agentcomputer` |
| 154 | [LangSmith Sandboxes](https://www.langchain.com/pricing) | agent-sandbox | vm | 0.1890 | 44.67 | 61.68 | 95.70 | 175.08 | - | - | `langsmith-sandbox` |
| 155 | [Flow Swiss Mac Bare Metal](https://doc.flow.swiss/platform/pricing/mac-bare-metal) | macos | dedicated-host | 0.3263 | 9.79 | 39.16 | 97.89 | 234.93 | - | - | `flow-swiss-mac` |
| 156 | [microsandbox](https://microsandbox.dev/pricing) | agent-sandbox | vm | 0.1648 | 53.94 | 68.78 | 98.44 | 167.66 | - | - | `microsandbox` |
| 157 | [Declaw](https://docs.declaw.ai/platform/billing) | agent-sandbox | firecracker | 0.1656 | 100.00 | 100.00 | 100.00 | 119.23 | - | $100 | `declaw` |
| 158 | [Vercel Sandbox](https://vercel.com/docs/sandbox/pricing) | agent-sandbox | firecracker | 0.3408 | 20.00 | 40.90 | 102.24 | 245.38 | - | $20 | `vercel-sandbox` |
| 159 | [Rivet (Actors & agentOS)](https://rivet.dev/pricing/) | agent-sandbox | - | 0.2794 | 28.38 | 53.52 | 103.81 | 221.14 | - | - | `rivet` |
| 160 | [Hyperstack](https://www.hyperstack.cloud/gpu-pricing) | gpu-cloud | vm | 0.3500 | 10.50 | 42.00 | 105.00 | 252.00 | - | - | `hyperstack` |
| 161 | [GKE Agent Sandbox](https://cloud.google.com/kubernetes-engine/docs/concepts/agent-sandbox) | hyperscaler | gvisor | 0.1087 | 76.26 | 86.04 | 105.61 | 151.26 | - | - | `gke-agent-sandbox` |
| 162 | [CircleCI](https://circleci.com/pricing/price-list/) | macos | vm | 0.3600 | 15.00 | 43.20 | 108.00 | 259.20 | - | $15 | `circleci` |
| 163 | [Google Cloud Build](https://cloud.google.com/build/pricing) | paas | vm | 0.3600 | 10.80 | 43.20 | 108.00 | 259.20 | - | - | `google-cloud-build` |
| 164 | [Replicate](https://replicate.com/pricing) | gpu-cloud | container | 0.3600 | 10.80 | 43.20 | 108.00 | 259.20 | - | - | `replicate` |
| 165 | [Deno Sandbox](https://deno.com/deploy/pricing) | agent-sandbox | firecracker | 0.3000 | 29.00 | 56.00 | 110.00 | 236.00 | - | - | `deno-sandbox` |
| 166 | [StateSet Sandbox](https://sandbox.stateset.app/) | agent-sandbox | gvisor | 0.2320 | 55.96 | 76.84 | 118.60 | 216.04 | - | - | `stateset` |
| 167 | [Huawei Cloud AgentArts](https://support.huaweicloud.com/price-agentarts/agentarts-price-pdf.pdf) | agent-sandbox | container | 0.3973 | 11.92 | 47.67 | 119.18 | 286.04 | - | - | `huawei-cloud` |
| 168 | [Cerebrium](https://cerebrium.ai/pricing) | gpu-cloud | container | 0.0791 | 102.37 | 109.50 | 123.74 | 156.97 | - | - | `cerebrium` |
| 169 | [Depot (GitHub Actions runners)](https://depot.dev/pricing) | macos | vm | 0.3600 | 30.80 | 63.20 | 128.00 | 279.20 | - | - | `depot` |
| 170 | [OpenAI Containers (Code Interpreter / Hosted Shell)](https://developers.openai.com/api/docs/pricing) | agent-sandbox | vm | 0.3600 | 30.80 | 63.20 | 128.00 | 279.20 | - | - | `openai-containers` |
| 171 | [Shardflux](https://shardflux.dev/#pricing) | agent-sandbox | firecracker | 0.4000 | 21.00 | 57.00 | 129.00 | 297.00 | - | - | `shardflux` |
| 172 | [Amika](https://www.amika.dev/pricing) | agent-sandbox | vm | 0.3312 | 39.94 | 69.74 | 129.36 | 268.46 | - | - | `amika` |
| 173 | [Baponi](https://baponi.ai/pricing/) | agent-sandbox | container | 0.1200 | 100.60 | 111.40 | 133.00 | 183.40 | - | - | `baponi` |
| 174 | [OpenComputer](https://opencomputer.dev/sandboxes) | agent-sandbox | vm | 0.3780 | 31.34 | 65.36 | 133.40 | 292.16 | - | - | `opencomputer` |
| 175 | [use.computer](https://use.computer/) | macos | apple-vm | 0.4500 | 13.50 | 54.00 | 135.00 | 324.00 | - | - | `use-computer` |
| 176 | [Ellipsis](https://www.ellipsis.dev/pricing) | agent-sandbox | qemu-kvm | 0.4567 | 13.70 | 54.81 | 137.01 | 328.83 | - | - | `ellipsis` |
| 177 | [Datalayer Runtimes](https://datalayer.io/pricing) | dev-env | container | 0.3000 | 58.00 | 85.00 | 139.00 | 265.00 | - | - | `datalayer` |
| 178 | [InstaVM](https://instavm.io/pricing) | agent-sandbox | firecracker | 0.1656 | 104.97 | 119.87 | 149.68 | 219.23 | - | - | `instavm` |
| 179 | [Beam](https://www.beam.cloud/pricing) | agent-sandbox | gvisor | 0.2272 | 95.81 | 116.26 | 157.15 | 252.56 | - | - | `beam` |
| 180 | [Namespace](https://namespace.so/pricing) | dev-env | vm | 0.2400 | 107.20 | 128.80 | 172.00 | 272.80 | - | - | `namespace` |
| 181 | [Buildkite hosted agents](https://buildkite.com/pricing) | macos | vm | 0.4800 | 44.40 | 87.60 | 174.00 | 375.60 | - | - | `buildkite-hosted` |
| 182 | [Alibaba Cloud AgentBay](https://www.alibabacloud.com/help/en/agentbay/product-overview/agentbay-billing-instructions) | agent-sandbox | container | 0.0992 | 151.98 | 160.90 | 178.76 | 220.42 | - | - | `alibaba-agentbay` |
| 183 | [Trigger.dev](https://trigger.dev/pricing) | paas | container | 0.6120 | 28.36 | 83.44 | 193.60 | 450.64 | - | - | `trigger-dev` |
| 184 | [Replicas](https://replicas.dev) | agent-sandbox | vm | 0.4800 | 64.40 | 107.60 | 194.00 | 395.60 | - | - | `replicas` |
| 185 | [AWS EC2 Mac (Dedicated Host)](https://aws.amazon.com/ec2/instance-types/mac/) | macos | dedicated-host | 0.6500 | 19.50 | 78.00 | 195.00 | 468.00 | - | - | `aws-ec2-mac` |
| 186 | [Bitbucket Pipelines](https://www.atlassian.com/software/bitbucket/pricing) | paas | container | 0.6000 | 36.25 | 90.25 | 198.25 | 450.25 | - | - | `bitbucket-pipelines` |
| 187 | [boxes.dev](https://boxes.dev/) | dev-env | firecracker | 0.6000 | 37.00 | 91.00 | 199.00 | 451.00 | - | - | `boxes-dev` |
| 188 | [E2B](https://e2b.dev/pricing) | agent-sandbox | firecracker | 0.1656 | 154.97 | 169.87 | 199.68 | 269.23 | - | - | `e2b` |
| 189 | [Lightning AI](https://lightning.ai/pricing) | dev-env | vm | 0.5100 | 65.30 | 111.20 | 203.00 | 417.20 | - | - | `lightning-ai` |
| 190 | [Zo Computer](https://www.zo.computer/pricing) | dev-env | container | 0.0247 | 200.74 | 202.96 | 207.40 | 217.75 | - | - | `zo-computer` |
| 191 | [GitLab.com hosted runners](https://docs.gitlab.com/ci/pipelines/compute_minutes/) | macos | vm | 0.6000 | 47.00 | 101.00 | 209.00 | 461.00 | - | - | `gitlab-runners` |
| 192 | [SF Compute (GPU market + Autoresearch sandboxes)](https://autoresearch.sfcompute.com/) | gpu-cloud | vm | 0.7315 | 21.95 | 87.78 | 219.46 | 526.69 | - | - | `sfcompute` |
| 193 | [Tensorlake Sandboxes](https://www.tensorlake.ai/pricing) | agent-sandbox | firecracker | 0.1200 | 250.00 | 250.00 | 250.00 | 250.00 | - | $250 | `tensorlake` |
| 194 | [Sail Research (Sailboxes)](https://docs.sailresearch.com/pricing) | agent-sandbox | firecracker | 0.0620 | 246.86 | 252.44 | 263.60 | 289.64 | $5 | - | `sail` |
| 195 | [Tenki Sandbox](https://tenki.cloud/pricing) | agent-sandbox | vm | 0.1656 | 254.97 | 269.87 | 299.68 | 369.23 | - | - | `tenki` |
| 196 | [Expo](https://expo.dev) | macos | vm | 1.0800 | 51.40 | 148.60 | 343.00 | 796.60 | - | - | `expo` |
| 197 | [Runloop](https://www.runloop.ai/pricing) | agent-sandbox | vm | 0.3168 | 259.50 | 288.02 | 345.04 | 478.10 | - | - | `runloop` |
| 198 | [Modal](https://modal.com/pricing) | agent-sandbox | gvisor | 0.3799 | 231.40 | 265.58 | 333.96 | 493.51 | $30 | - | `modal` |
| 199 | [MIOSA](https://miosa.ai/pricing) | agent-sandbox | firecracker | 0.1552 | 500.00 | 500.00 | 500.00 | 500.00 | - | $500 | `miosa` |
| 200 | [Archil](https://archil.com/pricing) | agent-sandbox | vm | 0.1800 | 505.40 | 521.60 | 554.00 | 629.60 | - | - | `archil` |
| 201 | [Aptible](https://www.aptible.com) | paas | container | 0.2000 | 505.00 | 523.00 | 559.00 | 643.00 | - | - | `aptible` |
| 202 | [Codemagic (mobile CI)](https://codemagic.io/pricing/) | macos | vm | 2.7000 | 130.00 | 373.00 | 859.00 | 1993.00 | - | - | `codemagic` |
| 203 | [Azure Pipelines](https://azure.microsoft.com/en-us/pricing/details/devops/azure-devops-services/) | paas | vm | 3.7200 | 111.60 | 446.40 | 1116.00 | 2678.40 | - | - | `azure-pipelines` |
| 204 | [Daytona (Windows sandboxes)](https://www.daytona.io/pricing) | windows | vm | 0.1656 | 2000.00 | 2000.00 | 2000.00 | 2000.00 | - | $2000 | `daytona-windows` |
| 205 | [Daytona](https://www.daytona.io/pricing) | agent-sandbox | container | 0.1656 | 2000.00 | 2000.00 | 2000.00 | 2000.00 | - | $2000 | `daytona` |
| 206 | [Nextmv](https://nextmv.io) | paas | container | 9.7200 | 291.60 | 1166.40 | 2916.00 | 6998.40 | - | - | `nextmv` |

**(disputed)** marks a row priced from a size the vendor advertises and the corpus card dropped, where the vendor's own pricing page and its own docs contradict each other. The price is the vendor's, not a confirmed figure. See FINDINGS section 5.5 and the note under table B.

---

## D. Every card accounted for

A missing row is a result. This is what happened to all 275 cards in the corpus, so a deliberate exclusion cannot be mistaken for an oversight.

Produced by `experiments/90-exclusion-ledger.py` at corpus commit `f6a71ab09fef`.

| status | cards | what it means |
|---|---|---|
| `ranked` | 197 | Ranked in table C. |
| `ranked-partial` | 9 | Ranked for some shapes only. |
| `gpu-only` | 15 | GPU-only provider: every mode sells a GPU, and no CPU rate is published. Priced separately as a GPU workload, not dropped. |
| `prelaunch-only` | 2 | Every published rate sits on a pre-launch mode (a region or offering that does not exist yet). There is no live price to rank. arker was the serious case: its cheapest mode was `eu-hetzner-proposed` at $0.0302/h against a live on-demand rate of $0.1877/h on the same card. |
| `too-big` | 16 | Publishes rates, but no published size meets the smallest shape priced here (1 vCPU / 1 GiB). It is a larger machine than this catalogue covers, not an unpriced one. |
| `no-rate` | 86 | The card publishes modes but no hourly rate and no size table, so there is nothing here to compute. REPROBED 2026-10-02 against each provider's own page (experiments/95-reprobe-unpriced.py): 45 of 86 genuinely publish no dollar figure, 7 were unreachable, and 34 DO publish prices, which means for those the corpus card is incomplete rather than the vendor being silent. They are not re-priced here because a $199/mo figure beside a support plan is not machine-hour data; closing that gap is the corpus maintainer's work. |
| `off-category` | 41 | Browser, scraping or non-compute product: sells minutes of a remote browser or a SaaS, not machines. Surveyed for free credit, excluded from ranking. |
| **total** | **366** | must equal the corpus card count |

### Where it breaks down by category

| category | total | ranked | partial | gpu-only | too big | no price | off-category |
|---|---|---|---|---|---|---|---|
| agent-sandbox | 126 | 80 | 6 | 0 | 8 | 30 | 0 |
| hyperscaler | 44 | 43 | 1 | 0 | 0 | 0 | 0 |
| paas | 42 | 22 | 0 | 0 | 2 | 18 | 0 |
| gpu-cloud | 41 | 11 | 0 | 15 | 1 | 14 | 0 |
| browser | 37 | 0 | 0 | 0 | 0 | 0 | 37 |
| dev-env | 33 | 13 | 1 | 0 | 1 | 18 | 0 |
| macos | 26 | 20 | 1 | 0 | 2 | 3 | 0 |
| windows | 13 | 8 | 0 | 0 | 2 | 3 | 0 |
| other | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| inference-api | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| self-host | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| finops | 1 | 0 | 0 | 0 | 0 | 0 | 1 |

### The 86 with no price in the card

The largest group of providers outside the ranking, so it is named rather than summarised. They are absent because the **card** carries no rate and no size table, not because this model refused them.

Each was then re-probed against the provider's own page (`experiments/95-reprobe-unpriced.py`). Of the 86:

- **45 publish no dollar figure at all.** The corpus is right.
- **7 were unreachable.** No verdict either way.
- **20 publish a machine rate** (`/min`, `/hour`, `/month`) that the card never captured. For these the corpus card is simply wrong. BuildJet is the clearest: $0.004/min for 2 vCPU / 8 GB, published, and the card carries no rate.
- **14 carry dollars that are not a machine rate**, such as an enterprise SSO tier. Ambiguous, and left ambiguous.

None of the 20 or 14 are re-priced here. Turning a marketing page into a card is the implementing session's work; a research session that guesses a rate produces a number nobody can check.

| provider | category | card says | page re-probe | figures seen | link |
|---|---|---|---|---|---|
| [Agency Tool Company](https://agencytool.com) | dev-env | no rate, no sizes | no-price-on-page | - | `agency-tool-company` |
| [Agent Relay](https://agentrelay.com) | paas | no rate, no sizes | no-price-on-page | - | `agent-relay` |
| [ainclave](https://www.ainclave.com/pricing) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `ainclave` |
| [Apoxy](https://apoxy.dev) | paas | no rate, no sizes | machine-rate-on-page | $0.05, $0.25 | `apoxy` |
| [Arga Labs](https://www.argalabs.com/) | agent-sandbox | no rate, no sizes | dollars-but-not-a-rate | $10 | `arga-labs` |
| [Artillery](https://www.artillery.io/pricing) | dev-env | no rate, no sizes | machine-rate-on-page | $ 0, $ 199, $ 499, $1199 | `artillery` |
| [AutoComputer](https://www.autocomputer.ai/) | windows | no rate, no sizes | unreachable | - | `autocomputer` |
| [Brimble Sandboxes](https://brimble.io/pricing) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $ 0, $ 11, $ 3, $0.032 | `brimble` |
| [BuildJet](https://buildjet.com/for-github-actions) | dev-env | no rate, no sizes | machine-rate-on-page | $0.004, $0.008, $0.016, $0.032, $0.048, $0.0 | `buildjet` |
| [Butter](https://butter.dev) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `butter` |
| [Bytebot](https://www.bytebot.ai/) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `bytebot` |
| [Caution](https://caution.co/pricing.html) | paas | no rate, no sizes | no-price-on-page | - | `caution` |
| [Chronicle Labs](https://chronicle-labs.com) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `chronicle-labs` |
| [Clusy](https://www.clusy.io/pricing) | dev-env | no rate, no sizes | machine-rate-on-page | $0, $12, $200, $30, $90 | `clusy` |
| [Coder](https://coder.com/pricing) | dev-env | no rate, no sizes | no-price-on-page | - | `coder` |
| [Cyberdesk](https://www.cyberdesk.io) | windows | no rate, no sizes | no-price-on-page | - | `cyberdesk` |
| [Dagger](https://dagger.io) | dev-env | no rate, no sizes | no-price-on-page | - | `dagger` |
| [Dexto](https://www.dexto.ai/docs/models/) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $0.00, $0.00474, $0.005, $0.00588, $0.006, $ | `dexto` |
| [Dockup](https://getdockup.com/) | paas | no rate, no sizes | dollars-but-not-a-rate | $45 | `dockup` |
| [Eventual](https://www.eventual.ai/) | paas | no rate, no sizes | no-price-on-page | - | `eventual` |
| [Expanse](https://expanse.sh) | gpu-cloud | no rate, no sizes | dollars-but-not-a-rate | $8 | `expanse` |
| [FlowDeploy](https://flowdeploy.com) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `flowdeploy` |
| [Fluidstack](https://fluidstack.io/) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `fluidstack` |
| [Halluminate](https://halluminate.ai/) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `halluminate` |
| [Hatchet](https://hatchet.run) | paas | no rate, no sizes | no-price-on-page | - | `hatchet-run` |
| [Heroic Labs](http://heroiclabs.com) | paas | no rate, no sizes | dollars-but-not-a-rate | $۹ | `heroic-labs` |
| [Hoplite](https://hoplite.sh) | agent-sandbox | no rate, no sizes | dollars-but-not-a-rate | $ 82.50, $0, $99 | `hoplite` |
| [HumanLayer](https://humanlayer.com) | agent-sandbox | no rate, no sizes | dollars-but-not-a-rate | $100 | `humanlayer` |
| [Hyrex](https://www.hyrex.io) | paas | no rate, no sizes | unreachable | - | `hyrex` |
| [Isle](https://www.tryisle.com/) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $0, $29 | `isle` |
| [Jamsocket](https://jamsocket.com) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $30 | `jamsocket` |
| [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks) | dev-env | no rate, no sizes | no-price-on-page | - | `kaggle` |
| [KubeSail](https://kubesail.com) | paas | no rate, no sizes | no-price-on-page | - | `kubesail` |
| [Lapdev](https://lap.dev/pricing/) | dev-env | no rate, no sizes | no-price-on-page | - | `lapdev` |
| [Limrun](https://lim.run) | macos | no rate, no sizes | no-price-on-page | - | `limrun` |
| [Manufact](https://manufact.com) | paas | no rate, no sizes | machine-rate-on-page | $0, $0.10, $1, $2, $25, $250, $5 | `manufact` |
| [Metorial](https://metorial.com) | paas | no rate, no sizes | dollars-but-not-a-rate | $49.00 | `metorial` |
| [Minicor](https://minicor.com) | windows | no rate, no sizes | no-price-on-page | - | `minicor` |
| [MiniMax Agent hosting / developer API scope](https://platform.minimax.io/docs/llms.txt) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `minimax` |
| [Mistral Compute / AI Cloud](https://mistral.ai/products/aicloud/) | gpu-cloud | no rate, no sizes | unreachable | - | `mistral-compute` |
| [Nebius ConTree (Token Factory Sandboxes)](https://tokenfactory.nebius.com/sandboxes/about) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `nebius-contree` |
| [Nodus Compute](https://www.nodus-compute.ai/pricing/) | agent-sandbox | no rate, no sizes | dollars-but-not-a-rate | $0.0075, $0.0179, $0.0316, $0.0357, $0.0396, | `nodus-compute` |
| [Okteto](https://okteto.com) | dev-env | no rate, no sizes | no-price-on-page | - | `okteto` |
| [OneCLI](https://onecli.sh) | agent-sandbox | no rate, no sizes | dollars-but-not-a-rate | $5 | `onecli` |
| [OpenHands Remote Sandbox / Cloud](https://docs.openhands.dev/openhands/usage/sandboxes/remote) | dev-env | no rate, no sizes | no-price-on-page | - | `openhands-runtime` |
| [Orgo](https://www.orgo.ai/pricing) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $ 29, $ 399, $ 99, $10, $29, $5, $50 | `orgo` |
| [OVHcloud GPU instances](https://www.ovhcloud.com/en/public-cloud/prices/) | gpu-cloud | no rate, no sizes | machine-rate-on-page | $ 200, $0.0000027, $0.0000033, $0.00000597,  | `ovh-gpu` |
| [PaperPod](https://www.paperpod.dev/) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $0.0001, $0.02, $1, $100, $20, $5, $5.00 | `paperpod` |
| [Party](https://party.build) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $0, $0.04, $0.14, $0.21, $0.31, $0.36, $0.93 | `party` |
| [Pipekit](https://pipekit.io/pricing) | dev-env | no rate, no sizes | dollars-but-not-a-rate | $799 | `pipekit` |
| [Pipeshift](https://pipeshift.com) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `pipeshift` |
| [Playgent](https://useplaygent.com) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `playgent` |
| [Ploomber](https://ploomber.io/) | paas | no rate, no sizes | unreachable | - | `ploomber` |
| [PoplarML](http://poplarml.com) | gpu-cloud | no rate, no sizes | unreachable | - | `poplarml` |
| [Porter](https://porter.run) | paas | no rate, no sizes | dollars-but-not-a-rate | $181, $20, $312, $347, $46, $60, $70, $72, $ | `porter` |
| [Reflex](https://reflex.dev/pricing/) | paas | no rate, no sizes | machine-rate-on-page | $ 25, $0, $100, $200, $25, $50 | `reflex` |
| [Refresh](https://www.refresh.dev) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `refresh` |
| [Release](https://release.com/pricing) | dev-env | no rate, no sizes | no-price-on-page | - | `release` |
| [Rescale](https://rescale.com) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `rescale` |
| [Revyl](https://www.revyl.com) | macos | no rate, no sizes | no-price-on-page | - | `revyl` |
| [Riza Code Interpreter](https://riza.io/pricing) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $250 | `riza` |
| [RunKit](https://runkit.com/) | agent-sandbox | no rate, no sizes | unreachable | - | `runkit` |
| [ScitiX Agent Sandbox](https://scitix.github.io/Agent-Sandbox/) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `scitix-agent-sandbox` |
| [SeaCloudAI Sandbox](https://sandbox-gateway.cloud.seaart.ai) | agent-sandbox | no rate, no sizes | unreachable | - | `seacloudai` |
| [Sealos DevBox](https://sealos.io/pricing/) | dev-env | no rate, no sizes | machine-rate-on-page | $0, $0.05, $0.15, $10, $12,451, $128, $2,030 | `sealos-devbox` |
| [Server4Agent](https://www.server4agent.com/pricing) | dev-env | no rate, no sizes | machine-rate-on-page | $0, $0.08, $0.10, $0.12, $1, $10, $150, $2,  | `server4agent` |
| [SF Tensor](https://sf-tensor.com) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `sf-tensor` |
| [Shadeform](https://www.shadeform.ai/) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `shadeform` |
| [Shuttle](https://www.shuttle.dev) | paas | no rate, no sizes | no-price-on-page | - | `shuttle` |
| [Sieve](https://sievedata.com/) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `sieve` |
| [Signadot](https://www.signadot.com/) | dev-env | no rate, no sizes | dollars-but-not-a-rate | $2 | `signadot` |
| [Skyhook](https://skyhook.io) | paas | no rate, no sizes | no-price-on-page | - | `skyhook` |
| [Tart + Orchard (Cirrus Labs)](https://tart.run/licensing/) | macos | no rate, no sizes | dollars-but-not-a-rate | $12, $12,000, $36,000 | `tart-orchard` |
| [Teclada](https://www.teclada.com/) | dev-env | no rate, no sizes | machine-rate-on-page | $100, $500 | `teclada` |
| [Tencent Cloud CubeSandbox](https://github.com/TencentCloud/CubeSandbox) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `tencent-cubesandbox` |
| [TensorPool](https://tensorpool.dev) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `tensorpool` |
| [Texel.ai](https://texel.ai) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `texel-ai` |
| [Tilde.run (discontinued)](https://lakefs.io/blog/we-recently-shut-down-tilde-run/) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `tilde-run` |
| [Trainy](https://trainy.ai/) | paas | no rate, no sizes | dollars-but-not-a-rate | $1,231, $1,232, $18,240, $2,034, $461, $640 | `trainy` |
| [Unikraft Cloud](https://unikraft.com/pricing) | agent-sandbox | no rate, no sizes | machine-rate-on-page | $0, $199, $39 | `unikraft-cloud` |
| [Vibrant Labs](https://vibrantlabs.com/) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `vibrant-labs` |
| [webapp.io](https://webapp.io) | dev-env | no rate, no sizes | no-price-on-page | - | `webapp-io` |
| [StackBlitz WebContainers](https://stackblitz.com/pricing) | dev-env | no rate, no sizes | no-price-on-page | - | `webcontainers` |
| [Windmill](https://www.windmill.dev/pricing) | paas | no rate, no sizes | machine-rate-on-page | $ 0, $ 10, $ 100, $ 120, $ 20, $ 50, $170 | `windmill` |
| [Zhipu Z Managed Agents](https://docs.bigmodel.cn/cn/managed-agents/overview.md) | agent-sandbox | no rate, no sizes | no-price-on-page | - | `zhipu` |
| [Zibra Labs](https://zibralabs.ai/) | gpu-cloud | no rate, no sizes | no-price-on-page | - | `zibra-labs` |

### The 2 priced only on a pre-launch mode

Every rate these cards publish sits on a region or offering that does not exist yet, so there is no live price to rank. **This is not a theoretical category**: arker was ranked at $0.0302/hour from `eu-hetzner-proposed` while the same card's live on-demand rate is $0.1877/hour, a factor of six. Revision 2 carried that row until the winning mode of every ranked provider was audited for pre-launch wording.

| provider | category | link |
|---|---|---|
| [Computer Use Cloud (computeruse.run)](https://computeruse.run/) | agent-sandbox | `computeruse-cloud` |
| [Leap0](https://leap0.dev/) | agent-sandbox | `leap0` |

### The 16 priced, but only for larger machines

| provider | category | link |
|---|---|---|
| [Veertu Anka Build Cloud](https://docs.veertu.com/anka/licensing/) | macos | `anka-build-cloud` |
| [Archal](https://www.archal.ai/) | agent-sandbox | `archal` |
| [Microsoft Dev Box (closed to new customers; retiring 2028-09-18)](https://azure.microsoft.com/en-us/products/dev-box/) | windows | `azure-dev-box` |
| [Claw 2 Agent](https://claw2agent.com/pricing) | agent-sandbox | `claw2agent` |
| [cloudrouter (Manaflow)](https://cloudrouter.dev) | agent-sandbox | `cloudrouter` |
| [Coasty](https://coasty.ai/pricing) | agent-sandbox | `coasty` |
| [ComputerUse.space](https://computeruse.space/) | agent-sandbox | `computeruse-space` |
| [Gemini API code execution](https://ai.google.dev/gemini-api/docs/code-execution) | agent-sandbox | `gemini-code-execution` |
| [Hetzner GPU servers](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/) | gpu-cloud | `hetzner-gpu` |
| [HUD](https://www.hud.ai/) | agent-sandbox | `hud` |
| [Kasm Workspaces](https://kasm.com/community-edition) | dev-env | `kasm-workspaces` |
| [Maritime](https://maritime.sh/pricing) | agent-sandbox | `maritime` |
| [Mastra](https://mastra.ai) | paas | `mastra` |
| [Windows 365 for Agents](https://learn.microsoft.com/en-us/windows-365/agents/pricing-paygo-always-available) | windows | `windows-365-agents` |
| [Apple Xcode Cloud](https://developer.apple.com/xcode-cloud/) | macos | `xcode-cloud` |
| [YepCode Run](https://yepcode.io/pricing/) | paas | `yepcode` |

### The 41 off-category products

Browser, scraping and non-compute products. They sell minutes of a remote browser or a SaaS, not machines, so ranking them beside a VM provider compares two purchases. They are still surveyed for free credit in tables A1 and A2.

| provider | category | link |
|---|---|---|
| [Airtop](https://www.airtop.ai/pricing) | browser | `airtop` |
| [Anchor Browser](https://anchorbrowser.io/pricing) | browser | `anchor-browser` |
| [Bright Data Browser API](https://brightdata.com/pricing/scraping-browser) | browser | `bright-data-browser` |
| [Browser Use Cloud](https://browser-use.com/pricing) | browser | `browser-use` |
| [BrowserAct](https://www.browseract.com/pricing) | browser | `browseract` |
| [Browserbase](https://www.browserbase.com/pricing) | browser | `browserbase` |
| [BrowserCloud](https://browsercloud.io/pricing) | browser | `browsercloud` |
| [Browserless](https://www.browserless.io/pricing) | browser | `browserless` |
| [Cedana](https://cedana.com/) | other | `cedana` |
| [CloudAxis](https://cloudaxis.ai/pricing/) | browser | `cloudaxis` |
| [CloudBrowser AI](https://cloudbrowser.ai/) | browser | `cloudbrowser` |
| [CloudCruise](https://cloudcruise.com/pricing) | browser | `cloudcruise` |
| [Cloudflare Browser Run / Kitesurf](https://developers.cloudflare.com/browser-run/pricing/) | browser | `cloudflare-browser` |
| [Ferr](https://ferr.dev/) | browser | `ferr` |
| [Firecrawl Interact / Browser Sandbox](https://www.firecrawl.dev/pricing) | browser | `firecrawl` |
| [Gologin Cloud Browser](https://gologin.com/cloud-browser/) | browser | `gologin` |
| [H Company / Surfer / H Agents API](https://www.hcompany.ai/pricing) | browser | `h-company` |
| [Hyperbeam](https://hyperbeam.com/) | browser | `hyperbeam` |
| [Hyperbrowser](https://www.hyperbrowser.ai/pricing) | browser | `hyperbrowser` |
| [Intuned](https://intunedhq.com/pricing) | browser | `intuned` |
| [Kernel](https://www.onkernel.com/pricing) | browser | `kernel` |
| [Lightpanda Cloud](https://lightpanda.io/pricing) | browser | `lightpanda` |
| [Magnitude](https://magnitude.dev/) | browser | `magnitude` |
| [Notte](https://www.notte.cc/pricing) | browser | `notte` |
| [OpenAGI / Lux](https://developer.agiopen.org/docs/pricing) | browser | `openagi` |
| [Opensteer](https://opensteer.com/pricing) | browser | `opensteer` |
| [Remote Browser](https://remote-browser.dev/pricing) | browser | `remote-browser` |
| [RunAnywhere](https://www.runanywhere.ai/) | inference-api | `runanywhere` |
| [Scrapeless Agent Browser](https://www.scrapeless.com/en/pricing) | browser | `scrapeless` |
| [Scrapfly Cloud Browser](https://scrapfly.io/pricing) | browser | `scrapfly` |
| [Scraping Bee](https://www.scrapingbee.com/pricing/) | browser | `scrapingbee` |
| [Self-hosted bare-metal sandbox fleet (hardware floor)](https://www.hetzner.com/dedicated-rootserver/ax42/) | self-host | `self-host-baremetal` |
| [Skyvern](https://www.skyvern.com/pricing) | browser | `skyvern` |
| [Smooth](https://www.smooth.sh/pricing) | browser | `smooth` |
| [Steel.dev](https://docs.steel.dev/overview/pricinglimits) | browser | `steel` |
| [Strong Compute](https://strongcompute.com) | finops | `strong-compute` |
| [Surfsky](https://surfsky.io/pricing) | browser | `surfsky` |
| [Tabstack](https://tabstack.ai/) | browser | `tabstack` |
| [Tilion](https://tilion.com/pricing) | browser | `tilion` |
| [TinyFish](https://www.tinyfish.ai/pricing) | browser | `tinyfish` |
| [Zenrows Browser Sessions](https://www.zenrows.com/pricing) | browser | `zenrows` |

