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
contract**. Largely (a) 2018 contracts that self-destructed the day they were made (vaults permanently
stuck - no code, no key), and (b) long-abandoned wallets. **Sized exactly in `unclaimed_classified.csv`
(2026-09-09).**

## `unclaimed_classified.csv` — 47,183 rows  *(added 2026-09-09)*
Full address-level scan of the non-drained unclaimed set (the 48,451 minus the 1,268 that are
in `drained_eoas.csv`). 42,820 scanned = 99.98% of the 2,424.9 ETH. Columns: `address`,
`unclaimed_eth`, `cls`, `contract_creator`/`contract_factory`/`contract_created` (for
`dead_contract`), `first_seen`/`last_seen`/`n_tx`/`called_lastwinner`/`first_tx_to_LW`/
`first_funder`/`cluster_funder` (for EOAs, top-20k), `touched_by_2026_drain_infra`.
`cls`: `dead_contract` 35,791 / **1,842.8 ETH** (self-destructed 2018 contracts — stuck for
everyone) · `eoa_house` 1 / 163.4 (pID-1 `aff`) · `eoa_cluster` 2,214 / 247.7 (dormant
farming-fleet EOAs — same fleet as the drained set, **0 ever infra-touched**) · `eoa_other`
941 / 138.3 · `eoa_unscanned` 3,688 / 31.2 (EOA, funder not pulled) · `lookup_failed` 185 ·
`scan_pending` 4,363 / 0.4 (dust). Full write-up + how-to-verify: `unclaimed_classified_README.md`.

## `dead_contract_creators.csv` — 120 rows  *(added 2026-09-09)*
The deployer wallets behind the `dead_contract` rows, ranked by `eth_stuck`. `creator`,
`n_dead_contracts_unclaimed`, `eth_stuck`, `first_created`, `last_created`. Top 6
(`0x73b61a56`, `0xae587866`, `0x16e21b70`, `0x820d115b`, `0x5167350d`, `0x7f2f933e`) = ~22,400
leaf contracts / ~1,183 ETH. = BAPT-LW20 airdrop-farming fleet + operator wash-trading bots.
Manual check: open a creator on Etherscan → "Contract Creations" (`#internaltx`).

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
