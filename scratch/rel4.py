import requests, time, collections, json, datetime as dt
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
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return []
    return []
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c".lower()
norm=json.load(open("norm.json"))
swept=set(t["from"].lower() for t in norm)
sample=list(dict.fromkeys(t["from"] for t in norm))[:120]

first_blocks=[]   # (block, ts, addr)
peer_edges=0
peer_pairs=collections.Counter()
gasprice_2018=collections.Counter()
for idx,a in enumerate(sample):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":60,"sort":"asc"})
    if not n: continue
    first_blocks.append((int(n[0]["blockNumber"]), int(n[0]["timeStamp"]), a, n[0]["from"].lower()))
    # peer interactions with other swept addrs
    for t in n:
        cp = t["to"].lower() if t["from"].lower()==a.lower() else t["from"].lower()
        if cp in swept and cp!=a.lower():
            peer_edges+=1; peer_pairs[tuple(sorted([a.lower(),cp]))]+=1
    # gas price fingerprint of the 2018 txs sent BY this addr
    for t in n:
        if t["from"].lower()==a.lower() and int(t["timeStamp"])<1546300800:
            gasprice_2018[int(t["gasPrice"])//10**9]+=1
    if idx%30==0: print(f"  {idx}/{len(sample)}",flush=True)

first_blocks.sort()
print("\n--- FIRST-TX timing of swept addrs (n={}): ---".format(len(first_blocks)))
mo=collections.Counter(U(ts)[:7] for _,ts,_,_ in first_blocks)
print("first-tx month:", dict(sorted(mo.items())))
# block bucket clustering: how many share a 5000-block window
bw=collections.Counter(b//5000 for b,_,_,_ in first_blocks)
top=bw.most_common(8)
print("densest 5000-block windows of first-tx (bucket -> count):", top)
# who sent the funding first tx
funders=collections.Counter(f for _,_,_,f in first_blocks)
print("first-tx 'from' (funder) top:", funders.most_common(12))

print(f"\n--- PEER GRAPH: direct txs between two swept addrs (sample {len(sample)}): {peer_edges} edges, {len(peer_pairs)} distinct pairs")
for p,c in peer_pairs.most_common(10): print("   ",c,p)

print("\n--- 2018 gasPrice (gwei) fingerprint of swept addrs' own txs:")
for g,c in gasprice_2018.most_common(12): print(f"   {g} gwei : {c}")
