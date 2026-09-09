import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.7); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.9); continue
        return res
    return None
def page(mod,act,a,cap=25):
    out=[];cur=0
    for _ in range(cap):
        r=call({"module":mod,"action":act,"address":a,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        nb=int(r[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    s=set();dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"))
        if k in s: continue
        s.add(k);dd.append(t)
    return dd

CA=["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
    "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451",
    "0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f"]
CAS=set(x.lower() for x in CA)
DRAIN_FUNDERS=set(x.lower() for x in ["0x696e01b63189fc476051122c15fcf57b05292cac","0x260d1c4724d15ae5c882d365886fb8cae70a746c",
  "0x86c6391dccf7c73b2119c0fa2630f1fdb5819741","0x0004c3cac4a399d4edae4a157485f2eb28aade92",
  "0x99e03db23a79125f0128288611feedf270a758e4","0x0ec193f5341ac1c7295ef2248ade76a2f8a17dcc"])
CEX={"0x28ffe35688ffffd0659aee2e34778b0ae4e193ad":"Crypto.com","0x46340b20830761efd32832a74d7169b29feb9758":"Binance",
 "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0":"Kraken","0xe93381fb4c4f14bda253907b18fad305d799241a":"Huobi",
 "0xa910f92acdaf488fa6ef02174fb86208ad7722ba":"OKX","0x6cc5f688a315f3dc28a7781717a9a798a59fda7b":"OKX2",
 "0xdfd5293d8e347dfe59e90efd55b2956a1343963d":"Binance16","0x5041ed759dd4afc3a72b8192c143f72f4724081a":"OKX6",
 "0x0d0707963952f2fba59dd06f2b425ace40b492fe":"Gate","0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c":"Gate2",
 "0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2":"FTX","0xd24400ae8bfebb18ca49be86258a3c749cf46853":"Gemini",
 "0xdc76cd25977e0a5ae17155770273a65d5f8b3f9d1":"Kraken2","0xa83b11093c858c86321fbc4c20fe82cdbd58e09e":"Kraken3",
 "0xfe9e8709d3215310075d67e3ed32a380ccf451c8":"Binance5"}
allin=collections.Counter(); allout=collections.Counter(); firstfunders=collections.Counter()
mar14=[]
for a in CA:
    n=page("account","txlist",a); i=page("account","txlistinternal",a)
    al=n+i
    ins=sorted([t for t in al if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if ins: firstfunders[ins[0]["from"].lower()]+=1
    for t in al:
        if t.get("from","").lower()==a.lower() and int(t["value"])>0: allout[(t.get("to") or "").lower()]+=int(t["value"])/1e18
        if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0: allin[t["from"].lower()]+=int(t["value"])/1e18
    for t in al:
        if "2026-03-1" in U(t["timeStamp"]) or "2026-03-2" in U(t["timeStamp"]):
            mar14.append((U(t["timeStamp"]),a[:10],t.get("from","")[:10],(t.get("to") or "")[:10],round(int(t["value"])/1e18,3),t.get("functionName","")[:20]))
print("=== Cluster A first-funders (who seeded them in 2018) ===")
for f,c in firstfunders.most_common(10):
    print(f"  {c}x  {f}  {CEX.get(f,'')}")
print("\n=== Cluster A TOP OUTFLOW destinations (all-time ETH) ===")
for d,v in sorted(allout.items(),key=lambda x:-x[1])[:14]:
    tag=CEX.get(d,"")
    if d in CAS: tag="[Cluster A internal]"
    if d in DRAIN_FUNDERS: tag="*** DRAIN INFRA FUNDER ***"
    print(f"  {v:10.2f} ETH  {d}  {tag}")
print("\n=== Cluster A TOP INFLOW sources (all-time ETH) ===")
for d,v in sorted(allin.items(),key=lambda x:-x[1])[:12]:
    tag=CEX.get(d,"") or ("[Cluster A internal]" if d in CAS else "")
    print(f"  {v:10.2f} ETH  {d}  {tag}")
print("\n=== Cluster A activity around 2026-03-14 (last gasp) ===")
for r in sorted(mar14)[-25:]:
    print("   ", r)
