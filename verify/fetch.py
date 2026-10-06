import urllib.request, ssl, os, json
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
urls = {
 "gcp_free":"https://cloud.google.com/free/docs/free-cloud-features",
 "oracle_alwaysfree":"https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm",
 "northflank_pricing":"https://northflank.com/pricing",
 "hf_spaces_overview":"https://huggingface.co/docs/hub/en/spaces-overview",
 "hf_spaces_gpus":"https://huggingface.co/docs/hub/en/spaces-gpus",
 "render_free":"https://render.com/docs/free",
 "azure_appservice_linux":"https://azure.microsoft.com/en-us/pricing/details/app-service/linux/",
 "supabase_pricing":"https://supabase.com/pricing",
 "sdf_members05":"http://sdf.org/?faq?MEMBERS?05",
 "sdf_members01":"http://sdf.org/?faq?MEMBERS?01",
 "blinkenshell_wiki":"https://blinkenshell.org/wiki/",
 "azure_free_services":"https://azure.microsoft.com/en-us/free/",
 "koyeb_szt":"https://www.koyeb.com/docs/run-and-scale/scale-to-zero",
 "pythonanywhere":"https://www.pythonanywhere.com/user/",
 "serv00":"https://serv00.com/pricing",
 "modelscope_hw":"https://modelscope.cn/openapi/v1/studios/hardware",
 "cf_workers_limits":"https://developers.cloudflare.com/workers/platform/limits/",
 "codespaces":"https://docs.github.com/en/billing/concepts/product-billing/github-codespaces",
 "google_cloud_shell":"https://cloud.google.com/shell/docs/limitations",
 # Final pass 2026-10-06: managed-backend providers, compute-vs-database question.
 "neon_pricing":"https://neon.com/pricing",
 "neon_functions_runtime_limits":"https://neon.com/docs/compute/functions/reference/runtime-limits",
 "neon_functions_websockets":"https://neon.com/docs/compute/functions/websockets",
 "neon_functions_overview":"https://neon.com/docs/compute/functions/overview",
 "turso_pricing":"https://turso.tech/pricing",
 "crdb_pricing":"https://www.cockroachlabs.com/pricing/",
 "crdb_quickstart":"https://www.cockroachlabs.com/docs/cockroachcloud/quickstart.html",
 "crdb_costs":"https://www.cockroachlabs.com/docs/cockroachcloud/costs.html",
 "tidb_pricing":"https://www.pingcap.com/pricing/",
 "upstash_redis_pricing":"https://upstash.com/pricing",
 "upstash_workflow_pricing":"https://upstash.com/pricing/workflow",
 "mongodb_pricing":"https://www.mongodb.com/pricing",
 "aiven_pricing_postgresql":"https://aiven.io/pricing/postgresql",
}
out={}
for k,u in urls.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}),timeout=30,context=ctx)
        b=r.read(); open(f"verify/pages/{k}.html","wb").write(b)
        out[k]={"url":u,"status":r.status,"bytes":len(b)}
    except Exception as e:
        out[k]={"url":u,"error":f"{type(e).__name__}: {str(e)[:100]}"}
print(json.dumps(out,indent=1))
