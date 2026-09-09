import json, csv

shared=json.load(open("a707_shared_addresses.json"))       # 11
rows=list(csv.DictReader(open("a707_shared_analysis.csv"))) # 11 shared + 6 A707-only

# split
shared_rows=[r for r in rows if r["group"]=="SHARED"]
only_rows=[r for r in rows if r["group"].startswith("A707-ONLY")]

with open("a707_link_shared_addresses.csv","w",newline="") as fh:
    cols=["group","address","first_tx","n_2018_LW_calls","first_funder","funder_is_ClusterA","sent_to_A707_ETH","sent_to_A707_when","2026_withdraw_calls","sent_to_our_collectors"]
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader()
    for r in shared_rows+only_rows: w.writerow({k:r.get(k,"") for k in cols})

md=f"""# 0xA707 <-> LastWinner-drain operation : the shared-address link

## The two actors
| | Public drainer 0xA707 | Our LastWinner-fleet operation |
|---|---|---|
| address | `0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7` (Etherscan `Fake_Phishing2831105`) | rotating collectors 0x8f55b448 / 0x5723168b / 0xa279ffef / 0x8d7c20e3 ... |
| active | 2026-04-29 23:37 -> 2026-05-07 | ~2026-04 -> 2026-09 (ongoing, tailing) |
| victims | **577 wallets**, 326.8 ETH | **~44,014 wallets**, ~4,500 ETH |
| gas seeded via | Uniswap V2 Router (a token->ETH swap) | reactivated 2018 Cluster-A fleet wallets |
| cash-out | 324.741 ETH -> THORChain -> BTC + Monero, within a week | consolidate + PARK (2,907 ETH unmoved 40+ days); some via LI.FI |
| 1-ETH side payments | 0x4feea1ca... , 0xbb9bb536... (fee / accomplice?) | none |

## Victim-set overlap (verified, not sampled)
- 0xA707's 577 senders: **16** ever called LastWinner ; **11** are in our 44,014-wallet drained set.
- 0xA707's other **561 victims** are a totally different population: first-tx years spread **2017-2026**, **0/120 funded by Cluster A**, many funded straight from Binance/other exchanges. => 0xA707 is a GENERIC "dormant wallet with a leaked/weak key" drainer (the publicly-reported April-2026 weak-key wave). Its LastWinner hits are **incidental** (2.8% of its list).

## What the 11 shared addresses show
For 8 of the 11 (the ones with a real transfer to 0xA707):
1. 2018 LastWinner launch-week wallet (first tx Aug 2018), played the game (2-32 calls).
2. On **2026-04-30, 04:10-05:58 UTC**, its balance (0.003 - 0.99 ETH) went to **0xA707**.
3. A few days later (**2026-05-03/04/05**) its residual dust (0.002 - 0.31 ETH) went to our burst-1 collector **0x8f55b448**.
4. Some were hit a 3rd time by our burst-2 collector 0x5723168b in Aug/Sep 2026, and made 1-21 withdraw() calls.
(The other 3 of the 11 only have a 0-ETH tx to 0xA707 - likely address-poisoning / a failed tx - and were processed only by our operation.)
- 5 of the 11 are funded by a Cluster A bankroll wallet; the rest by OKX / misc.

## Interpretation
- **No shared infrastructure**: different gas source, different collectors, different bridge, opposite cash-out tempo.
- **Not a shared keystore**: if 0xA707 held the Cluster A fleet keystore it would have taken thousands, not 11-16.
- The overlap = ~16 of the fleet's 2018 wallets ALSO had independently-weak/leaked keys, so BOTH a general weak-key hunter (0xA707) and the fleet-keystore holder (our operation) could drain them. 0xA707 got there ~3 days earlier; our operation swept the leftovers.
- => our operation holding the COMPLETE, clean fleet keystore points to the rightful holder (operators / successor); 0xA707 is an unrelated opportunist.

## Files
- `a707_link_shared_addresses.csv` - the 11 shared + 6 "0xA707 drained a LastWinner player our op only lightly touched", with per-address timeline for you to verify on Etherscan.
- `a707_senders_full.json` - all 577 addresses that funded 0xA707 (for your own cross-checks).
"""
open("a707_link_analysis.md","w").write(md)
print("wrote a707_link_shared_addresses.csv and a707_link_analysis.md")
print("\n11 shared addresses:")
for a in shared: print("  ", a)
