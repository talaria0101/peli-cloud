#!/usr/bin/env python3
"""Re-fetch the first-party pages data/always-on-free.json quotes from.

    python3 verify/fetch.py          # fetch every page into verify/pages/
    python3 verify/fetch.py --check  # report which claims have no capture

The URL KEYS here are the same keys verify/claims.json checks by, so a page can
always be re-fetched by the name its claim uses. `--check` is what proves that:
a capture directory that cannot be regenerated from this file is a broken
evidence store, and the failure mode it prevents is a quote that verifies against
a stale copy nobody can reproduce.
"""
import json
import os
import ssl
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "verify", "pages")
CLAIMS = os.path.join(ROOT, "verify", "claims.json")
os.chdir(ROOT)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120 Safari/537.36"
}

# Every key here matches a key in verify/claims.json.
urls = {
    # --- the six corrected rows, plus the pages their quotes live on ---
    "oracle_alwaysfree": "https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm",
    "codespaces": "https://docs.github.com/en/billing/concepts/product-billing/github-codespaces",
    "hf_spaces_overview": "https://huggingface.co/docs/hub/en/spaces-overview",
    "hf_spaces_gpus": "https://huggingface.co/docs/hub/en/spaces-gpus",
    "koyeb_szt": "https://www.koyeb.com/docs/run-and-scale/scale-to-zero",
    "northflank_pricing": "https://northflank.com/pricing",
    "northflank_docs_billing": "https://northflank.com/docs/v1/application/billing/pricing-on-northflank",
    # Three Blinkenshell pages, because the quotes are on three different pages.
    # The wiki root is the "Start" page and carries neither the port nor the rules.
    "blinkenshell_wiki": "https://blinkenshell.org/wiki/FAQ",
    "blinkenshell_rules": "https://blinkenshell.org/docs/rules/",
    "blinkenshell_limits": "https://blinkenshell.org/docs/resource-limits/",
    # --- the always-on census ---
    "gcp_free": "https://cloud.google.com/free/docs/free-cloud-features",
    "render_free": "https://render.com/docs/free",
    "azure_appservice_linux": "https://azure.microsoft.com/en-us/pricing/details/app-service/linux/",
    "supabase_pricing": "https://supabase.com/pricing",
    "cf_workers_limits": "https://developers.cloudflare.com/workers/platform/limits/",
    "google_cloud_shell": "https://cloud.google.com/shell/docs/limitations",
    "serv00_offer": "https://serv00.com/pricing",
    "neon_pricing": "https://neon.com/pricing",
    "modelscope_hw": "https://modelscope.cn/openapi/v1/studios/hardware",
    "modelscope_ai_hw": "https://modelscope.ai/openapi/v1/studios/hardware",
    # --- free UNIX shells, incl. the deployed config the quotes come from ---
    "sdf_members01": "http://sdf.org/?faq?MEMBERS?01",
    "sdf_members05": "http://sdf.org/?faq?MEMBERS?05",
    "tilde_town": "https://tilde.town/wiki/faq.html",
    "tilde_town_autokick": "https://tilde.town/wiki/autokick.html",
    "tilde_town_admin": "https://tilde.town/wiki/administration.html",
    "tilde_club_faq": "https://tilde.club/wiki/faq.html",
    "tilde_green": "https://tilde.green/",
    "tilde_green_tos": "https://wiki.tilde.green/tos",
    "ctrlc_home": "https://ctrl-c.club/",
    "ctrlc_faq": "https://ctrl-c.club/faq.html",
    "ctrlc_signup": "https://signup.ctrl-c.club/",
    "ctrlc_notice": "https://ctrl-c.club/system_notice_long.html",
    "hashbang_stats": "https://hashbang.sh/server/stats",
    "hashbang_clean_lurkers": "https://raw.githubusercontent.com/hashbang/shell-etc/master/cron.daily/clean-lurkers",
    "hashbang_limits": "https://raw.githubusercontent.com/hashbang/shell-server/master/ansible/tasks/security/main.yml",
}


def check():
    """Which claims have no capture, and which captures have no URL."""
    claims = json.load(open(CLAIMS, encoding="utf-8"))
    claims.pop("_comment", None)
    missing = [p for p in claims if not os.path.exists(os.path.join(PAGES, f"{p}.html"))]
    orphan = [
        f for f in os.listdir(PAGES)
        if f.endswith(".html") and f[: -len(".html")] not in claims
    ] if os.path.isdir(PAGES) else []
    print(f"{len(claims)} claims, {len(os.listdir(PAGES)) if os.path.isdir(PAGES) else 0} captures")
    if missing:
        print("claims with NO capture (run verify/fetch.py):")
        for m in missing:
            print("  ", m)
    if orphan:
        print("captures with no claim (harmless, but they are dead weight):")
        for o in sorted(orphan):
            print("  ", o)
    no_url = [c for c in claims if c not in urls]
    if no_url:
        print("claims with NO url in fetch.py (cannot be re-fetched):")
        for c in no_url:
            print("  ", c)
    return 1 if (missing or no_url) else 0


def fetch():
    os.makedirs(PAGES, exist_ok=True)
    out = {}
    for k, u in urls.items():
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=30, context=ctx)
            b = r.read()
            with open(os.path.join(PAGES, f"{k}.html"), "wb") as fh:
                fh.write(b)
            out[k] = {"status": r.status, "bytes": len(b)}
        except Exception as e:
            out[k] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
    ok = sum(1 for v in out.values() if v.get("status") == 200)
    for k, v in sorted(out.items()):
        mark = "200" if v.get("status") == 200 else "ERR"
        print(f"  {mark} {k:<32} {v.get('bytes', v.get('error', ''))}")
    print(f"\n{ok}/{len(urls)} fetched")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else fetch())