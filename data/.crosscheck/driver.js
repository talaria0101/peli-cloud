
const path = process.argv[2];
const cardFile = process.argv[3];
const outFile = process.argv[4];
require(path);
const card = require(cardFile);
const W = {"vcpu": 2, "ram": 4, "disk": 10, "os": "linux", "arch": "any", "gpu": "none", "gpuCount": 1, "sessions": 1000, "sessionMin": 10, "concurrency": 20, "alwaysOn": 0, "cpuUtil": 0.3, "ramUtil": 0.5, "idleShare": 0.2, "cpuPeakUtil": 0.6, "ramPeakUtil": 0.7, "snapshotGiB": 0, "egress": 10, "ipv4": 0, "seats": 1, "persistentDisk": false, "pooled": false, "classes": null, "showZero": false, "internet": "open"};
const OPTS = {"required": [], "maxAccess": 3, "region": "any", "idleSuspend": true, "idleCapture": 1, "overrides": {}, "sizing": "min"};
const out = {};
try {
  const r = PM.priceSoft(card, W, OPTS);
  out.eligible = !!r.eligible;
  out.total = (r && typeof r.total === 'number') ? r.total : null;
  out.breakdown = (r && r.breakdown) ? r.breakdown : null;
  out.reasons = (r && r.reasons) ? r.reasons : null;
  out.unknowns = (r && r.unknowns) ? r.unknowns : null;
} catch (e) {
  out.error = String(e && e.stack ? e.stack.split('\n').slice(0,3).join(' | ') : e);
}
require('fs').writeFileSync(outFile, JSON.stringify(out));
