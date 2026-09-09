import json, requests, time, collections
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
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
def page(mod,act,a):
    out=[];cur=0
    for _ in range(20):
        r=es({"module":mod,"action":act,"address":a,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        nb=int(r[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    return out

PAY="0x9c1065e4a2fe67715ce82772cfc223bd76009451"
# deployers = recipients of paymaster's 0.1 ETH funding
pn=page("account","txlist",PAY)
deployers=sorted(set(t["to"].lower() for t in pn if t["from"].lower()==PAY.lower() and int(t["value"])>0 and t.get("to")))
print(f"paymaster funded {len(deployers)} deployer wallets")

proxies=set(); deployer_of={}
for idx,dep in enumerate(deployers):
    di=page("account","txlistinternal",dep)
    for t in di:
        if t.get("type")=="create" and t.get("from","").lower()==dep and t.get("to"):
            proxies.add(t["to"].lower()); deployer_of[t["to"].lower()]=dep
    # also normal-tx contractAddress field
    dn=page("account","txlist",dep)
    for t in dn:
        if t.get("contractAddress"):
            proxies.add(t["contractAddress"].lower()); deployer_of.setdefault(t["contractAddress"].lower(),dep)
    if idx%40==0: print(f"  {idx}/{len(deployers)} deployers, {len(proxies)} proxies",flush=True)

print(f"\nTotal BAPT-LW20 proxy contracts found: {len(proxies)}")
json.dump({"proxies":sorted(proxies),"deployers":deployers}, open("bapt_lw20_proxies.json","w"))

# intersect with unclaimed vaults
u=dict(json.load(open("unclaimed.json")))
hit=[(a,u[a]) for a in proxies if a in u]
print(f"BAPT proxies that STILL have an unclaimed LastWinner vault: {len(hit)}  totaling {sum(v for _,v in hit):.2f} ETH")
# and with the FULL balances.json (claimed+unclaimed)
b={r["address"].lower():r["balance_eth"] for r in json.load(open("balances.json"))["balances"]}
allhit=[(a,b[a]) for a in proxies if a in b]
print(f"BAPT proxies in balances.json at all: {len(allhit)}  totaling {sum(v for _,v in allhit):.2f} ETH")
json.dump([a for a,_ in hit], open("bapt_stuck_vaults.json","w"))
