import json, csv
# Curated infrastructure catalogue of the 2026 LastWinner-fleet drain operation.
workers=json.load(open("cf49_workers.json"))
rows=[]
def add(addr, role, phase, notes):
    rows.append({"address": addr.lower(), "role": role, "phase": phase, "notes": notes})

# ---- victim-facing collectors / consolidation ----
add("0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1","loose-ETH collector","July 2026","27,231 victim EOAs -> here -> one 2907.12 ETH hop to 0xe4a219fbed")
add("0xe4a219fbed16e5c62e335082521f44c508b19191","cold park","July 2026","holds 2,907.12 ETH untouched since 2026-07-28")
add("0x8d7c20e3b88bc70246306d9620c2d555448523f7","dust collector + burst-2 gas source","Aug 24 2026","30,364 victim EOAs -> here (~102 ETH dust); also seeds burst-2 gas")
add("0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac","burst-1 sweep collector","burst-1 (Apr-Aug 2026)","withdraw() proceeds; shares 0x8f55.../...fac vanity affix with a gas funder")
add("0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8","burst-1 gas funder","burst-1","2018-08-06 wallet; first funded by 0x4ce9f39d (Cluster A bankroll)")
add("0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","burst-2 sweep collector","burst-2 (Aug-Sep 2026)","holds ~62 ETH; first funded by 0x86c6391d (2018-08-07 wallet)")
add("0x220ecbb6c968fbd6f73cfe56017d78fcc4f18647","burst-2 pool / park","burst-2 (Aug 31-Sep 2)","1000+ inbound legs, holds 19.99 ETH, ZERO outbound - consolidate-and-hold")

# ---- burst-2 dispatcher + worker fleet ----
add("0x99e03db23a79125f0128288611feedf270a758e4","burst-2 dispatcher funder","burst-2","2020-04-26 wallet; funded 0xcf49c8fb with 10.23 ETH on 2026-08-31")
add("0xcf49c8fb434af3a2cde64fe3907ce27bf1317762","burst-2 dispatcher","burst-2","split 10.23 ETH into 15 x 0.6318 ETH + 1 x 0.75 to the worker fleet, 2026-08-31")
for i,w in enumerate(workers,1):
    if w=="0x220ecbb6c968fbd6f73cfe56017d78fcc4f18647": continue
    add(w,"burst-2 worker (gas-drip + collect)","burst-2 (Aug 31-Sep 4)",
        f"worker #{i}: ~0.632 ETH seed from 0xcf49c8fb; ~788 victims each - drip ~0.003 ETH gas -> victim withdraw() -> sweep back here")

# ---- downstream ----
add("0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b","downstream hub (EOA)","burst-2","high-velocity plain-transfer EOA")
add("0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae","bridge","burst-2","LiFiDiamond = LI.FI bridge/swap aggregator (mainstream contract) - some funds bridged/swapped")

# ---- 2018 keyset wallets used to bootstrap infra ----
add("0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","2018 bankroll 'Cluster A'","bootstrap","seeded burst-1 gas funder; mutual-only 5-wallet cluster, stopped 2026-03-14")
add("0x696e01b63189fc476051122c15fcf57b05292cac","2018 fleet wallet","bootstrap","seeded July collector 0xa279ffef; itself a track-A sweeper WITH an LW vault")
add("0x260d1c4724d15ae5c882d365886fb8cae70a746c","2018 fleet wallet","bootstrap","seeded Aug-24 collector 0x8d7c20e3; itself track-A; first tx 2018-08-08")
add("0x86c6391dccf7c73b2119c0fa2630f1fdb5819741","2018 fleet wallet","bootstrap","seeded burst-2 collector 0x5723168b; first tx 2018-08-07")

# ---- separate actor (shares keys, not infra) ----
add("0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7","SEPARATE drainer (public 'Fake_Phishing2831105')","2026-04-29..05-07","577 wallets / 326.8 ETH -> THORChain -> BTC/XMR. Only 11 shared victims, ZERO shared infra. Different operator, overlapping compromised keys.")
add("0xa271266ea7cf6863e518edc7bb2607349cde2cf1","funder of sequential-pID 2026 rebind wallets","2026-08","funded 0x0d4a2d5a etc. (pIDs 89135+) that hold un-withdrawn 2018 gen vaults")

cols=["address","role","phase","notes"]
with open("infra_addresses.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump(rows, open("infra_addresses.json","w"), indent=1)
print(f"infra_addresses.csv: {len(rows)} rows")
for r in rows: print(f"  {r['address']}  {r['role']}")
