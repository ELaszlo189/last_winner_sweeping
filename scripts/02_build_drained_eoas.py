import json, csv, datetime as dt, collections
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")

camp=json.load(open("camp_norm.json"))
intl=json.load(open("camp_intl.json"))
bal={r["address"].lower(): r["balance_eth"] for r in json.load(open("balances.json"))["balances"]}
ta=json.load(open("trackA_senders.json")); a279=set(ta["a279"]); d8d7=set(ta["8d7c"])
pubdr=set(json.load(open("drainer_senders.json"))["senders"])   # sent to 0xA707 (public Apr-30 drainer)
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"

# withdraw() calls per address
wd=collections.defaultdict(list)
for t in camp:
    if (t.get("functionName","") or "").startswith("withdraw") and t["isError"]=="0":
        wd[t["from"].lower()].append(int(t["timeStamp"]))
# ETH actually pulled OUT of the LW contract per address
outeth=collections.defaultdict(float)
for t in intl:
    if t["from"].lower()==LW and int(t["value"])>0:
        outeth[t["to"].lower()]+=int(t["value"])/1e18

def burst(ts):
    d=U(ts)
    if d<="2026-05-20": return "1 (Apr-May)"
    if d>="2026-07-25": return "2 (Aug-Sep)"
    return "mid"

universe = set(wd) | a279 | d8d7
rows=[]
for a in sorted(universe):
    ws=sorted(wd.get(a,[]))
    trackA = ("Jul(0xa279ffef)" if a in a279 else "") + ("+" if a in a279 and a in d8d7 else "") + ("Aug24(0x8d7c20e3)" if a in d8d7 else "")
    via=[]
    if ws: via.append("withdraw()")
    if a in a279 or a in d8d7: via.append("looseETH")
    first_w = U(ws[0]) if ws else ""
    rows.append({
      "address": a,
      "drained_via": "+".join(via),
      "withdraw_calls": len(ws),
      "first_withdraw": first_w,
      "last_withdraw": U(ws[-1]) if ws else "",
      "withdraw_burst": burst(ws[0]) if ws else "",
      "eth_pulled_from_LW_contract": round(outeth.get(a,0.0),6),
      "looseETH_sweep": trackA or "",
      "lw_vault_balance_snapshot": round(bal[a],6) if a in bal else "",
      "still_unclaimed_vault": "yes" if (a in bal and a not in wd) else "",
      "also_drained_by_public_0xA707": "yes" if a in pubdr else "",
      "lw_participant": "yes" if (a in bal or a in outeth) else "no",
    })

# FILE 1: all drained EOAs
cols=list(rows[0].keys())
with open("drained_eoas.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump(rows, open("drained_eoas.json","w"))

# FILE 2: LastWinner-participant subset
lw_rows=[r for r in rows if r["lw_participant"]=="yes"]
with open("drained_eoas_lastwinner.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(lw_rows)
json.dump(lw_rows, open("drained_eoas_lastwinner.json","w"))

# summary
n=len(rows)
print(f"drained_eoas.csv         : {n} addresses")
print(f"drained_eoas_lastwinner.csv: {len(lw_rows)} addresses ({len(lw_rows)*100//n}%)")
via=collections.Counter(r["drained_via"] for r in rows)
print("\ndrained_via breakdown:")
for k,c in via.most_common(): print(f"  {c:6d}  {k}")
print("\nwithdraw_burst breakdown (of withdraw() callers):")
bc=collections.Counter(r["withdraw_burst"] for r in rows if r["withdraw_burst"])
for k,c in bc.most_common(): print(f"  {c:6d}  {k}")
print("\nlooseETH sweep collector breakdown:")
lc=collections.Counter(r["looseETH_sweep"] for r in rows if r["looseETH_sweep"])
for k,c in lc.most_common(): print(f"  {c:6d}  {k}")
tot_pulled=sum(r["eth_pulled_from_LW_contract"] for r in rows)
tot_vault=sum(r["lw_vault_balance_snapshot"] for r in rows if isinstance(r["lw_vault_balance_snapshot"],float))
print(f"\ntotal ETH pulled from LW contract (in file): {tot_pulled:.1f}")
print(f"total snapshot vault balance (in file): {tot_vault:.1f}")
print(f"addresses also hit by public 0xA707 drainer: {sum(1 for r in rows if r['also_drained_by_public_0xA707'])}")
print(f"non-LW-participant drained EOAs (loose ETH only, never had a vault): {sum(1 for r in rows if r['lw_participant']=='no')}")
