import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
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

# the 11 addrs that sent to BOTH the Apr-30 drainer AND appear as our LW withdrawers
ds=set(json.load(open("drainer_senders.json"))["senders"])
camp=json.load(open("camp_norm.json"))
lww=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
overlap=sorted(ds & lww)
print(f"{len(overlap)} addresses that BOTH sent to Apr-30 drainer 0xA707... AND called LastWinner withdraw() in our set:")
for a in overlap:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":6,"sort":"desc"})
    n=n if isinstance(n,list) else []; nd=nd if isinstance(nd,list) else []
    fb=int(n[0]["blockNumber"]) if n else 0
    # did anything sweep this addr BEFORE 2026? (early key compromise test)
    pre26_out=[t for t in n if t["from"].lower()==a.lower() and int(t["value"])>0 and t["timeStamp"]<"1735689600"]
    print(f"  {a}  first={U(n[0]['timeStamp']) if n else '?'}(blk{fb})  last={U(nd[0]['timeStamp']) if nd else '?'}  ntx={len(n)}  pre-2026 outgoing ETH txs={len(pre26_out)}")

# Was the broader LW fleet EVER swept before 2026? sample 40 known trackA members, check for any 2019-2025 full-balance-out event
ta=json.load(open("trackA_senders.json")); members=list(set(ta["a279"])|set(ta["8d7c"]))[:40]
early_sweeps=0
print("\nchecking 40 fleet members for pre-2026 sweep activity:")
for a in members:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":50,"sort":"asc"})
    if not isinstance(n,list) or not n: continue
    outs=[t for t in n if t["from"].lower()==a.lower() and int(t["value"])>0]
    yrs=collections.Counter(U(t["timeStamp"])[:4] for t in outs)
    gap = [y for y in yrs if "2020"<=y<="2025"]
    if gap: early_sweeps+=1
print(f"  {early_sweeps}/40 had ANY outgoing ETH tx in 2020-2025 (0 => keys stayed dormant/uncompromised until 2026)")
