#!/usr/bin/env python3
"""Write kage's user config for the daily research run.

    OC_FREE_API_KEY=... python3 .github/research/write-kage-config.py [CONFIG_DIR]

Registers the oc-free gateway as a custom Anthropic-Messages provider (the
gateway's own docs name /v1/messages as the route for agent work) and asks the
gateway what the chosen model's context window is, so kage can compact history
at the right size. The /v1/models call also proves the key works before kage
spends a run on it: a 401 stops here with the gateway's own message.

Environment:
    OC_FREE_API_KEY   required. Never printed, never written to the file: the
                      config names the variable, kage reads it at run time.
    OC_FREE_BASE_URL  default https://oc-free.pg.ai.ajam.dev
    OC_FREE_MODEL     default oc-free-auto
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("OC_FREE_BASE_URL", "https://oc-free.pg.ai.ajam.dev").rstrip("/")
MODEL = os.environ.get("OC_FREE_MODEL", "oc-free-auto")
KEY = os.environ.get("OC_FREE_API_KEY", "")
CFG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.config/kage")


def fail(msg):
    print("write-kage-config: " + msg, file=sys.stderr)
    sys.exit(1)


if not KEY:
    fail("OC_FREE_API_KEY is empty or unset")

req = urllib.request.Request(BASE + "/v1/models", headers={"x-api-key": KEY})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        listing = json.load(resp)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")[:500]
    fail("GET /v1/models answered HTTP %d: %s" % (e.code, body))
except (urllib.error.URLError, TimeoutError, ValueError) as e:
    fail("GET /v1/models failed: %s" % e)

entries = {m.get("id"): m for m in listing.get("data", [])}
if MODEL not in entries:
    fail("model %r is not served; the gateway lists: %s" % (MODEL, sorted(k for k in entries if k)))
entry = entries[MODEL]

lines = [
    "# Written by .github/research/write-kage-config.py. Holds no key.",
    "[provider]",
    'default_model = "ocfree/%s"' % MODEL,
    "",
    "[providers.custom.ocfree]",
    'kind = "anthropic"',
    'base_url = "%s"' % BASE,
    'display_name = "pg.ai oc-free"',
    'api_key_env = "OC_FREE_API_KEY"',
    "",
    "[[providers.custom.ocfree.models]]",
    'id = "%s"' % MODEL,
    'name = "%s"' % MODEL,
]
for src, dst in (("context_window", "context"), ("max_output_tokens", "max_output")):
    v = entry.get(src)
    if isinstance(v, int) and v > 0:
        lines.append("%s = %d" % (dst, v))
lines += [
    "",
    "[shell]",
    "# The model's shell must never see the gateway key.",
    'scrub_env = ["OC_FREE_API_KEY", "*_TOKEN", "*_SECRET", "*_PASSWORD"]',
    "",
    "[agents]",
    "max_running = 4",
    "# One run ends in at most 45 minutes of agent work per agent.",
    "timeout = 2700",
    "",
]

os.makedirs(CFG, exist_ok=True)
path = os.path.join(CFG, "config.toml")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
os.chmod(path, 0o600)
print("wrote %s (model %s, context_window=%s, max_output_tokens=%s)" % (
    path, MODEL, entry.get("context_window"), entry.get("max_output_tokens")))
