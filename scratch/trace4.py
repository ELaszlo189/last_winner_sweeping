import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=requests.get(base,params=p,timeout=60).json()
        except: time.sleep(2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(2); continue
        return []
    return []
def pg(module,action,addr,sort="desc",maxp=40,sb=0,eb=99999999):
    out=[]
    for p_ in range(1,maxp+1):
        res=call({"module":module,"action":action,"address":addr,"page":p_,"offset":1000,"sort":sort,"startblock":sb,"endblock":eb})
        if not res: break
        out.extend(res)
        if len(res)<1000: break
        time.sleep(0.15)
    return out
G="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C".lower()

# All internal-out from game, get the big ones
intl=pg("account","txlistinternal",G,sort="desc",maxp=40)
io=[t for t in intl if t["from"].lower()==G]
io.sort(key=lambda x:-int(x["value"]))
print("window:", U(min(int(t['timeStamp']) for t in io)), "->", U(max(int(t['timeStamp']) for t in io)), " count", len(io))
print("\nTOP 25 vault withdrawals (address, ETH, date):")
big=io[:25]
for t in big:
    print(f"  {int(t['value'])/1e18:10.4f}  {t['to']}  {U(t['timeStamp'])}")

# follow the top 8 two hops
def hop(addr, depth, prefix=""):
    if depth==0: return
    tl=pg("account","txlist",addr,sort="asc",maxp=3)
    outs=[x for x in tl if x["from"].lower()==addr.lower() and int(x["value"])>0]
    ins=[x for x in tl if x["to"].lower()==addr.lower() and int(x["value"])>0]
    bal=call({"module":"account","action":"balance","address":addr})
    print(f"{prefix}{addr}  ntx={len(tl)} in={len(ins)} out={len(outs)} firsttx={U(tl[0]['timeStamp']) if tl else '?'}")
    for o in outs[-4:]:
        print(f"{prefix}  -> {int(o['value'])/1e18:.4f} ETH to {o['to']} @ {U(o['timeStamp'])}")
        hop(o["to"], depth-1, prefix+"    ")

print("\n=== FOLLOW TOP VAULTS ===")
seen=set()
for t in big[:8]:
    a=t["to"]
    if a in seen: continue
    seen.add(a)
    print(f"\n[{int(t['value'])/1e18:.3f} ETH vault]")
    hop(a,3)
