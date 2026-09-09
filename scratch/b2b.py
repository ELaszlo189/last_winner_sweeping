import json, requests, time, collections, datetime as dt, csv
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.8); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.0); continue
        return res
    return None

ta=json.load(open("trackA_senders.json"))
aS=set(ta["a279"]); dS=set(ta["8d7c"])
FLEET_FUNDERS=set(x.lower() for x in [
 "0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914",
 "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
 "0x73957709695e73fd175582105c44743cf0fb6f2f","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1",
 "0xb2a48f542dc56b89b24c04076cbe565b3dc58e7b","0x6e0bf5fd188f59cc8b64569d211912d8248d883d",
 "0x03cb0021808442ad5efb61197966aef72a1def96"])
u=json.load(open("unclaimed.json"))
TOP=[a for a,v in u[:220]]; BAL=dict(u)
rows=[]; cls=collections.Counter(); clseth=collections.defaultdict(float)
for idx,a in enumerate(TOP):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":50,"sort":"asc"})
    n=n if isinstance(n,list) else []
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"desc"})
    nd=nd if isinstance(nd,list) else []
    code=call({"module":"proxy","action":"eth_getCode","address":a})
    isC=isinstance(code,str) and len(code)>2
    fb=int(n[0]["blockNumber"]) if n else 0
    fd=U(n[0]["timeStamp"]) if n else "?"
    ld=U(nd[0]["timeStamp"]) if nd else "?"
    funder=n[0]["from"].lower() if n else None
    launch = 6094000<=fb<=6140000
    ff = funder in FLEET_FUNDERS
    trackA = a in aS or a in dS
    dormant = ld<"2026-01-01"
    active26 = ld>="2026-01-01"
    if isC: c="CONTRACT_stuck"
    elif trackA: c="FLEET_trackA_swept"
    elif ff: c="FLEET_bankroll_funded"
    elif active26 and not launch: c="ACTIVE_2026_maybe_independent"
    elif launch and dormant: c="cohort_dormant_unattributed"
    else: c="other"
    cls[c]+=1; clseth[c]+=BAL[a]
    rows.append(dict(address=a,bal=round(BAL[a],4),is_contract=isC,first=fd,last=ld,ntx=len(n),
                     funder=funder,launch_week=launch,fleet_funder=ff,trackA=trackA,cls=c))
    if idx%40==0: print(f"{idx}/{len(TOP)}",flush=True)
with open("unclaimed_top_classified.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
tot=sum(BAL[a] for a in TOP)
print(f"\n=== top {len(TOP)} unclaimed addrs, {tot:.1f} ETH ===")
for c,nn in cls.most_common():
    print(f"  {nn:4d}  {clseth[c]:8.2f} ETH  {clseth[c]/tot*100:4.1f}%  {c}")
# trackA overlap across ALL unclaimed (free, no api)
allun=set(a for a,_ in u)
ov_a=len(allun & aS); ov_d=len(allun & dS)
print(f"\nALL {len(allun)} unclaimed addrs: {ov_a} also swept loose-ETH to 0xa279ffef, {ov_d} to 0x8d7c20e3, {len(allun&(aS|dS))} to either")
oveth=sum(v for a,v in u if a in aS or a in dS)
print(f"  their Mar-31 unclaimed vault total: {oveth:.1f} ETH  (of {sum(v for _,v in u):.1f})")
