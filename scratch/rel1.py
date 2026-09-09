import requests, time, collections, json, datetime as dt, csv
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.2); continue
        return []
    return []

COTOKEN="0x03cb0021808442ad5efb61197966aef72a1def96".lower()
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c".lower()

norm=json.load(open("norm.json"))
swept=list(dict.fromkeys(t["from"] for t in norm))   # unique swept EOAs from Aug31-Sep6 window
print("unique swept addrs in window:", len(swept))
sample=swept[:180]

rows=[]
funders=collections.Counter()
cotoken_hits=0
for idx,a in enumerate(sample):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":25,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":25,"sort":"asc"})
    ins=sorted([t for t in (list(n)+list(i)) if t.get("to","").lower()==a.lower() and int(t["value"])>0],
               key=lambda x:(int(x["blockNumber"]), int(x.get("transactionIndex",0) or 0)))
    f = ins[0]["from"].lower() if ins else None
    fdate = U(ins[0]["timeStamp"]) if ins else None
    fval = int(ins[0]["value"])/1e18 if ins else 0
    funders[f]+=1
    # coToken interaction anywhere in first 25 txs?
    seen_ct = any(COTOKEN in (t.get("to","").lower(), t.get("from","").lower()) for t in list(n)+list(i))
    if seen_ct: cotoken_hits+=1
    first_tx_date = U(n[0]["timeStamp"]) if n else "?"
    rows.append({"addr":a,"first_tx":first_tx_date,"funder":f,"funder_date":fdate,"fund_eth":round(fval,5),
                 "ntx_first25": len(n),"cotoken_linked":seen_ct})
    if idx%30==0: print(f"  {idx}/{len(sample)} ...", flush=True)

with open("relatedness_sample.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

print(f"\ncoToken-linked in first 25 txs: {cotoken_hits}/{len(sample)}")
print(f"\ndistinct first-funders: {len(funders)}  (for {len(sample)} sampled addrs)")
print("TOP first-funders:")
for f,c in funders.most_common(20):
    print(f"   {c:4d}  {f}")
# funder date distribution
fd=collections.Counter(r["funder_date"][:7] if r["funder_date"] else "?" for r in rows)
print("\nfunder month distribution:", dict(sorted(fd.items())))
# first-tx month distribution
ftd=collections.Counter(r["first_tx"][:7] for r in rows)
print("first-tx month distribution:", dict(sorted(ftd.items())))
