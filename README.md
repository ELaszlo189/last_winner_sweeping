# LastWinner 2026 vault-drain — investigation

An open, reproducible map of what happened to **LastWinner** (`0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C`),
the biggest FoMo3D clone of 2018, whose 8‑years‑dormant wallet fleet started being emptied in 2026.

> **Status:** partly resolved, partly open. Numbers and addresses below are on‑chain facts;
> the *attribution* (who / why) is an inference and is explicitly hedged. See
> [`llm.txt`](./llm.txt) for the machine‑readable brief and the list of open questions,
> and [`summary.json`](./summary.json) for every figure with its derivation.

---

## Fact / interpretation / alternatives

### What is fact (on‑chain, verifiable)
- Since **May 2026**, one entity has swept **~44,000** Ethereum wallets tied to the 2018
  gambling game **LastWinner**: first the loose ETH in the wallets (**~3,000 ETH**), then each
  wallet's in‑game vault via `withdraw()` (**~1,545 ETH** — the contract went 3,970.71 →
  2,425.63 ETH).
- **~80–85%** of the swept wallets provably transacted with the LastWinner contract; **~⅔**
  were funded by ETH withdrawals from **Huobi/HTX + BW.com**; **~44%** used a Nov‑2018 ETH
  pooling contract ("coToken").
- **~4,550 ETH** moved in total; as of early Sept 2026 it is consolidated into a handful of
  wallets and **mostly parked** — 2,907 ETH unmoved in `0xe4a219fbed` since 28 Jul.
- A **separate** operator (`0xA707…`, the publicly‑reported April‑30 "dormant wallet drain")
  swept **~11–16** of the same wallets days earlier; its other 561 victims are unrelated (§4).
- The **2,425 ETH still in the contract** is largely unrecoverable — much of it sits in the
  vaults of ~1,000 addresses that were contracts and self‑destructed back in 2018 (no key, no
  code), the rest in long‑abandoned wallets.

### What we think
- The ~44k wallets are **one 2018 LastWinner farming operation** (or mostly one), not
  thousands of unrelated people — see *"Why the ~44k wallets are treated as one set"* below.
- The 2026 sweep is **slightly more likely a consolidation** by whoever rightfully holds the
  keys than a theft: it's methodical, it calls `withdraw()` even on empty wallets (roster
  behaviour), and it **parks** rather than dumps.

### What it could be instead
- A **mix** — one farm + independent farmers + retail — that only shares "played LastWinner +
  got swept in 2026".
- A **theft**: Etherscan labels a linked address phishing, this sits inside a broader
  April‑2026 weak‑key dormant‑wallet wave, and a real user has claimed a drained wallet. If
  the parked ETH bridges/cashes out, or the key flaw turns out to be publicly reproducible,
  it tips to theft.
- Run by **2–3 parties or a sweeper service**, not one person.
- The Huobi funding could just mean these were **ordinary Chinese gamblers**, not a
  coordinated farm at all.

*Full reasoning and every figure: [`summary.json`](./summary.json). Open questions and the
list of things that could be wrong: [`llm.txt`](./llm.txt).*

---

## 1. What LastWinner was (2018)

- A straight code fork of **FoMo3D** ("last person to buy a key before the timer expires wins
  the pot"). Deployed 2018‑08‑06 by `0xeae69cADEB04E66767bD69f52e0fFFc28E37d799` (a throwaway
  wallet, 23 tx, 3 ETH). **Source never verified on Etherscan.**
- Fronted by Android + iPhone apps and promoted by a Chinese fundraising‑pyramid crowd
  ("蟻群 / Ant Swarm") — per 2018 reporting (see [`SOURCES.md`](./SOURCES.md)).
- ~270k transactions in its first 6 days; briefly out‑traded the original FoMo3D.
- **Bot fleet:** ~44k wallets were spun up to farm the game from launch, mostly funded by
  Huobi/HTX withdrawals. 2018 reports allege ~200,000 ETH of operator bot funding — the
  *substance* (a large 2018 farming set manufacturing volume) checks out; the *figure* is a
  soft contemporaneous estimate, and **no single "bankroll" entity is identified** — the six
  wallets that funded most of the fleet are HTX/Huobi and BW.com exchange hot wallets.

## 2. What happened in 2026

The LastWinner contract held **3,970.71 ETH** on 2026‑03‑31; it holds **2,425.63 ETH** now.
The sweep has run in **four phases**, in two modes — pulling each wallet's in‑game vault out of
the contract via `withdraw()`, and sweeping the loose ETH already sitting in the wallet:

