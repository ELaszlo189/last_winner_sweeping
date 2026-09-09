import json, requests, time, collections, datetime as dt, csv
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.6); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.8); continue
        return res
    return None
ta=json.load(open("trackA_senders.json")); aS=set(ta["a279"]); dS=set(ta["8d7c"])
FF=set(x.lower() for x in ["0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0x73957709695e73fd175582105c44743cf0fb6f2f","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x6e0bf5fd188f59cc8b64569d211912d8248d883d","0x03cb0021808442ad5efb61197966aef72a1def96"])
u=json.load(open("unclaimed.json")); BAL=dict(u); TOP=[a for a,v in u[:150]]
rows=[]; cls=collections.Counter(); clseth=collections.defaultdict(float)
for idx,a in enumerate(TOP):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":30,"sort":"asc"}) or []
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":3,"sort":"desc"}) or []
    fb=int(n[0]["blockNumber"]) if n else 0
    fd=U(n[0]["timeStamp"]) if n else "?"; ld=U(nd[0]["timeStamp"]) if nd else "?"
    funder=n[0]["from"].lower() if n else None
    launch=6094000<=fb<=6140000
    ta_hit=a in aS or a in dS
    if ta_hit: c="FLEET (track-A swept)"
    elif funder in FF: c="FLEET (bankroll-funded)"
    elif ld>="2026-04-01" and not ta_hit: c="ACTIVE-2026 (indep?)"
    elif launch and ld<"2026-01-01": c="cohort dormant, unattributed"
    elif ld<"2020-01-01": c="dormant since 2018-19, unattributed"
    else: c="other"
    cls[c]+=1; clseth[c]+=BAL[a]
    rows.append(dict(address=a,eth=round(BAL[a],4),first=fd,last=ld,ntx=len(n),funder=funder,launch=launch,trackA=ta_hit,cls=c))
    if idx%30==0: print(idx,flush=True)
csv.DictWriter(open("unclaimed_top150.csv","w",newline=""),fieldnames=list(rows[0].keys())).writerows([dict(zip(rows[0],rows[0]))]) if False else None
with open("unclaimed_top150.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
tot=sum(BAL[a] for a in TOP)
print(f"\ntop {len(TOP)} unclaimed by value = {tot:.1f} ETH")
for c,nn in cls.most_common(): print(f"  {nn:3d}  {clseth[c]:8.2f} ETH ({clseth[c]/tot*100:4.1f}%)  {c}")
print("\ntop 15:")
for r in rows[:15]: print(f"  {r['eth']:9.3f}  first={r['first']} last={r['last']} ntx={r['ntx']:3d} trackA={r['trackA']}  {r['cls']}")
