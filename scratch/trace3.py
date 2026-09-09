import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=requests.get(base,params=p,timeout=60).json()
        except: time.sleep(2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(2); continue
        return []
    return []
def paginate(module,action,addr,sort="asc",maxp=60,startblock=0):
    out=[]
    for pg in range(1,maxp+1):
        res=call({"module":module,"action":action,"address":addr,"page":pg,"offset":1000,"sort":sort,"startblock":startblock,"endblock":99999999})
        if not res: break
        out.extend(res)
        if len(res)<1000: break
        time.sleep(0.15)
    return out

COL="0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"
n=paginate("account","txlist",COL,sort="asc")
i=paginate("account","txlistinternal",COL,sort="asc")
print(f"COLLECTOR {COL}")
print(f"  normal tx total: {len(n)}   internal total: {len(i)}")
print(f"  active: {U(n[0]['timeStamp'])}  ->  {U(n[-1]['timeStamp'])}")
IN=[t for t in n if t["to"].lower()==COL.lower()]
OUT=[t for t in n if t["from"].lower()==COL.lower()]
print(f"  inbound normal: {len(IN)}  sum {sum(int(t['value']) for t in IN)/1e18:.2f} ETH")
print(f"  outbound normal: {len(OUT)}  sum {sum(int(t['value']) for t in OUT)/1e18:.2f} ETH")
od=collections.Counter(); ov=collections.defaultdict(float)
for t in OUT:
    od[t["to"]]+=1; ov[t["to"]]+=int(t["value"])/1e18
print("  OUTBOUND destinations:")
for d,c in od.most_common(20):
    print(f"    {c:4d}  {ov[d]:12.4f} ETH   {d}")
# largest single inbound (the big vaults)
print("  TOP 10 inbound by value:")
for t in sorted(IN,key=lambda x:-int(x["value"]))[:10]:
    print(f"    {int(t['value'])/1e18:10.4f} ETH  from {t['from']}  {U(t['timeStamp'])}")

# check nametag / label via etherscan
for a in [COL,"0x03cb0021808442ad5efb61197966aef72a1def96"]:
    r=requests.get(base,params={"chainid":1,"module":"account","action":"txlist","address":a,"page":1,"offset":1,"apikey":ESK},timeout=30).json()
    # no label api on free; skip

# Phase-1 (May 2026) — where did those sweeps go? sample May withdrawers
print("\n--- MAY 2026 phase: sample withdrawers & their sweep dest ---")
mi=paginate("account","txlistinternal","0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C",sort="desc",maxp=30)
may=[t for t in mi if "1746057600"<=t["timeStamp"]<"1748736000" and t["from"].lower()=="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"]
print("  May internal-out events seen:", len(may))
seen=set(); dests=collections.Counter()
for t in may[:40]:
    a=t["to"]
    if a in seen: continue
    seen.add(a)
    tl=paginate("account","txlist",a,sort="desc",maxp=2)
    outs=[x for x in tl if x["from"].lower()==a.lower() and int(x["value"])>0]
    if outs: dests[outs[0]["to"]]+=1
print("  May sweep destinations:", dests.most_common(8))
