import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=requests.get(base,params=p,timeout=60).json()
        except: time.sleep(2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(2); continue
        return r["result"] if not isinstance(r.get("result"),str) else []
    return []
def paginate(module,action,addr,sort="desc",maxp=40):
    out=[]
    for pg in range(1,maxp+1):
        res=call({"module":module,"action":action,"address":addr,"page":pg,"offset":1000,"sort":sort})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        time.sleep(0.2)
    return out

COL="0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"
GAS="0x03cb0021808442ad5efb61197966aef72a1def96"

# ---- COLLECTOR outflows ----
n=paginate("account","txlist",COL); i=paginate("account","txlistinternal",COL)
print(f"COLLECTOR {COL}: normal={len(n)} internal={len(i)}")
print("  first activity:", U(min(int(t['timeStamp']) for t in n)))
out=collections.Counter(); outv=collections.defaultdict(float)
for t in n:
    if t["from"].lower()==COL.lower() and int(t["value"])>0:
        out[t["to"]]+=1; outv[t["to"]]+=int(t["value"])/1e18
print("  OUT (normal) dest -> count / ETH:")
for d,c in out.most_common(12): print(f"    {c:5d} {outv[d]:12.4f}  {d}")
inv=sum(int(t['value']) for t in i if t['to'].lower()==COL.lower())/1e18
innn=sum(int(t['value']) for t in n if t['to'].lower()==COL.lower())/1e18
print(f"  total IN: internal {inv:.3f} ETH + normal {innn:.3f} ETH   ({len(i)} internal legs)")
print(f"  total OUT: {sum(outv.values()):.3f} ETH")

# ---- GAS funder contract ----
print(f"\nGAS FUNDER {GAS}")
cr=requests.get(base,params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":GAS,"apikey":ESK},timeout=60).json()["result"]
print("  creation:", cr)
src=requests.get(base,params={"chainid":1,"module":"contract","action":"getsourcecode","address":GAS,"apikey":ESK},timeout=60).json()["result"][0]
print("  name:", src.get("ContractName"), " compiler:", src.get("CompilerVersion"))
gn=paginate("account","txlist",GAS,maxp=15)
print("  gasfunder normal tx:", len(gn), " span:", U(gn[-1]['timeStamp']), "->", U(gn[0]['timeStamp']))
callers=collections.Counter(t["from"] for t in gn)
print("  who calls the gas funder:")
for a,c in callers.most_common(6): print(f"    {c:5d}  {a}")

# ---- are withdraw callers 2018-era bots? sample 12 ----
print("\n--- withdraw caller provenance (are these 2018 bots?) ---")
norm=json.load(open("norm.json"))
samp=list(dict.fromkeys(t["from"] for t in norm))[:12]
for a in samp:
    tl=paginate("account","txlist",a,sort="asc",maxp=3)
    il=paginate("account","txlistinternal",a,sort="asc",maxp=3)
    firsttx=U(tl[0]["timeStamp"]) if tl else "?"
    lastold=[t for t in tl if t["timeStamp"]<"1600000000"]
    seed = il[0] if il else None
    print(f"{a} firsttx={firsttx} ntx={len(tl)} 2018-2020 txs={len(lastold)} seededBy={(seed['from'] if seed else None)} seedETH={(int(seed['value'])/1e18 if seed else 0)}")
