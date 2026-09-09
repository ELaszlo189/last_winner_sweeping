import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base = "https://api.etherscan.io/v2/api"
def page_all(module, action, address):
    out=[]; sb=0; seen=set()
    while True:
        got=None
        for _ in range(5):
            r = requests.get(base, params={"chainid":1,"module":module,"action":action,"address":address,
                "startblock":sb,"endblock":99999999,"page":1,"offset":1000,"sort":"asc","apikey":ESK}, timeout=90).json()
            if isinstance(r.get("result"),list): got=r["result"]; break
            time.sleep(1.5)
        if not got: break
        new=[t for t in got if (t["hash"],t.get("traceId",""),t.get("logIndex","")) not in seen or True]
        # dedupe by hash+from+to+value+blk for internal
        added=0
        for t in got:
            key=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"))
            if key in seen: continue
            seen.add(key); out.append(t); added+=1
        last_blk=int(got[-1]["blockNumber"])
        if len(got)<1000: break
        if last_blk==sb and added==0: break
        sb=last_blk  # overlap by 1 block to be safe; dedupe handles it
    return out

norm = page_all("account","txlist",C)
intl = page_all("account","txlistinternal",C)
print("total normal txs:", len(norm), " range:",
      dt.datetime.utcfromtimestamp(int(norm[0]["timeStamp"])).date(), "->", dt.datetime.utcfromtimestamp(int(norm[-1]["timeStamp"])).date())
print("total internal txs:", len(intl))

bym = collections.Counter(dt.datetime.utcfromtimestamp(int(t["timeStamp"])).strftime("%Y-%m") for t in norm)
print("\nnormal txs by month:")
for m in sorted(bym): print(" ", m, bym[m])

fn = collections.Counter((t.get("functionName","") or t.get("input","")[:10]) for t in norm)
print("\ntop functions called:")
for f,c in fn.most_common(12): print(f"  {c:5d}  {f[:60]}")

w = [t for t in norm if (t.get("functionName","") or "").startswith("withdraw")]
print("\nwithdraw() calls:", len(w), " unique callers:", len(set(t["from"].lower() for t in w)))
io = [t for t in intl if t["from"].lower()==C.lower()]
print("internal ETH-out events:", len(io), " total ETH out:", sum(int(t["value"]) for t in io)/1e18)
byim = collections.Counter(dt.datetime.utcfromtimestamp(int(t["timeStamp"])).strftime("%Y-%m") for t in io)
print("ETH-out by month (ETH):")
vbym=collections.defaultdict(float)
for t in io: vbym[dt.datetime.utcfromtimestamp(int(t["timeStamp"])).strftime("%Y-%m")]+=int(t["value"])/1e18
for m in sorted(byim): print(f"  {m}  {byim[m]:5d} events  {vbym[m]:.3f} ETH")

json.dump(norm, open("norm.json","w")); json.dump(intl, open("intl.json","w"))
print("\nsaved norm.json / intl.json")
