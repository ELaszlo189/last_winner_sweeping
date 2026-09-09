import requests, time, collections, json, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return r.get("result")
    return []
def page(module,action,addr,sb=0):
    out=[]; cur=sb
    while True:
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    seen=set(); dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"))
        if k in seen: continue
        seen.add(k); dd.append(t)
    return dd

A="0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1"
n=page("account","txlist",A); i=page("account","txlistinternal",A)
IN=[t for t in n+i if t.get("to","").lower()==A.lower() and int(t["value"])>0]
sizes=sorted(int(t["value"])/1e18 for t in IN)
tot=sum(sizes)
print(f"0xa279ffef INBOUND: {len(IN)} legs, {tot:.2f} ETH")
b=collections.Counter()
for s in sizes:
    if s<1e-3:b["<0.001"]+=1
    elif s<1e-2:b["0.001-0.01"]+=1
    elif s<0.05:b["0.01-0.05"]+=1
    elif s<0.2:b["0.05-0.2"]+=1
    elif s<1:b["0.2-1"]+=1
    elif s<10:b["1-10"]+=1
    else:b[">10"]+=1
for k in ["<0.001","0.001-0.01","0.01-0.05","0.05-0.2","0.2-1","1-10",">10"]:
    ssum=sum(s for s in sizes if (k=="<0.001" and s<1e-3) or (k=="0.001-0.01" and 1e-3<=s<1e-2) or (k=="0.01-0.05" and 1e-2<=s<0.05) or (k=="0.05-0.2" and 0.05<=s<0.2) or (k=="0.2-1" and 0.2<=s<1) or (k=="1-10" and 1<=s<10) or (k==">10" and s>=10))
    print(f"   {k:12} {b[k]:6d} legs  {ssum:10.2f} ETH")
print("top 12 inbound legs:")
for t in sorted(IN,key=lambda x:-int(x["value"]))[:12]:
    print(f"   {int(t['value'])/1e18:9.3f} ETH from {t['from']}  {U(t['timeStamp'])}")

# trace 0xe4a219fbed forward
E="0xe4a219fbed16e5c62e335082521f44c508b19191"
en=page("account","txlist",E); ei=page("account","txlistinternal",E)
print(f"\n0xe4a219fbed: {len(en)} normal + {len(ei)} internal")
for t in sorted(en+ei,key=lambda x:int(x["blockNumber"])):
    d="OUT->"+t["to"] if t["from"].lower()==E.lower() else "IN <-"+t["from"]
    print(f"   {U(t['timeStamp'])}  {d}  {int(t['value'])/1e18:.4f} ETH  {t.get('functionName','')[:30]}")

# 0x8d7c20e3 balance + internal out
D="0x8d7c20e3b88bc70246306d9620c2d555448523f7"
dbal=call({"module":"account","action":"balance","address":D})
di=page("account","txlistinternal",D)
dout=[t for t in di if t.get("from","").lower()==D.lower()]
print(f"\n0x8d7c20e3: balance now {int(dbal)/1e18 if isinstance(dbal,str) else '?'} ETH ; internal-out legs {len(dout)} sum {sum(int(t['value']) for t in dout)/1e18:.3f}")
for t in sorted(dout,key=lambda x:-int(x['value']))[:6]:
    print(f"   OUT {int(t['value'])/1e18:.4f} -> {t['to']} {U(t['timeStamp'])}")
