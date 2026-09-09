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
def page(module,action,addr):
    out=[]; cur=0
    while True:
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"]); cur = nb if nb!=cur else nb+1
    seen=set(); dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"))
        if k in seen: continue
        seen.add(k); dd.append(t)
    return dd

# withdraw EOAs from the full campaign pull
camp=json.load(open("camp_norm.json"))
weoas=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
print("campaign withdraw() EOAs:", len(weoas))

for name,a in [("0x8d7c20e3","0x8d7c20e3b88bc70246306d9620c2d555448523f7"),
               ("0xa279ffef","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1")]:
    n=page("account","txlist",a); i=page("account","txlistinternal",a)
    al=n+i
    IN=[t for t in al if t.get("to","").lower()==a.lower() and int(t["value"])>0]
    OUT=[t for t in al if t.get("from","").lower()==a.lower() and int(t["value"])>0]
    inv=sum(int(t["value"]) for t in IN)/1e18; outv=sum(int(t["value"]) for t in OUT)/1e18
    senders=collections.Counter(t["from"].lower() for t in IN)
    from_weoa=sum(1 for t in IN if t["from"].lower() in weoas)
    dests=collections.defaultdict(float); dcount=collections.Counter()
    for t in OUT: dests[t["to"].lower()]+=int(t["value"])/1e18; dcount[t["to"].lower()]+=1
    span=f"{U(al[0]['timeStamp'])} .. {U(al[-1]['timeStamp'])}" if al else "?"
    print(f"\n===== {name}  {a}")
    print(f"  span {span}   tx: {len(n)} normal + {len(i)} internal")
    print(f"  IN : {len(IN)} legs, {inv:.3f} ETH, {len(senders)} unique senders; {from_weoa} legs are from campaign withdraw()-EOAs")
    print(f"  IN size: p50={sorted(int(t['value']) for t in IN)[len(IN)//2]/1e18:.5f}  max={max(int(t['value']) for t in IN)/1e18:.3f}" if IN else "")
    print(f"  OUT: {len(OUT)} legs, {outv:.3f} ETH, to {len(dests)} addrs:")
    for d,v in sorted(dests.items(),key=lambda x:-x[1])[:10]:
        print(f"     {v:10.3f} ETH ({dcount[d]}x)  {d}")
    # top senders
    print("  top senders:")
    for sdr,c in senders.most_common(6):
        print(f"     {c:4d}x  {sdr}  ({'campaign-EOA' if sdr in weoas else 'other'})")
