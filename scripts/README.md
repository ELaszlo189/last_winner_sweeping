# scripts/

Curated reproducers for the headline results. Numbered in rough dependency order.
Each reads `.env` (the originals reference `../.env`) and hits Etherscan (~3 req/s) + an RPC.

| script | produces | notes |
|---|---|---|
| `01_pull_campaign.py`        | `camp_norm.json`, `camp_intl.json` | every 2026 tx to the LastWinner contract + every payout |
| `02_build_drained_eoas.py`   | `drained_eoas.csv` | union of withdraw() callers + track-A loose-ETH sweep victims. Needs `balances.json` (external, not shipped) for the vault columns — comment those out or regenerate it. |
| `03_relatedness_sample.py`   | `relatedness_sample.csv` | first-tx / first-funder / coToken-link for a sample; the basis of the "one fleet" claim |
| `04_lastwinner_all_callers.py`| `lastwinner_all_callers.json` | full block-range scan of everyone who ever called the contract; checkpoints |
| `05_a707_intersection.py`    | `a707_senders_full.json` + printed intersections | the 0xA707 overlap analysis |
| `06_build_a707_link_files.py`| `a707_link_shared_addresses.csv`, `a707_link_analysis.md` | |

`../scratch/` holds every other one-off script from the investigation — badly named but each
derives one specific finding. `grep -l 0xSOMEADDRESS ../scratch/*.py` to find the one that
touched an address you care about.
