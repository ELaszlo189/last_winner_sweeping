import json, requests, time, collections, datetime as dt, random
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(8):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.4)
    return None
u=json.load(open("unclaimed.json"))
random.seed(1)
# stratified sample
tiers={">=1":[a for a,v in u if v>=1], "0.1-1":[a for a,v in u if 0.1<=v<1],
       "0.01-0.1":[a for a,v in u if 0.01<=v<0.1], "<0.01":[a for a,v in u if v<0.01]}
BAL=dict(u)
samp=[]
for k,lst in tiers.items():
    random.shuffle(lst); samp+= [(k,a) for a in lst[:70]]
print("sampling", len(samp))
res=collections.Counter(); reseth=collections.defaultdict(float)
for idx,(tier,a) in enumerate(samp):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":6,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":4,"sort":"desc"})
    n=n or []; nd=nd or []
    fy = U(n[0]["timeStamp"])[:4] if n else "?"
    ly = U(nd[0]["timeStamp"])[:7] if nd else "?"
    hello = any(t.get("input","").startswith("0x48656c6c") for t in n+nd)
    if fy=="2018" and ly<"2026-01":
        c="dormant since 2018-19 (real abandoned)"
    elif fy=="2018" and ly>="2026-01" and hello:
        c="2018 addr, REACTIVATED 2026 w/ Hello-spam"
    elif fy=="2018" and ly>="2026-01":
        c="2018 addr, some 2026 activity"
    elif fy in ("2026","2025"):
        c="address FIRST created 2025-26 (staged/rebound)"
    else:
        c=f"other ({fy}/{ly})"
    res[c]+=1; reseth[c]+=BAL[a]
    if idx%40==0: print(idx,flush=True)
tot=sum(BAL[a] for _,a in samp)
print(f"\n=== {len(samp)} sampled unclaimed addrs ({tot:.1f} ETH sampled) ===")
for c,nn in res.most_common():
    print(f"  {nn:4d}  {reseth[c]:8.2f} ETH  {c}")
