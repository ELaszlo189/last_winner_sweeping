import json, collections
u=json.load(open("unclaimed.json"))           # [(addr, mar31_bal_eth)] not-yet-claimed
ta=json.load(open("trackA_senders.json"))
aS=set(ta["a279"]); dS=set(ta["8d7c"]); trackA=aS|dS
camp=json.load(open("camp_norm.json"))
callers=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
b=json.load(open("balances.json"))
allbal={r["address"].lower():r["balance_eth"] for r in b["balances"]}

unc=dict(u); TOT=sum(unc.values())
print(f"NOT-yet-claimed: {len(unc)} addrs, {TOT:.1f} ETH (== current contract balance)\n")

# 1) overlap with the loose-ETH (track A) sweep
ov=[(a,v) for a,v in u if a in trackA]
print(f"[A] unclaimed addrs that DID sweep their loose ETH to 0xa279ffef/0x8d7c20e3 (track A) but have NOT done withdraw():")
print(f"    {len(ov)} addrs   {sum(v for _,v in ov):.1f} ETH   ({sum(v for _,v in ov)/TOT*100:.0f}% of the 2,425 ETH)")

# 2) of ALL track A senders, how many still unclaimed vs claimed
tA_claimed = len(trackA & callers)
tA_unclaimed = len(trackA & set(unc))
tA_nobalance = len(trackA - set(allbal) - callers)
print(f"\n[B] the {len(trackA)} track-A loose-ETH sweep senders break down as:")
print(f"    {tA_claimed} have ALSO called withdraw() (fully processed)")
print(f"    {tA_unclaimed} are in the unclaimed vault list (loose ETH taken, vault still pending)")
print(f"    ~{len(trackA)-tA_claimed-tA_unclaimed} had no Mar-31 vault balance / other")

# 3) campaign callers who are NOT in balances.json (operator ran whole key list, incl zero-balance)
callers_nobal = callers - set(allbal)
print(f"\n[C] campaign withdraw() callers with NO Mar-31 vault balance: {len(callers_nobal)} / {len(callers)}")
print("    -> operator called withdraw() from a fixed address roster, not a balance scan")

# 4) size split of the track-A-overlap unclaimed
buck=collections.Counter(); ev=collections.defaultdict(float)
for a,v in ov:
    k=">=1" if v>=1 else "0.1-1" if v>=0.1 else "0.01-0.1" if v>=0.01 else "<0.01"
    buck[k]+=1; ev[k]+=v
print("\n[D] the track-A-overlap unclaimed, by size:")
for k in [">=1","0.1-1","0.01-0.1","<0.01"]:
    print(f"    {k:9} {buck[k]:5d} addrs  {ev[k]:8.2f} ETH")
