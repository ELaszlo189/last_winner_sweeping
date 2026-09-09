import requests, time, collections, json, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(7):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.3)
    return []
def page(module,action,addr,cap=30):
    out=[]; cur=0
    for _ in range(cap):
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    s=set(); dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"))
        if k in s: continue
        s.add(k); dd.append(t)
    return dd

HUB="0xcf49c8fb434af3a2cde64fe3907ce27bf1317762"
n=page("account","txlist",HUB); i=page("account","txlistinternal",HUB)
al=n+i
IN=[t for t in al if t.get("to","").lower()==HUB and int(t["value"])>0]
OUT=[t for t in al if t.get("from","").lower()==HUB and int(t["value"])>0]
print(f"HUB 0xcf49c8fb: {len(n)} normal + {len(i)} internal;  active {U(al[0]['timeStamp'])} .. {U(al[-1]['timeStamp'])}")
print(f"  IN  {len(IN)} legs {sum(int(t['value']) for t in IN)/1e18:.3f} ETH from {len(set(t['from'].lower() for t in IN))} addrs")
print(f"  OUT {len(OUT)} legs {sum(int(t['value']) for t in OUT)/1e18:.3f} ETH to {len(set(t['to'].lower() for t in OUT))} addrs")
# funder
fin=sorted(IN,key=lambda x:int(x["blockNumber"]))
print(f"  first funded by {fin[0]['from']} ({int(fin[0]['value'])/1e18:.3f} ETH, {U(fin[0]['timeStamp'])})")
# outbound value histogram
vc=collections.Counter(round(int(t["value"])/1e18,4) for t in OUT)
print("  outbound amount histogram:", vc.most_common(8))
# recipients
rc=collections.defaultdict(lambda:[0,0.0])
for t in OUT:
    rc[t["to"].lower()][0]+=1; rc[t["to"].lower()][1]+=int(t["value"])/1e18
recips=sorted(rc.items(), key=lambda x:-x[1][1])
print(f"\n  {len(recips)} distinct recipients (worker fleet):")
for a,(c,v) in recips:
    print(f"    {a}  {c}x  {v:.3f} ETH")
json.dump([a for a,_ in recips], open("cf49_workers.json","w"))

# profile each worker: gas-dripper? collector? both?
camp=json.load(open("camp_norm.json"))
lww=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
print("\n  --- worker roles ---")
for a,(c,v) in recips[:20]:
    wn=page("account","txlist",a,cap=6); wi=page("account","txlistinternal",a,cap=6)
    wal=wn+wi
    o=[t for t in wal if t.get("from","").lower()==a.lower() and int(t["value"])>0]
    ins=[t for t in wal if t.get("to","").lower()==a.lower() and int(t["value"])>0]
    # gas drips = many small ~0.003 outbound to distinct addrs
    drips=[t for t in o if 0.0005<int(t["value"])/1e18<0.02]
    drip_targets=set(t["to"].lower() for t in drips)
    drip_to_victims=len(drip_targets & lww)
    # collector = many inbound from distinct addrs
    in_from=set(t["from"].lower() for t in ins)
    in_from_victims=len(in_from & lww)
    bal=call({"module":"account","action":"balance","address":a})
    balv=int(bal)/1e18 if isinstance(bal,str) and bal.lstrip('-').isdigit() else 0
    span=f"{U(wal[0]['timeStamp'])[:10]}..{U(wal[-1]['timeStamp'])[:10]}" if wal else "?"
    print(f"    {a} bal={balv:.3f} span={span} | IN {len(ins)} legs from {len(in_from)} ({in_from_victims} victims) | OUT {len(o)}; drips {len(drips)} to {len(drip_targets)} ({drip_to_victims} victims)")
