import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=30).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.2); continue
        return res
    return None
def page(mod,act,a):
    out=[];cur=0
    for _ in range(40):
        r=call({"module":mod,"action":act,"address":a,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        nb=int(r[-1]["blockNumber"]); cur=nb+1 if nb>=cur else cur+1
    s=set();dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"))
        if k in s: continue
        s.add(k);dd.append(t)
    return dd

DR="0xa707034429c8e4e01df056c0cbcf478f0fbefad7"
n=page("account","txlist",DR); i=page("account","txlistinternal",DR)
IN=[t for t in n+i if (t.get("to") or "").lower()==DR and int(t["value"])>0]
OUT=[t for t in n+i if t.get("from","").lower()==DR and int(t["value"])>0]
inbound_senders = collections.Counter(t["from"].lower() for t in IN)
print(f"0xA707: {len(n)} normal + {len(i)} internal ; active {U(n[0]['timeStamp'])}..{U(n[-1]['timeStamp'])}")
print(f"  IN: {len(IN)} legs, {sum(int(t['value']) for t in IN)/1e18:.2f} ETH, {len(inbound_senders)} unique senders")
print(f"  OUT: {len(OUT)} legs, {sum(int(t['value']) for t in OUT)/1e18:.2f} ETH")
od=collections.defaultdict(float)
for t in OUT: od[(t.get('to') or '').lower()]+=int(t["value"])/1e18
print("  OUT destinations:")
for d,v in sorted(od.items(),key=lambda x:-x[1]): print(f"    {v:9.3f} ETH  {d}")
# who funded 0xA707 (gas)?
firstin=sorted(IN,key=lambda x:int(x["blockNumber"]))
gas=[t for t in n if (t.get("to") or "").lower()==DR]
print(f"  first inbound: {U(firstin[0]['timeStamp'])} {int(firstin[0]['value'])/1e18} ETH from {firstin[0]['from']}")

json.dump({"senders":sorted(inbound_senders)}, open("a707_senders_full.json","w"))

# ---- INTERSECTIONS ----
a707 = set(inbound_senders)
drained = set(r["address"].lower() for r in json.load(open("drained_eoas.json")))
lw_callers = set(json.load(open("lw_senders_ckpt_slim.json"))["senders"])
vaults = set(r["address"].lower() for r in json.load(open("balances.json"))["balances"])
ta = json.load(open("trackA_senders.json")); trackA=set(ta["a279"])|set(ta["8d7c"])
camp = json.load(open("camp_norm.json"))
wcallers = set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))

print(f"\n=== 0xA707 senders ({len(a707)}) intersections ===")
print(f"  ∩ our drained set (44,014):           {len(a707 & drained)}")
print(f"  ∩ our 2026 withdraw() callers:        {len(a707 & wcallers)}")
print(f"  ∩ our track-A loose-ETH sweep victims:{len(a707 & trackA)}")
print(f"  ∩ LastWinner callers (63k):           {len(a707 & lw_callers)}")
print(f"  ∩ LastWinner pID/vault holders (65k): {len(a707 & vaults)}")
shared = sorted(a707 & (drained | wcallers | trackA))
print(f"\n  UNION of shared with our operation: {len(shared)} addresses")
json.dump(shared, open("a707_shared_addresses.json","w"))
