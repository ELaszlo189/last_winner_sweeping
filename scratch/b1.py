import json, collections
b=json.load(open("balances.json"))
rows=b["balances"]
print("snapshot:", b["scan_date"], " contract had", b["contract_eth_balance"], "ETH across", b["addresses_with_balance"], "addrs")
bal={r["address"].lower(): r["balance_eth"] for r in rows}
print("loaded balances:", len(bal), " sum", round(sum(bal.values()),2), "ETH")

# campaign withdraw() callers (post-snapshot)
camp=json.load(open("camp_norm.json"))
callers=collections.Counter()
for t in camp:
    if (t.get("functionName","") or "").startswith("withdraw"):
        callers[t["from"].lower()]+=1
print("campaign withdraw() callers:", len(callers))

claimed = {a:v for a,v in bal.items() if a in callers}
unclaimed = {a:v for a,v in bal.items() if a not in callers}
print(f"\nCLAIMED since snapshot : {len(claimed):6d} addrs  {sum(claimed.values()):9.2f} ETH  (Mar-31 balances)")
print(f"NOT yet claimed       : {len(unclaimed):6d} addrs  {sum(unclaimed.values()):9.2f} ETH")

def dist(d, label):
    buck=collections.Counter(); ev=collections.defaultdict(float)
    for a,v in d.items():
        k = ">=1" if v>=1 else "0.1-1" if v>=0.1 else "0.01-0.1" if v>=0.01 else "<0.01"
        buck[k]+=1; ev[k]+=v
    print(f"\n{label}:")
    for k in [">=1","0.1-1","0.01-0.1","<0.01"]:
        print(f"   {k:9} {buck[k]:6d} addrs  {ev[k]:9.2f} ETH")
dist(unclaimed,"UNCLAIMED distribution")

# save unclaimed sorted
u=sorted(unclaimed.items(), key=lambda x:-x[1])
json.dump(u, open("unclaimed.json","w"))
print("\ntop 25 unclaimed:")
for a,v in u[:25]:
    print(f"   {v:9.4f}  {a}")
