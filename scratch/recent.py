import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; C="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base="https://api.etherscan.io/v2/api"
def call(params):
    params.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try:
            r=requests.get(base,params=params,timeout=60).json()
        except Exception as e:
            time.sleep(2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate limit" in str(r.get("result","")).lower(): time.sleep(2); continue
        return r["result"]
    return []

# NORMAL txs, descending, paginate
norm=[]
for pg in range(1,26):
    res=call({"module":"account","action":"txlist","address":C,"page":pg,"offset":1000,"sort":"desc"})
    if not res: break
    norm.extend(res)
    if len(res)<1000: break
    time.sleep(0.25)
print("normal txs pulled:", len(norm))
if norm:
    print("newest:", dt.datetime.utcfromtimestamp(int(norm[0]["timeStamp"])), "block", norm[0]["blockNumber"])
    print("oldest pulled:", dt.datetime.utcfromtimestamp(int(norm[-1]["timeStamp"])), "block", norm[-1]["blockNumber"])
bym=collections.Counter(dt.datetime.utcfromtimestamp(int(t["timeStamp"])).strftime("%Y-%m") for t in norm)
print("\nby month:")
for m in sorted(bym): print(f"  {m}  {bym[m]}")
fn=collections.Counter((t.get("functionName","").split("(")[0] or t.get("methodId","")) for t in norm)
print("\nfunctions:")
for f,c in fn.most_common(15): print(f"  {c:6d}  {f}")

# INTERNAL txs descending
intl=[]
for pg in range(1,26):
    res=call({"module":"account","action":"txlistinternal","address":C,"page":pg,"offset":1000,"sort":"desc"})
    if not res: break
    intl.extend(res)
    if len(res)<1000: break
    time.sleep(0.25)
print("\ninternal txs pulled:", len(intl))
io=[t for t in intl if t["from"].lower()==C.lower()]
print("ETH-out events:", len(io), " total:", sum(int(t["value"]) for t in io)/1e18, "ETH")
vb=collections.defaultdict(float); cb=collections.Counter()
for t in io:
    m=dt.datetime.utcfromtimestamp(int(t["timeStamp"])).strftime("%Y-%m"); vb[m]+=int(t["value"])/1e18; cb[m]+=1
print("ETH out by month:")
for m in sorted(vb): print(f"  {m}  {cb[m]:6d} events  {vb[m]:10.3f} ETH")

json.dump(norm,open("norm.json","w")); json.dump(intl,open("intl.json","w"))
