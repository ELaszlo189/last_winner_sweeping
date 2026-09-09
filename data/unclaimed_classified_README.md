# unclaimed_classified.csv — what the 2,425 ETH still in the LastWinner contract actually is

Completes `open_leads[0]` / the `TASK1` spot-check in `summary.json`: a full address-level
scan of every vault holder that has **not** called `withdraw()` and is **not** in the 2026
drained set (`data/drained_eoas.csv`).

Scope: the **47,183** non-drained unclaimed addresses (the 48,451 in `unclaimed.json` minus
the 1,268 that are in `drained_eoas.csv` and hold 0.04 ETH of dust between them).
**42,820 / 47,183 scanned = 99.98% of the 2,424.9 ETH** (the 4,363 unscanned rows are
sub-0.0006 ETH dust, 0.41 ETH total, marked `scan_pending`).

Method, per address:
- `eth_getCode(addr)` (Alchemy) + `contract getcontractcreation` (Etherscan V2). Was-a-contract
  + empty code now  ⇒  **self-destructed** (dead, no key, no code).
- For EOAs in the top 20,000 by value: first funder (first inbound value tx, normal or
  internal), first-tx date, whether the first outgoing tx was to LastWinner, whether it ever
  called LastWinner. Cluster funder = one of the six 2018 bankroll wallets
  (`0x4ce9f39d3a`, `0x1d1e10e8c6`, `0xecd8b3877d`, `0xeb6d43fe24`, `0x25c6459e5c`, `0x73957709`).
- `touched_by_2026_drain_infra` = the address ever received ETH from one of the 28 operation
  addresses in `infra_addresses.csv` (workers, dispatcher, gas funders, collectors, bootstrap).

## Headline

| class | addrs | ETH | what it is |
|---|--:|--:|---|
| `dead_contract`   | 35,791 | **1,842.8** | 2018 contracts that self-destructed the day they were made. **Permanently stuck — unwithdrawable by anyone, the 2026 drainer included.** |
| `eoa_house`       | 1 | **163.4** | `0xf3cb6f36…` — pID 1, pure `aff` (house / first-referrer commission). Real EOA, dormant since 2019. |
| `eoa_cluster`     | 2,214 | **247.7** | Dormant 2018 **farming-fleet** EOAs: cluster funder, first-seen Aug 2018, first tx = play LastWinner, dormant since 2018–19. Same fleet as the drained set — but **0 of them were ever touched by the 2026 drain infra.** |
| `eoa_other`       | 941 | 138.3 | LW players funded outside the six bankrolls — secondary sub-farms + larger individuals. |
| `eoa_unscanned`   | 3,688 | 31.2 | Confirmed EOA, funder fingerprint not pulled (tail). By the top-20k rate ≈ 70% are also cluster. |
| `lookup_failed`   | 185 | 1.1 | Etherscan creation lookup errored — re-run. |
| `scan_pending`    | 4,363 | 0.4 | Sub-0.0006 ETH dust, not scanned. |

So of the ~2,425 ETH: **~76% is dead-contract residue that no key can reach**, ~7% is the
game's own house wallet, **~11% (~270 ETH) is dormant fleet EOAs the 2026 operator did not
take**, and only ~6% is plausibly ordinary abandoned players.

Independent cross-check (`scratch` funder-coverage pass): for the four bankroll wallets whose
2018 funding is in normal txs, ~10–12% of everything they funded is unclaimed **and** never
infra-touched — ≥4,985 wallets / ≥224 ETH. That is the floor for "same cluster, not the
entity's active key set."

## Does the 2026 entity have fleet keys still pending?

**No, for anything it controls.** It gas-touched 18,216 distinct addresses and drained 100%
of them; only 2 infra-touched addresses have a residual vault (0.0001 ETH). Of ~25,300
`withdraw()` callers only 1,268 have a pending vault and they hold 0.04 ETH.

**The `eoa_cluster` set is the same 2018 fleet by origin, but the operator's key trove
evidently covers only ~88–90% of it.** Whoever (if anyone) holds those ~270 ETH of keys has
not moved.

## Where to manually verify the self-destructed contracts

- **`data/dead_contract_creators.csv`** — the 120 deployer wallets that created the dead
  contracts, ranked by ETH stuck. Six wallets (`0x73b61a56…`, `0xae587866…`, `0x16e21b70…`,
  `0x820d115b…`, `0x5167350d…`, `0x7f2f933e…`) made ~22,400 of the 35,791 and account for
  ~1,183 ETH. On Etherscan, open a creator and use the **"Contract Creations"** internal-txn
  filter (`…/address/<creator>#internaltx`) to see the batch of leaf contracts it deployed.
- **`data/unclaimed_classified.csv`, `cls == dead_contract`** — each row has the
  `contract_creator`, the `contract_factory` (the intermediate contract `0xae5878…` etc.
  called that actually `CREATE`d the leaf), and the `contract_created` date. Paste any
  `address` into Etherscan: it shows as a **Contract** with a red **"Self Destruct"** notice,
  a creation tx, and no current bytecode. `eth_getCode(addr) == 0x` confirms it.
- Re-derive the whole table:
  `getcontractcreation` for was-it-ever-a-contract, `eth_getCode` for alive-now, then the
  `scratch/` scripts `scan_creation*.py` / `build_outputs.py` (working copies in the
  investigation scratchpad) that produced these two files.

This is the "BAPT-LW20" airdrop-farming operation (AnChain's name — see
`scratch/app_history_findings.md` §2b) plus the game operator's own wash-trading bots: a
coordinated multi-account fleet, but one whose wallets were contracts that self-destructed,
so their `gen`/`aff` vaults are stranded forever.