| Phase | When | What | ETH | Collector → destination |
|---|---|---|---|---|
| **1 — `withdraw()` burst 1** | **May 2026** | ~7,570 `withdraw()` calls | **~579** | `0x8f55b448…` |
| **2 — loose‑ETH sweep 1** | 26–30 Jul 2026 | 27,231 wallets' EOA balances | **2,907** | `0xa279ffef…` → one hop → `0xe4a219fbed…`, **parked since 28 Jul** |
| **3 — loose‑ETH sweep 2** | 24 Aug 2026 | 30,364 wallets' leftover dust | ~102 | `0x8d7c20e3…` (parked) |
| **4 — `withdraw()` burst 2** | 24 Aug – 6 Sep 2026 | ~16,400 `withdraw()` calls, run in parallel by a **16‑wallet worker fleet** (dispatcher `0xcf49c8fb…`) | **~965** | `0x5723168b…`; some onward via the LI.FI bridge |

Totals: **~1,545 ETH** pulled from the contract via `withdraw()` (phases 1 + 4, reconciles
exactly with the 3,970.71 → 2,425.63 balance drop) + **~3,010 ETH** of loose ETH swept from the
wallets (phases 2 + 3). Full infrastructure list in [`data/infra_addresses.csv`](./data/infra_addresses.csv).

**Grand total moved ≈ 4,550 ETH; ~3,090 ETH consolidated‑and‑parked; nothing large cashed out.**

## 3. Who — the 2018 cast

| # | Actor | Role | On‑chain link to the others |
|---|---|---|---|
| 1 | Game operator `0xeae69cad` + "Ant Swarm" promoters | built + promoted the game | **none** (deployer is a throwaway, 23 tx) |
| 2 | The **fleet** (~44k wallets) | farmed the game from launch; ~⅔ first funded by **Huobi/HTX** withdrawals (5 hot wallets) + **BW.com** (1) | — |
| 3 | **"coToken" pool** `0x03cb0021808442ad5efb61197966aef72a1def96` | a small ETH deposit/withdraw **pooling contract** (~187 ETH, 552 depositors, active only **Nov 2018**); a co‑investment / pooled‑betting vehicle used by **~44%** of the fleet | deployer funded from OKX; **no link** to the game operator |

The **2026 drainer** holds keys to ~44k wallets and works them as an organised roster (it even
calls `withdraw()` on ~8,900 empty ones). Whether that reflects one 2018 farm or a mass key
compromise of many participants is the core open question.

*Note on the six funding wallets:* they are **HTX/Huobi and BW.com exchange hot wallets**
(sent‑tx counts 12k–773k). "Funded by Huobi" tells you the fleet's working capital came out of
the dominant 2018 Chinese exchange — it does **not** identify a private bankroll. A mass
0.0025‑ETH sweep from those wallets on 2026‑03‑14 is exchange hot‑wallet consolidation, not
anything to do with this operation.

## Why the ~44k wallets are treated as one set

Not proof — a best inference. The signals, strongest first:

1. **Purpose‑built.** Almost every wallet was **funded and first used on the same day**, and
   its first action was playing LastWinner or depositing to the coToken pool. These are not
   pre‑existing personal wallets; they were created to farm the game.
2. **Two tight creation windows** — ~63% first appear in LastWinner's opening ~5 days
   (Aug 2018), ~22% in a second wave in **Nov 2018**. Not spread across years.
3. **A shared private pooling contract.** ~44% of the wallets deposited to **coToken**
   (`0x03cb0021`), which existed for **only 25 days** in Nov 2018 and had 552 depositors.
   Unrelated gamblers don't share a bespoke pool.
4. **One shared funding route** — ~⅔ seeded from the same six Huobi/HTX + BW.com hot wallets.
   Weak on its own (Huobi ≈ everyone in 2018 China), but it lines up with 1–3.
5. **One keyholder in 2026.** The sweep drips a uniform ~0.003 ETH of gas, does
   gas → `withdraw()` → sweep in the same minute, funnels to a small rotating set of
   collectors, and calls `withdraw()` on ~8,900 **empty** wallets — i.e. it is iterating a
   fixed list, not reacting to balances. Whatever the wallets were in 2018, they are **one
   controlled set now**.
6. **LastWinner‑specific.** ~85% provably touched the LastWinner contract; 0% of a sampled
   subset ever touched the original FoMo3D.

**Against:** the funding route is a weak signal, ~56% are *not* in the coToken pool, and 2018
behaviour is heterogeneous (5–50 tx, varied gas). So it could instead be a farm **plus**
independent farmers **plus** retail that merely share "played LastWinner + got swept in 2026".

## 4. The separate April‑2026 drainer (`0xA707…`)

`0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7` (Etherscan `Fake_Phishing2831105`) drained 577
dormant wallets / 326.8 ETH over Apr 29 – May 7 2026 and bridged to BTC + Monero via THORChain.
It shares **exactly 11 victims** with our operation (16 that ever played LastWinner). Its other
561 victims are unrelated wallets from **2017–2026**, mostly exchange‑funded — i.e. `0xA707`
is a *generic* weak‑legacy‑key sweeper and the overlap is **incidental**, not a shared
keystore. On the 11 shared wallets, `0xA707` took the loose EOA balance on Apr 30; our
operation later called `withdraw()` and took the still‑in‑contract game vault — **two
different pools of ETH**. Detail: `a707_link_analysis.md`, `a707_link_shared_addresses.csv`.

