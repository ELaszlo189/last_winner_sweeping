import requests, time, collections, json, datetime as dt
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
ta=json.load(open("trackA_senders.json")); trackA=set(ta["a279"])|set(ta["8d7c"])
bal={r["address"].lower():r["balance_eth"] for r in json.load(open("balances.json"))["balances"]}
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"

# cf49 funder provenance
for a,lab in [("0x99e03db23a79125f0128288611feedf270a758e4","0xcf49c8fb (burst-2 dispatcher) funder")]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":10,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"desc"})
    lwx=call({"module":"account","action":"txlist","address":a,"page":1,"offset":200,"sort":"asc"})
    n=n if isinstance(n,list) else []; nd=nd if isinstance(nd,list) else []
    lwhits=sum(1 for t in (lwx if isinstance(lwx,list) else []) if t.get("to","").lower()==LW)
    ins=[t for t in n if t.get("to","").lower()==a.lower() and int(t["value"])>0]
    print(f"{lab}: {a}")
    print(f"  first_tx={U(n[0]['timeStamp']) if n else '?'}  last={U(nd[0]['timeStamp']) if nd else '?'}  LW_txs={lwhits}  trackA={a in trackA}  had_vault={a in bal}")
    print(f"  first funded by {ins[0]['from'] if ins else '?'}")

# where do the 16 workers forward their collected ETH?
workers=json.load(open("cf49_workers.json"))
fwd=collections.Counter(); fwdv=collections.defaultdict(float)
for w in workers:
    n=call({"module":"account","action":"txlist","address":w,"page":1,"offset":1000,"sort":"asc"})
    n=n if isinstance(n,list) else []
    # big outbound (consolidation), not the 0.003 drips
    big=[t for t in n if t["from"].lower()==w.lower() and int(t["value"])/1e18>0.05]
    for t in big:
        fwd[t["to"].lower()]+=1; fwdv[t["to"].lower()]+=int(t["value"])/1e18
print("\n16 workers -> consolidation destinations (>0.05 ETH legs):")
for d,c in fwd.most_common(12):
    tag = " <-- burst-2 collector" if d=="0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52" else ""
    print(f"  {c:3d} legs  {fwdv[d]:8.3f} ETH  {d}{tag}")
