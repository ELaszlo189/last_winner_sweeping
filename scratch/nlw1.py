import json, requests, time, collections, datetime as dt, random
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
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
d=json.load(open("drained_eoas.json"))
nlw=[r["address"] for r in d if r["drained_via"]=="looseETH" and r["lw_participant"]=="no"]
lw =[r["address"] for r in d if r["lw_participant"]=="yes"]
random.seed(2); random.shuffle(nlw); random.shuffle(lw)
SN=nlw[:260]; SL=lw[:160]
def profile(addrs, label):
    rows=[]; funders=collections.Counter(); months=collections.Counter(); ntxc=collections.Counter(); fhash=collections.Counter()
    for idx,a in enumerate(addrs):
        if idx%25==0: print(f"  {label} {idx}/{len(addrs)}",flush=True)
        n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":12,"sort":"asc"}) or []
        i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":12,"sort":"asc"}) or []
        n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
        allin=sorted([t for t in n+i if t.get("to","").lower()==a.lower() and int(t["value"])>0],
                     key=lambda x:(int(x["blockNumber"]),int(x.get("transactionIndex",0) or 0)))
        if not n and not allin: continue
        f = allin[0]["from"].lower() if allin else None
        fm = U(allin[0]["timeStamp"]) if allin else (U(n[0]["timeStamp"]) if n else "?")
        funders[f]+=1; months[fm]+=1
        if allin: fhash[allin[0]["hash"]]+=1
        ntxc["1-5" if len(n)<=5 else "6-20" if len(n)<=20 else "21+"]+=1
        rows.append((a,f,fm,len(n)))
    print(f"\n=== {label} (n={len(rows)}) ===")
    print("first-funded month:", dict(sorted(months.items())))
    print("tx-count buckets:", ntxc.most_common())
    print(f"distinct first-funders: {len(funders)} for {len(rows)} addrs")
    for fdr,c in funders.most_common(15): print(f"   {c:4d}  {fdr}")
    print("batch funding-tx hashes (>1 addr same tx):", [(h[:14],c) for h,c in fhash.most_common(8) if c>1])
    return funders
fn=profile(SN,"NON-LW pure-looseETH"); fl=profile(SL,"LW-participant")
common=set(fn)&set(fl)
print(f"\n=== FUNDER OVERLAP: {len(common)} in BOTH ===")
for f in sorted(common,key=lambda x:-(fn[x]+fl[x]))[:20]:
    print(f"   {f}   nonLW:{fn[f]}  LW:{fl[f]}")
json.dump({"nlw_funders":dict(fn),"lw_funders":dict(fl)},open("nlw_vs_lw_funders.json","w"))
