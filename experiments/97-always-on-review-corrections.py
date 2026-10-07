#!/usr/bin/env python3
"""Second correction pass over data/always-on-free.json, after a review.

Idempotent, like 96-always-on-corrections.py before it: run it as many times as
you like and it prints "0 changes applied" from the second run on. Every change
below was measured, and each one is a defect that survived PR #1's own review
pass because the guard only tested that a quote was non-empty.

WHAT CHANGED, and the artefact that decides each:

1. neon-free: T2 -> DEAD. Its own cited page says a 24/7 database costs about
   182.5 CU-hours a month against a 100 CU-hour allowance, and that "100 CU-hours
   covers about 400 hours of active compute, more than half the hours in a
   month". tier_note says a relay "cannot defeat QUOTA walls" and tiers.DEAD is
   "a quota that exhausts regardless", so a counted T2 here inflates the count by
   exactly the thing the taxonomy exists to exclude. Defeating scale-to-zero is
   what makes the quota exhaust; the row's own keepalive field said so.

2. sdf-free-shell: T1 -> T2. T1 is defined as "No idle sleep, no hard session
   cap, no expiry. It just runs." The row's own idle_or_session_limit says
   "validated accounts expire after 2 years without a UNIX login" and it is the
   only T1 row in the file carrying a keepalive ("one login per 2 years"). By the
   file's own definitions that is T2.

3. ctrl-c-club: T1 -> T2, on the same clause. Its idle_or_session_limit is a
   "5-YEAR INACTIVITY ARCHIVE", which is an expiry with a restore path. Two rows
   claimed to be the most generous policy in the census (sdf's 2 years and this
   5 years); that contradiction goes away when both are T2 and neither is
   claiming to be the standout.

4. serv00: verified_by named verify/pages/serv00.html. That is not a key in
   verify/fetch.py; the key is serv00_offer. The byte count (54173) matched the
   real capture exactly, so this was a wrong path in a true claim.

5. blinkenshell: the primary quote was a reconstruction of a feature table that
   is not in any capture. blinkenshell_wiki (the wiki root) contains zero <table>
   elements; the only Free-vs-Supporter table is on /docs/resource-limits/ and
   its rows are memory / open files / processes / SSH sessions / background
   processes. The quote is replaced with the table's actual cells, and the
   verified_by is corrected to say which page carries it and that the Free column
   was read cell by cell from THAT table. The verdict does not change: the rules
   page independently carries "No IRC bots are allowed on free accounts" and "You
   are not allowed to run any server/daemon on free accounts. This includes
   bouncers."

6. ctrl-c-club: source pointed at system_notice_long.html, but its quote and
   quote2 are on signup.ctrl-c.club. Each quote now carries the page it is
   actually on. quote2 is corrected to signup.ctrl-c.club's own wording, because
   system_notice_long.html words it differently ("This has been a soft limit for a
   while, but the rules were hard to find or understand, and it has been unevenly
   enforced"), so keeping the old text under the new page would be a worse lie.

7. hashbang: quote added a semicolon the source does not have; quote2 collapsed
   a YAML line-fold continuation ("\\" then newline then "CPUQuota") into a
   space, which is a real character change. quote3 is not in any capture at all
   and is dropped rather than left as an unverifiable claim. The keepalive field
   already carries the file-existence semantics.

8. modelscope-studio: quote spliced two different API responses into one string
   with ".cn:" / ".ai:" labels that appear in neither. Replaced with the two
   responses as two separately-labelled fragments, each traceable to its own
   capture.

9. azure-appservice-f1: quote2 is not on the cited page, which verified_by
   already admitted. The row is re-tiered to UNVERIFIED-with-the-rest-kept shape:
   no - the shape is fine and the F1 figures ARE on the page. Instead the quote2
   is dropped and the 20-minute rule moves into caveats, labelled as
   second-hand, because a T2 classification that rests entirely on a number the
   row says is absent from its own source is not a T2.

10. rows whose verified_by claimed first-hand but named no capture now name the
    capture they mean, or say plainly that they read the page without keeping a
    capture. tilde-town and tilde-green were probed live rather than captured;
    the blinkenshell and hashbang rows name their captures now.

11. tier_note and the T1/T2 definitions are corrected so the file does not
    contradict itself: T1 becomes "no expiry" with sdf moved out, and the two
    "most generous in this census" claims are removed.

The counted total therefore moves from 22 to 20 (T1 7->5, T2 8->7, DEAD
17->18). That is the point: three rows were counted that the taxonomy excludes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "always-on-free.json")


def row(doc, rid):
    for r in doc["rows"]:
        if r["id"] == rid:
            return r
    raise SystemExit(f"no such row id: {rid}")


def apply(doc):
    changed = []

    # 1. neon-free: a quota that exhausts, not a liveness wall.
    neon = row(doc, "neon-free")
    if neon["tier"] != "DEAD":
        neon["tier"] = "DEAD"
        changed.append("neon-free: T2 -> DEAD")
    neon["hard_wall"] = (
        "100 CU-hrs/month per project, and the vendor's own page prices an "
        "always-on database above it: 'Once scale to zero is disabled, the "
        "minimum CU-hours a database can use in a month is about 182.5 (about "
        "730 hours in a month x 0.25 minimum CU size)'. 'At 0.25 CU, 100 "
        "CU-hrs covers about 400 hours of active compute, more than half the "
        "hours in a month.' Defeating scale-to-zero is what makes the quota "
        "exhaust, so this is a quota wall and no relay defeats one."
    )
    neon.pop("keepalive", None)
    neon["relay"] = None
    neon["quote"] = (
        "Free $0 Build and learn free with no time limits and no credit card "
        "required."
    )
    neon["verified_by"] = (
        "me, 2026-10-07 - page fetched HTTP 200, 658102 bytes; the Free-plan "
        "table row and the 182.5 / 400-hours arithmetic quoted in hard_wall "
        "were read from verify/pages/neon_pricing.html. The marketing phrase "
        "'no time limits' is on the same page as the cap it contradicts."
    )
    neon["caveats"] = (
        "RETIERED FROM T2 ON REVIEW. It was counted as always-on-with-a-keepalive "
        "on the reasoning that 'auto-resume on query defeats scale-to-zero'. That "
        "is the mechanism that makes the quota exhaust: a database that never "
        "scales to zero consumes CU-hours for the whole month, and the vendor "
        "puts a 24/7 database at ~182.5 CU-hr against a 100 CU-hr allowance. "
        "Marketing on the same page says 'no time limits' while the table beside "
        "it carries the cap. The scale-to-zero + quota shape is still "
        "instructive, so the row stays in the census as DEAD rather than being "
        "deleted."
    )

    # 2. sdf-free-shell: carries an expiry and a keepalive, so it is T2.
    sdf = row(doc, "sdf-free-shell")
    if sdf["tier"] != "T2":
        sdf["tier"] = "T2"
        changed.append("sdf-free-shell: T1 -> T2")
    sdf["keepalive"] = (
        "one UNIX login per 2 years. The clock is lastlog, so a background job "
        "alone will not keep the account alive; it has to be a real login."
    )
    sdf["verified_by"] = (
        "me, 2026-10-06, quotes read from the fetched bytes at "
        "verify/pages/sdf_members05.html and sdf_members01.html; "
        "verify/claims.json holds both phrases. NOT RE-FETCHABLE FROM EVERY "
        "HOST: sdf.org returns 502/504 through some egress proxies, so on those "
        "hosts verify/claim.py reports both captures as absent. That is the "
        "honest state - the quotes were read from the bytes when they were "
        "fetched, and the bytes are not reproducible from here."
    )
    sdf["caveats"] = (
        "A SHARED HOST, NOT A PRIVATE VM - tens of thousands of users share one "
        "kernel. RETIERED FROM T1: T1 is defined as 'no expiry', and this row "
        "carries a 2-year login expiry plus a keepalive, which is the file's own "
        "definition of T2. The 2-year expiry was also described here as 'the "
        "gentlest idle policy in the census', which was a claim about the other "
        "rows and was not this row's to make. Login expiry runs at ~600 days for "
        "prevalidated accounts. Live banner read by verify/probe.py "
        "(SSH-2.0-OpenSSH_10.4)."
    )

    # 3. ctrl-c-club: a 5-year archive is an expiry, so T2.
    ccc = row(doc, "ctrl-c-club")
    if ccc["tier"] != "T2":
        ccc["tier"] = "T2"
        changed.append("ctrl-c-club: T1 -> T2")
    ccc["keepalive"] = (
        "one login per 5 years. The homepage states the archive policy verbatim: "
        "'we're archiving accounts that have not been logged into in 5 years or "
        "more', with a restore path via the admin address."
    )
    ccc["idle_or_session_limit"] = (
        "5-year inactivity archive: 'we're archiving accounts that have not been "
        "logged into in 5 years or more', restorable on request. No "
        "session-level timeout stated."
    )
    ccc["source"] = "https://ctrl-c.club/"
    ccc["quote"] = (
        "To make room for our active and new users, we're archiving accounts that "
        "have not been logged into in 5 years or more."
    )
    ccc["quote2"] = (
        "Signups are closed for now! Thank you for your interest in Ctrl-C.club! "
        "We're pausing signups to work on some scaling issues. You can still "
        "submit a signup to get on a waitlist."
    )
    ccc["quote3"] = (
        "One gigabyte storage limit (this is not a hard limit: brief, occasional "
        "overages are not a problem)."
    )
    ccc["quote2_page"] = "https://signup.ctrl-c.club/"
    ccc["quote3_page"] = "https://signup.ctrl-c.club/"
    ccc["verified_by"] = (
        "me, 2026-10-06 - fetched ctrl-c.club/ (quote, and the 825-user population "
        "figure), faq.html, signup.ctrl-c.club/ (quote2, quote3) and "
        "system_notice_long.html directly, all HTTP 200, under verify/pages/ as "
        "ctrlc_home, ctrlc_faq, ctrlc_signup, ctrlc_notice. Live banner read by "
        "verify/probe.py."
    )
    ccc["caveats"] = (
        "RETIERED FROM T1 ON REVIEW: T1 says 'no expiry' and this row archives at "
        "5 years. Its quotes were also moved to the pages they are actually on - "
        "the closed-signups text and the 1 GB limit are both on "
        "signup.ctrl-c.club, not on system_notice_long.html, which words the "
        "storage limit differently and differently again. Signups are CURRENTLY "
        "CLOSED (waitlist only). Reachable today only by EXISTING members; a new "
        "person can only join a waitlist. The daemon ban is on Eggdrop bots and "
        "on services DUPLICATING Ctrl-C.club's own, not on all background "
        "processes."
    )

    # 4. serv00: the capture path was wrong; the fetch was not.
    serv = row(doc, "serv00")
    serv["verified_by"] = (
        "me, 2026-10-06 - page fetched HTTP 200, 54173 bytes, quote read from "
        "the fetched bytes at verify/pages/serv00_offer.html (the key in "
        "verify/fetch.py; an earlier revision of this field named a "
        "serv00.html that does not exist, with the same byte count, so the fetch "
        "was real and only the path was wrong)."
    )

    # 5. blinkenshell: quote the table that exists, and say which one it is.
    bl = row(doc, "blinkenshell")
    bl["quote"] = (
        "Type | Free account limit | Supporter account limit | Memory usage "
        "(RSS) | 128 MB | 256 MB | Number of open files | 128 | 128 | Number of "
        "processes | 100 | 100 | SSH sessions | 6 | 6 | Background processes | 2 "
        "| 5"
    )
    bl["quote2"] = (
        "No IRC bots are allowed on free accounts. (Available on Supporter Account "
        "only) You are not allowed to run any server/daemon on free accounts. "
        "This includes bouncers. (Available on Supporter Account only)"
    )
    bl["quote_page"] = "https://blinkenshell.org/docs/resource-limits/"
    bl["quote2_page"] = "https://blinkenshell.org/docs/rules/"
    bl["source"] = "https://blinkenshell.org/docs/resource-limits/"
    bl["verified_by"] = (
        "me, 2026-10-06 - fetched https://blinkenshell.org/docs/resource-limits/ "
        "and https://blinkenshell.org/docs/rules/ directly (both 200, under "
        "verify/pages/ as blinkenshell_limits and blinkenshell_rules) and read "
        "the Free column of the limits table cell by cell. The Free/Supporter "
        "table IS on /docs/resource-limits/; an earlier revision attributed it to "
        "the wiki root, which carries no table at all."
    )
    bl["caveats"] = (
        "CORRECTION TO BOTH THE LAUNCH BASE AND TO THIS ROW'S OWN EARLIER TEXT. "
        "Free Blinkenshell is a screen/tmux host, not an endpoint host: the "
        "limits table's Free column caps memory at 128 MB, processes at 100, SSH "
        "sessions at 6 and background processes at 2, and the rules page says "
        "in so many words that IRC bots, servers/daemons and bouncers are "
        "Supporter-only. The port fact the launch base got wrong is separate: the "
        "host is on 2222, not 22, which is why the launch base's port-22 excuse "
        "never covered it. Earlier revisions of this row quoted a 'Disk Quota "
        "100 MB (x4~)' feature table that exists on no page in verify/pages/; "
        "that text was not in the captures and is not claimed here. Signup also "
        "requires a VOUCH by an existing member."
    )
    bl["spec"] = (
        "Free account limits, from the vendor's own table: 128 MB RSS memory, 100 "
        "processes, 128 open files, 6 SSH sessions, 2 background processes. "
        "screen/tmux detach allowed. Stockholm, online since 2006. SSH on port "
        "2222, not 22."
    )

    # 6. hashbang: quote what the bytes say, drop what no capture supports.
    hb = row(doc, "hashbang")
    # The script's own bytes are:
    #     if [ ! -f "/home/${user}/.keep-account" ]; then
    #         loginctl terminate-user "$user"
    #     fi
    # The statement ends at "$user"; `fi` is on the next line, with no
    # semicolon. The earlier revision of this row read
    # `loginctl terminate-user "$user"; fi` and a first pass at this correction
    # reproduced the same semicolon, which the extended guard caught because the
    # fragment does not occur in the capture. That is what the clause is for.
    hb["quote"] = (
        'DAYS=30 ... if [ ! -f "/home/${user}/.keep-account" ]; then '
        'loginctl terminate-user "$user"\n        fi'
    )
    hb["quote2"] = (
        '/bin/systemctl set-property --runtime "user-${PAM_UID}.slice" \\ '
        "CPUQuota=50% MemoryLimit=512M BlockIOWeight=10"
    )
    hb["quote3"] = None
    hb.pop("quote3", None)
    hb["quote_page"] = (
        "https://raw.githubusercontent.com/hashbang/shell-etc/master/cron.daily/clean-lurkers"
    )
    hb["quote2_page"] = (
        "https://raw.githubusercontent.com/hashbang/shell-server/master/ansible/tasks/security/main.yml"
    )
    hb["verified_by"] = (
        "me, 2026-10-06 - read cron.daily/clean-lurkers and "
        "ansible/tasks/security/main.yml from hashbang/shell-etc and "
        "hashbang/shell-server at GitHub raw (both 200, under verify/pages/ as "
        "hashbang_clean_lurkers and hashbang_limits) and the live /server/stats "
        "API (200, hashbang_stats). An earlier revision of this row quoted a "
        "tmux line that is in no capture; it is withdrawn rather than left as an "
        "unverifiable claim."
    )

    # 7. modelscope: two API responses, two captures, no splice.
    ms = row(doc, "modelscope-studio")
    # An earlier revision pasted both responses into one string with '.cn:' and
    # '.ai:' labels that appear in neither response, so no single capture
    # contains the quote. quote and quote2 are one response each, each in the
    # capture that serves it, which is what makes them traceable.
    ms["quote"] = (
        '{"hardware":[{"name":"platform/2v-cpu-8g-mem","resource_type":"free",'
        '"supported_sdk_types":["gradio","streamlit","docker","static"]}]}'
    )
    ms["quote2"] = (
        '{"hardware":[{"name":"platform/2v-cpu-16g-mem","resource_type":"free",'
        '"supported_sdk_types":["gradio","streamlit","docker","static"]}]}'
    )
    ms["quote_page"] = "https://modelscope.cn/openapi/v1/studios/hardware"
    ms["quote2_page"] = "https://modelscope.ai/openapi/v1/studios/hardware"
    ms["verified_by"] = (
        "me, 2026-10-06 - fetched BOTH unauthenticated OpenAPIs. quote is the "
        "whole of modelscope.cn's response data.hardware[0], captured at "
        "verify/pages/modelscope_hw.html; quote2 is the same field from "
        "modelscope.ai, captured at verify/pages/modelscope_ai_hw.html; each was "
        "stable across 3 runs. The two are separate quotes because they are two "
        "separate responses from two separate sites - an earlier revision "
        "spliced them into one string, which no capture can match."
    )

    # 8. azure F1: the T2 rested on a number absent from its own source.
    az = row(doc, "azure-appservice-f1")
    if az["tier"] != "UNVERIFIED":
        az["tier"] = "UNVERIFIED"
        changed.append("azure-appservice-f1: T2 -> UNVERIFIED")
    az.pop("quote2", None)
    az.pop("keepalive", None)
    az["quote"] = (
        "F1 Free Shared (60 CPU minutes / day) 1 GB 1.00 GB $-"
    )
    az["verified_by"] = (
        "me, 2026-10-07 - the F1 row read from fetched bytes (HTTP 200, 826190 "
        "bytes) at verify/pages/azure_appservice_linux.html. The 20-minute idle "
        "timeout is NOT on that page and is not claimed here; see caveats."
    )
    az["caveats"] = (
        "NOT COUNTED, ON REVIEW. The 512 MB / 5 GB F1 figures repeated in every "
        "older guide are obsolete - the current vendor table says 1 GB RAM / "
        "1.00 GB storage, and that correction stands. But the row was counted as "
        "T2 on a 20-minute idle timeout that its own verified_by said was absent "
        "from the page it cited, so the entire classification rested on a number "
        "with no first-party capture. A T2 whose only claim to being always-on is "
        "unverified is not a T2. The 20-minute figure is documented on "
        "Microsoft's WebJobs docs per a research pass; fetch that page to "
        "promote this row back to T2."
    )

    # 9. rows claiming first-hand with no capture named.
    tt = row(doc, "tilde-town")
    tt["verified_by"] = (
        "me, 2026-10-06 - probed live (banner SSH-2.0-OpenSSH_10.0p2 "
        "Debian-7+deb13u4, in verify/reachability.json) and re-fetched "
        "verify/pages/tilde_town.html, tilde_town_admin.html and "
        "tilde_town_autokick.html. The banner is the capture for the liveness "
        "claim; the pages are the capture for the port policy."
    )
    tg = row(doc, "tilde-green")
    tg["verified_by"] = (
        "me, 2026-10-06 - probed live (banner SSH-2.0-OpenSSH_10.5p1 Debian-1, in "
        "verify/reachability.json) and fetched verify/pages/tilde_green.html and "
        "tilde_green_tos.html, which publishes the hard limits an earlier pass "
        "recorded as unpublished."
    )

    # 10. the file must not contradict itself about what T1 means.
    doc["tiers"]["T1"] = (
        "Always-on as-is. No idle sleep, no hard session cap, no login expiry or "
        "archival. Nothing needs doing to keep it."
    )
    doc["tiers"]["T2"] = (
        "Always-on WITH A KEEPALIVE, or with an expiry long enough to schedule. "
        "Sleeps, scales to zero, is reclaimed when idle, or archives after a "
        "stated period of silence - but a periodic login, a held WebSocket, cron, "
        "or light sustained CPU defeats it. Each row names the exact keepalive."
    )

    # Recompute the counts rather than editing them, so they cannot desync.
    from collections import Counter
    c = Counter(r.get("tier") for r in doc["rows"])
    doc["counts"] = {t: c[t] for t in sorted(
        {"T1", "T2", "T3", "DEAD", "UNVERIFIED"})}

    return changed


def main():
    with open(DATA, encoding="utf-8") as fh:
        doc = json.load(fh)
    before = json.dumps(doc, sort_keys=True)
    changed = apply(doc)
    if not changed:
        print("0 changes applied (already corrected; this script is idempotent)")
        return 0
    after = json.dumps(doc, sort_keys=True)
    if after == before:
        print("0 changes applied (already corrected; this script is idempotent)")
        return 0
    # ensure_ascii=False keeps the quotes readable; the file is opened and
    # written with an explicit encoding so the bytes do not depend on the
    # platform's preferred one. This is the boundary PR #1 half-closed.
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for line in changed:
        print("  applied:", line)
    print(f"{len(changed)} change(s) applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())