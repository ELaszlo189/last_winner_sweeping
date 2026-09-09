# data/ — column definitions

## `drained_eoas.csv` — 44,014 addresses
Every EOA touched by the 2026 LastWinner-fleet drain operation (union of: called `withdraw()`
on the LastWinner contract in 2026, and/or had its loose ETH swept to a July/Aug collector).

| column | meaning |
|---|---|
| `address` | the EOA |
| `drained_via` | `withdraw()` (pulled its in-game vault), `looseETH` (its plain ETH balance was swept), or both |
| `withdraw_calls` | # of successful `withdraw()` calls it made on the contract in 2026 |
| `first_withdraw` / `last_withdraw` | dates |
| `withdraw_burst` | `1 (Apr-May)` (label as stored; the payouts are almost entirely May 2026) — the ~579 ETH tranche, collector `0x8f55b448…` · `2 (Aug-Sep)` — the ~965 ETH tranche, collector `0x5723168b…` |
| `eth_pulled_from_LW_contract` | ETH this address received from the contract via `withdraw()` (deduped, 1 per tx). Σ = **1,545 ETH**, reconciles exactly with the contract balance drop 3,970.71 → 2,425.63 ETH |
| `looseETH_sweep` | which loose-ETH collector(s): `Jul(0xa279ffef)` (26–30 Jul 2026) and/or `Aug24(0x8d7c20e3)` (24 Aug 2026) |
| `lw_vault_balance_snapshot` | the address's in-game vault (win+gen+aff) from `balances.json` — an **external input not shipped here** (an ~August-2026 snapshot despite its `scan_date: 2026-03-31` field; regenerate via `getPlayerInfoByAddress`). Blank if not present. |
| `still_unclaimed_vault` | had a snapshot vault and has NOT called `withdraw()` |
| `also_drained_by_public_0xA707` | also sent ETH to `0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7` (`Fake_Phishing2831105`, a SEPARATE actor — 11 shared victims) |
| `lw_participant` | strict flag: had a vault OR received ETH from the contract |
| `touched_lastwinner` | `yes` = sent a tx to the contract (full block-range scan, 63,456 unique callers, converged through mid-Sep 2018) OR holds a pID/vault. `unknown` = not confirmed in that data. **35,527 `yes` (80.7%)**, 8,487 `unknown` (19.3%). The `unknown` set is almost all loose-ETH-only; the caller scan stops mid-Sep 2018 and a full-history sample of that group found 60% did call the contract — so true "never touched LastWinner" is ~15% of the set, and those belong to the same broad 2018 cohort (same Huobi/BW funding route, same Aug/Nov-2018 creation waves, 45% used the coToken pool). |

## `infra_addresses.csv` / `.json` — 32 rows
Curated catalogue of the operation's own infrastructure with `role` / `phase` / `notes`:
collectors, cold parks, per-phase gas funders, the burst-2 dispatcher `0xcf49c8fb` and its
16-wallet worker fleet (each = gas-drip + collect for ~788 victims over Aug 31 – Sep 4;
`0x0e6e1be9d6…` = worker #9), the LI.FI bridge, the four 2018-keyset wallets used to seed
each phase's infra, and — for contrast — the SEPARATE public drainer `0xA707…`.

## `a707_link_shared_addresses.csv` — 17 rows
The 11 addresses drained by BOTH `0xA707` and this operation, plus 6 more that `0xA707`
drained which also played LastWinner. Per-address: 2018 first-tx, # of 2018 LastWinner calls,
first funder (and whether it is one of the six Huobi/BW hot wallets), ETH & timestamp sent to `0xA707`, 2026 `withdraw()`
count, and what went to our collectors. See `a707_link_analysis.md`.

## `a707_senders_full.json` — 577
Every wallet that funded `0xA707`. Its ~561 non-LastWinner victims span 2017–2026 and are
mostly exchange-funded — `0xA707` is a generic weak-legacy-key sweeper, the LastWinner overlap
is incidental.

## `a707_shared_addresses.json` — the 11, bare list.

## `relatedness_sample.csv` — 180 rows
A stratified sample of drained addresses with first-tx date, first funder, and early coToken
linkage — the evidence that the drained set is a related 2018 LastWinner cohort.

## `lastwinner_all_callers.json` — 63,456
Every unique address that ever sent a transaction to the LastWinner contract (Etherscan
block-range scan; converged through ~mid-Sep 2018 — not 100% of the contract's full life).

## `unclaimed.json` — 48,451 `[address, ETH]` pairs
The vault holders who have NOT called `withdraw()` — i.e. the **2,425 ETH still inside the
contract**. Largely (a) BAPT-LW20 self-destructed proxy contracts, vaults permanently stuck,
and (b) genuinely abandoned real players. Sizing (a) vs (b) exactly is an open task (see `llm.txt`).

## `trackA_senders.json` — `{a279: [...], 8d7c: [...]}`
The 27,230 / 30,364 addresses that swept loose ETH to the July / Aug-24 collectors.

## `camp_norm.json.gz` / `camp_intl.json.gz`
Raw Etherscan dumps: every 2026 transaction to the LastWinner contract (26,853) and every
internal payout out of it (24,063). The reproducibility anchor for the withdraw()-side numbers.

## Headline reconciliation
- Contract: **3,970.71 ETH (2026-03-31) → 2,425.63 ETH (now)** = **1,545 ETH** via `withdraw()`
  (burst-1 ~580 + burst-2 ~965).
- PLUS loose ETH swept straight from the EOAs: **~2,907 ETH** (July → `0xa279ffef` → parked at
  `0xe4a219fbed`) + ~102 ETH (Aug-24 dust → `0x8d7c20e3`).
- **Total moved ≈ 4,550 ETH; ~3,090 ETH consolidated-and-parked; nothing large cashed out.**
