const fs=require('fs'),path=require('path');
const engine="/workspace/peli-cloud/references/battleships/site/engine.js";
const cards=["/workspace/peli-cloud/references/battleships/research/cards/zeabur.json", "/workspace/peli-cloud/references/battleships/research/cards/zenrows.json", "/workspace/peli-cloud/references/battleships/research/cards/zhipu.json", "/workspace/peli-cloud/references/battleships/research/cards/zibra-labs.json", "/workspace/peli-cloud/references/battleships/research/cards/zipbox.json", "/workspace/peli-cloud/references/battleships/research/cards/zo-computer.json"];
const outDir="/workspace/peli-cloud/data/.crosscheck";
const MODES=["strict", "soft"];
try{require(engine);}catch(e){process.stderr.write('engine load failed: '+e+'\n');process.exit(3);}
const W={"vcpu": 2, "ram": 4, "disk": 10, "os": "linux", "arch": "any", "gpu": "none", "gpuCount": 1, "sessions": 1000, "sessionMin": 10, "concurrency": 20, "alwaysOn": 0, "cpuUtil": 0.3, "ramUtil": 0.5, "idleShare": 0.2, "cpuPeakUtil": 0.6, "ramPeakUtil": 0.7, "snapshotGiB": 0, "egress": 10, "ipv4": 0, "seats": 1, "persistentDisk": false, "pooled": false, "classes": null, "showZero": false, "internet": "open"},OPTS={"required": [], "maxAccess": 3, "region": "any", "idleSuspend": true, "idleCapture": 1, "overrides": {}, "sizing": "min"};
for(const c of cards){
  const id=path.basename(c,'.json');
  let card;try{card=JSON.parse(fs.readFileSync(c,'utf8'));}catch(e){for(const m of MODES){fs.writeFileSync(path.join(outDir,m+'_'+id+'.out.json'),JSON.stringify({id:id,error:'card parse: '+e}));}continue;}
  for(const m of MODES){
    const rec={id:id,mode:m};
    try{
      const r = (m==='strict') ? PM.priceCard(card,W,OPTS) : PM.priceSoft(card,W,OPTS);
      rec.eligible=!!r.eligible;
      rec.total=(r&&typeof r.total==='number')?r.total:null;
      rec.breakdown=(r&&r.breakdown)?r.breakdown:null;
      if(r&&r.unknowns)rec.unknowns=r.unknowns;
      if(r&&r.compromises)rec.compromises=r.compromises;
      if(r&&r.caveats)rec.caveats=r.caveats;
      if(r&&r.reasons)rec.reasons=r.reasons;
      if(r&&r.planLimits)rec.planLimits=r.planLimits;
    }catch(e){rec.error=String(e&&e.message?e.message:e);}
    fs.writeFileSync(path.join(outDir,m+'_'+id+'.out.json'),JSON.stringify(rec));
  }
}