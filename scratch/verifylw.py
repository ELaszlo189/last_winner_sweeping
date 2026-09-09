import json, requests, time, collections, random, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.5); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.7); continue
        return res
    return None
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
d=json.load(open("drained_eoas.json"))
grp=[r["address"] for r in d if r["drained_via"]=="looseETH" and r["lw_participant"]=="no"]  # the 17,418
random.seed(11); random.shuffle(grp); SAMP=grp[:500]
touched=0; not_touched=[]; by_year=collections.Counter(); how=collections.Counter()
for idx,a in enumerate(SAMP):
    if idx%50==0: print(f"  {idx}/{len(SAMP)}  (touched {touched})",flush=True)
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":10000,"sort":"asc"}) or []
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":10000,"sort":"asc"}) or []
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    lw_as_to   = [t for t in n if (t.get("to") or "").lower()==LW]
    lw_in_intl = [t for t in i if (t.get("to") or "").lower()==LW or t.get("from","").lower()==LW]
    if lw_as_to or lw_in_intl:
        touched+=1
        if lw_as_to: how["direct call (normal tx to LW)"]+=1
        elif lw_in_intl: how["only via internal (proxy/payout)"]+=1
        yr = U((lw_as_to or lw_in_intl)[0]["timeStamp"])
        by_year[yr]+=1
    else:
        not_touched.append(a)
print(f"\n=== {len(SAMP)} sampled from the 17,418 'looseETH-only, no-vault' group ===")
print(f"INTERACTED with LastWinner (ever): {touched}/{len(SAMP)}  ({touched*100//len(SAMP)}%)")
print(f"NO detectable LastWinner interaction: {len(not_touched)}/{len(SAMP)}")
print("how they touched LW:", how.most_common())
print("year of first LW interaction:", dict(sorted(by_year.items())))
print("\nsample of the NON-touchers (first 15):", not_touched[:15])
json.dump(not_touched, open("drained_no_lw_interaction.json","w"))