## 5. Current status (as of early Sep 2026)

- LastWinner contract: **2,425.63 ETH**. Full scan (2026‑09‑09, `data/unclaimed_classified.csv`):
  **1,842.8 ETH (76%) in 35,791 self‑destructed 2018 contracts** (unrecoverable — no key, no
  code; a batch airdrop‑farming fleet, 120 deployer wallets), **163.4 ETH** the game's own
  pID‑1 house/`aff` wallet, **~270 ETH** in dormant farming‑fleet EOAs the 2026 operator never
  touched (its key trove covers ~88–90% of the fleet, not all), **~147 ETH** other abandoned
  players. The operator drained 100% of the 18,216 addresses it did gas‑touch.
- `0xe4a219fbed…`: **2,907 ETH**, unmoved 40+ days.
- Other collectors: ~180 ETH, mostly idle.
- Only ~325 ETH is known to have actually left through a bridge (the `0xA707` actor, not ours).

---

## What's in this repo

| path | contents |
|---|---|
| `README.md` | this file |
| [`llm.txt`](./llm.txt) | machine‑readable brief + open questions + how to continue |
| [`summary.json`](./summary.json) | **every finding**, every number with its derivation |
| [`SOURCES.md`](./SOURCES.md) | references (SECBIT, contemporaneous reporting, the 2026 coverage) |
| [`data/FILES_README.md`](./data/FILES_README.md) | column definitions for the CSVs |
| `data/drained_eoas.csv` | **44,014** drained wallets: how each was drained, burst, funder, `touched_lastwinner`, whether also hit by `0xA707` |
| `data/infra_addresses.csv` | **32** operation‑owned addresses with roles (collectors, worker fleet, parks, bootstrap wallets) |
| `data/a707_link_shared_addresses.csv` | the 11 shared + 6 more, with per‑address timelines to verify on Etherscan |
| `data/a707_senders_full.json` | all 577 wallets that funded `0xA707` |
| `data/a707_link_analysis.md` | the "separate actor" write‑up |
| `data/relatedness_sample.csv` | 180‑address funder sample behind the "one fleet" claim |
| `data/unclaimed.json` | 48,451 not‑yet‑claimed vault holders (= the 2,425 ETH still in the contract) |
| `data/unclaimed_classified.csv` | **47,183** of those, classified: dead self‑destructed contract vs live EOA, funder fingerprint, whether the 2026 drain infra ever touched it. 99.98% of the ETH scanned. See `data/unclaimed_classified_README.md`. |
| `data/dead_contract_creators.csv` | the **120** deployer wallets behind the 35,791 self‑destructed contracts (1,843 ETH stuck), ranked — where to manually verify on Etherscan |
| `data/camp_norm.json.gz`, `data/camp_intl.json.gz` | raw 2026 contract tx / payout dumps (reproducibility anchor) |
| `scripts/` | curated scripts that reproduce the headline results |
| `scratch/` | every other ad‑hoc script used during the investigation — messy, but shows exactly how each finding was derived |

**Not included:** `balances.json` — the per‑player in‑game vault snapshot (an external input,
~65k rows). It is reconstructable from `getPlayerInfoByAddress(address)` on the contract, or
from the contract's event logs. Derived columns in `drained_eoas.csv` (`lw_vault_balance_snapshot`,
`still_unclaimed_vault`) come from it.

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # fill in ETHERSCAN_API_KEY (+ RPC_URL for eth_call/eth_getBalance)
.venv/bin/python scripts/01_pull_campaign.py
```

Scripts read `.env` from the repo root. Etherscan free tier is ~3–5 req/s — the bigger pulls
checkpoint and take a while.

## Caveats (please read before quoting this)

- **Attribution is inference.** No private "bankroll" entity is identified (the wallets that
  funded most of the fleet are HTX/Huobi + BW.com hot wallets). There is **no proof** of who
  operated the 2018 fleet (one farm? farmers + retail?) or who runs the 2026 drain.
- **Consolidation vs. theft is ~50/50 and unresolved.** Do not present it as proven either way.
- The "scam / pyramid" framing of LastWinner is **2018 reporting** (cited in `SOURCES.md`), not
  an original finding here.
- `touched_lastwinner = unknown` for ~19% of the drained set is a **data‑completeness limit**
  (the caller scan stops mid‑Sep 2018), not a claim that those wallets are unrelated.
- The ETH being swept is overwhelmingly a **bot operation's own farmed dividends**, with a
  small minority of apparently‑real players mixed in — not, in the main, innocent retail savings.

## License / use

Public‑domain data and analysis. Verify everything against Etherscan before relying on it.
Corrections and continuations welcome — see `llm.txt` for the open threads.
