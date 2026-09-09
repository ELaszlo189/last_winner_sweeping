import json, requests, time, collections
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
S=requests.Session()
def es(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.2); continue
        return res
    return None
def allpages(mod,act,a,maxp=12):
    out=[]; cur=0
    for _ in range(maxp):
        r=es({"module":mod,"action":act,"address":a,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        nb=int(r[-1]["blockNumber"])
        cur = nb+1 if nb>cur else cur+1
    # dedupe
    s=set();dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"))
        if k in s: continue
        s.add(k);dd.append(t)
    return dd

PAY="0x9c1065e4a2fe67715ce82772cfc223bd76009451"
n=allpages("account","txlist",PAY); i=allpages("account","txlistinternal",PAY)
recips=sorted(set((t.get("to") or "").lower() for t in n+i if t.get("from","").lower()==PAY.lower() and int(t["value"])>0 and t.get("to")))
print(f"paymaster {PAY}: {len(n)} norm + {len(i)} intl ; funded {len(recips)} distinct recipients")

proxies=set()
for idx,dep in enumerate(recips):
    di=allpages("account","txlistinternal",dep,maxp=4)
    dn=allpages("account","txlist",dep,maxp=4)
    for t in di:
        if t.get("type")=="create" and t.get("to"): proxies.add(t["to"].lower())
    for t in dn:
        if t.get("contractAddress"): proxies.add(t["contractAddress"].lower())
    if idx%40==0: print(f"  {idx}/{len(recips)} deployers -> {len(proxies)} proxies",flush=True)
print(f"\nBAPT-LW20 proxy contracts: {len(proxies)}")
json.dump(sorted(proxies), open("bapt_lw20_proxies.json","w"))

u=dict(json.load(open("unclaimed.json")))
b={r["address"].lower():r["balance_eth"] for r in json.load(open("balances.json"))["balances"]}
hit=[(a,u[a]) for a in proxies if a in u]
allhit=[(a,b[a]) for a in proxies if a in b]
print(f"BAPT proxies with an UNCLAIMED vault now: {len(hit)}  = {sum(v for _,v in hit):.2f} ETH  (PERMANENTLY STUCK)")
print(f"BAPT proxies in balances.json total: {len(allhit)} = {sum(v for _,v in allhit):.2f} ETH")
json.dump([a for a,_ in hit], open("bapt_stuck_vaults.json","w"))
