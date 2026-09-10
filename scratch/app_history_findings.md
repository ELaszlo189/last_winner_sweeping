# LastWinner (最后赢家) — game, app, bot-farming & private-key findings

Research note supporting the 2026 vault-drain investigation (`summary.json`).
Compiled 2026-09-07. All external claims attributed inline; sources at bottom.

---

## 1. What LastWinner was

- **A FoMo3D clone.** Deployed **2018-08-06**, block 6098849, at
  `0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C` by deployer
  `0xeae69cADEB04E66767bD69f52e0fFFc28E37d799`. Contract token label on
  Etherscan: "Last Winner (LW)".
- Near-verbatim fork of FoMo3D's Solidity (same `getPlayerVaults`,
  `getPlayerInfoByAddress`, `registerNameXID`, `airDropTracker_`, `withdraw()`
  selectors; even the `atInversebrah` joke function). **The on-chain contract is
  NOT source-verified on Etherscan** — our selector evidence comes from bytecode
  analysis (`../bytecode.txt`), not published source.
- Run by a Chinese team, promoted by a fundraising-pyramid crowd
  **"蚁群传播 / Ant Swarm Propagation"**. The FoMo3D team publicly disowned it as a
  rip-off.
- Scale: **~270k+ tx in ~6 days**; at peak it consumed **~30% of all Ethereum
  gas** and was a headline cause of the Aug-2018 fee spike / mempool congestion.
- Game model: buy "keys"; last key-buyer before the timer hits zero takes the
  main pot; a separate **airdrop pool** pays random smaller hits. LW raised the
  airdrop rate to **10%** (FoMo3D was 1%).
- Then effectively dormant 2019–2025 until the 2026 drain that this repo maps.

---

## 2. Was it bot-farmed? — YES, in two separate senses

### 2a. The operator's own wash-trading bots (fake volume)
- Multiple reports (CoinDesk; SECBIT; 界面新闻/Jiemian; Zhihu) state the operator
  **pre-loaded ~200,000 ETH to run automated bot transactions** against its own
  contract, to fake a busy, crowded game and lure real depositors.
- SECBIT flags the exact 200k figure as **reported but not independently
  verified**. What *is* on-chain-visible: bursts of contract
  creation + self-destruct and tx shapes far from human play, from the very
  first blocks — consistent with heavy scripted seeding.
- Interpretation: a Ponzi bootstrapped with robots. "The popularity may have been
  a carefully planned scheme that used robots to fabricate activity and attract
  new investors" (Jiemian / Zhihu).

### 2b. Third-party airdrop farming — the BAPT-LW20 group
- LW copied FoMo3D's broken airdrop RNG verbatim: seed derived from
  `block.timestamp / difficulty / coinbase / gaslimit / number / msg.sender`,
  win if `(seed % 1000) < airDropTracker_`. All inputs are publicly observable,
  so an attacker can **pre-compute a winning tx before sending it**.
- Group **BAPT-LW20** (AnChain naming) pre-deployed **~1,000 proxy contracts**
  (funded from Kraken) used as "extraNonce" values, looped them to find winning
  create-addresses, used nested contract creation in constructors to bypass the
  human-only check, and fired **~50,000 tx over 6 days**.
- Take: **~5,194 ETH from the airdrop pool** + the **7,754 ETH grand prize**
  = **~12,948 ETH** (~$12M then). Their tx were <10% of traffic but captured
  ~49% of airdrop payouts. Peak Aug 8–10 2018, ~100 ETH/hour.
- This is the "~5,194 ETH from the airdrop pool" line in `summary.json`
  `history_2018`.

**Bottom line:** LastWinner was bot-farmed by its own operators for fake volume
*and* was bot-farmed by outside attackers who drained the airdrop pool. Both are
well documented.

---

## 3. Was it an Android app? — YES (Android + iPhone)

- Marketed as **"just download and install the app to participate"**. Native
  clients for **Android and iPhone** (SECBIT: mobile clients that "simplified
  operations and lowered the barrier to entry").
- The pitch was explicitly to spare mainland users from installing a browser
  wallet extension (MetaMask): the app shipped a **built-in Ethereum wallet**.
- Lowering that barrier is what let it scale to a mass, non-crypto-native
  Ponzi audience.
- Front-end site was `lastwinner.me` (**domain now dead / NXDOMAIN**). Wayback
  has it — see §5.

---

## 4. Did you import a private key into the app? — the key question

Two conflicting pictures; both matter.

### Official guide (`lastwinner.me/en/guide.html`, via search cache)
- You could **CREATE** a new in-app wallet **or IMPORT** one via **mnemonic or
  private key**.
- Either path: you set a **wallet PIN** for payment verification. "LW does not
  store your PIN and does not provide PIN recovery."

### Third-party reviews (2018, Chinese-language)
Harsher and more specific:
- On **wallet creation the app did NOT display, or let you back up, the private
  key or mnemonic**, and provided **no export function** afterwards.
- Net effect: **the LastWinner team (or its backend) controlled users'
  private keys** — users effectively got only an address. Reviewers called this a
  major risk and tied it to the pyramid-scheme operation.

### Reading
Import was *possible* (advanced users could bring an existing key), but the
**default onboarding produced an effectively custodial, non-exportable wallet**.
Whether keys were generated **client-side on the phone** or **server-side and
pushed down** is **not established from public sources** — this is the crux for
attribution and needs the app binary / backend to resolve.

---

## 5. Does the app's code survive anywhere? — search results (2026-09-07)

**Nothing conclusive found. No public source for the app itself.**

| Target | Result |
|---|---|
| **On-chain contract source** | **NOT verified** on Etherscan for `0xDd9fd6b6…`. No published Solidity. Only bytecode. |
| **GitHub — LastWinner-specific** | None. `github.com/search?q=lastwinner+fomo3d` → **0 repos**. No Gitee hits either. |
| **GitHub — generic FoMo3D clones** | `reedhong/fomo3d_clone` and its fork `Jaetoxi/fomo3d` (Truffle projects reconstructing FoMo3D contracts). **Generic, not LW**; no mobile/app/wallet/keygen code; Chinese README about "fomo3d官网合约". Useful only as a contract-behaviour reference. |
| **APK mirrors** | No `com.lastwinner…` package found on APKPure / APKCombo via search. Not yet checked directly on Chinese stores (应用宝 / 应用汇 / 豌豆荚) or archived APK sites. |
| **Wayback Machine — site** | Snapshots EXIST. `lastwinner.me/` → snapshot `20221128172930`. `lastwinner.me/en/guide.html` → snapshot `20220331044704` (HTTP 200). Earlier 2018 snapshots very likely exist too. |
| **Wayback fetch from here** | **Blocked** — this agent's WebFetch cannot reach `web.archive.org` (and jina/allorigins/corsproxy proxies all failed: 403/401/522). The `archive.org/wayback/available` JSON API *does* work. |

### App-download links found on the LastWinner site (user, 2026-09-07)

iOS ad-hoc / enterprise install manifest:
```
itms-services://?action=download-manifest&url=https://lastwinnerapp.oss-cn-shanghai.aliyuncs.com/lastwinner.plist
```
- Host `lastwinnerapp.oss-cn-shanghai.aliyuncs.com` = an **Alibaba Cloud OSS bucket**
  (`lastwinnerapp`, Shanghai region).
- As of 2026-09-07 the agent gets **HTTP 404** on both `/lastwinner.plist` and the
  bucket root `/`. 404 on the *root* (vs 403 `AccessDenied`) strongly implies the
  **bucket was deleted** — need `curl -i` to read the `<Code>` and be sure
  (`NoSuchBucket` = gone; `AccessDenied` = alive, try key guesses; `NoSuchKey` on
  the file but `AccessDenied` on root = alive).
- **Not in Wayback** (`archive.org/wayback/available` → no snapshot for the .plist).
  Not indexed anywhere (0 search hits for the bucket / `lastwinner.plist` /
  `lastwinner.ipa`).
- Normal flow: the `.plist` contains a `software-package` URL pointing at the
  actual **`.ipa`** (very likely another key in the same bucket, e.g.
  `lastwinner.ipa`). The **Android `.apk`** link is probably also on this bucket
  or listed on the same guide page — get the archived HTML to find both.
- Value even if only the `.ipa`/`.apk` survives: it does **not** need to be
  installable — unzip it and read the Mach-O / Java-Kotlin / bundled JS to see
  **how wallet keys are generated and whether they're sent anywhere**. APK is
  trivial (`jadx`); IPA needs class-dump / Hopper + JS-bundle grep.

### Commands to chase the app binary (run yourself — agent is firewalled from web.archive.org)

```
# 1. Is the OSS bucket alive or deleted? read the XML <Code>
curl -is 'https://lastwinnerapp.oss-cn-shanghai.aliyuncs.com/' | sed -n '1,40p'
curl -is 'https://lastwinnerapp.oss-cn-shanghai.aliyuncs.com/?list-type=2&max-keys=1000' | sed -n '1,60p'
curl -is 'https://lastwinnerapp.oss-cn-shanghai.aliyuncs.com/lastwinner.plist'

# 2. If alive, guess common keys
for k in lastwinner.ipa LastWinner.ipa lastwinner.apk LastWinner.apk app/lastwinner.ipa \
         ios/lastwinner.ipa android/lastwinner.apk lastwinner.mobileprovision update.xml version.json; do
  echo "== $k"; curl -so /dev/null -w '%{http_code}\n' "https://lastwinnerapp.oss-cn-shanghai.aliyuncs.com/$k"
done

# 3. Wayback: every archived URL for the OSS host + the site (find .ipa/.apk/.plist/JS)
curl -sL 'https://web.archive.org/cdx/search/cdx?url=lastwinnerapp.oss-cn-shanghai.aliyuncs.com*&output=text&fl=timestamp,original,mimetype,statuscode&collapse=urlkey&limit=10000'
curl -sL 'https://web.archive.org/cdx/search/cdx?url=lastwinner.me*&matchType=domain&output=text&fl=timestamp,original,mimetype,statuscode&collapse=urlkey&limit=20000' -o lw_cdx.txt
grep -Ei '\.ipa|\.apk|\.plist|manifest|download|/js/|bundle|app\.' lw_cdx.txt
```

### To pull the archived site yourself (agent is firewalled from web.archive.org)
Run in this session with the `!` prefix, or in a normal shell:

```
# raw archived guide page (id_ = original bytes, no Wayback rewriting)
curl -sL 'https://web.archive.org/web/20220331044704id_/https://lastwinner.me/en/guide.html' -o lw_guide_2022.html
curl -sL 'https://web.archive.org/web/20221128172930id_/https://lastwinner.me/' -o lw_home_2022.html

# list ALL archived lastwinner.me URLs (find 2018 snapshots, JS bundles, APK links)
curl -sL 'https://web.archive.org/cdx/search/cdx?url=lastwinner.me*&output=text&fl=timestamp,original,mimetype,statuscode&collapse=urlkey&limit=5000' -o lw_cdx.txt

# then grep for the front-end JS bundles and any apk
grep -Ei '\.js$|\.apk$|wallet|keystore|mnemonic|bip39' lw_cdx.txt
```

The front-end JS bundles (if archived) are where **client-side key generation**
would be visible — that would confirm or kill the "weak RNG in the app" vector
(vector B in `summary.json`).

---

## 6. Why this matters for the 2026 drain (`summary.json` vectors)

The 2018 history lines up with the two leading compromise vectors:

- **Vector A — bot-farm key store.** Both the operator's wash-trading fleet
  (§2a) and BAPT-LW20's ~1,000 proxies (§2b) required large sets of funded
  hot wallets whose keys lived in a bulk keystore / DB / master seed. That is a
  concentrated, later-leakable trove — matches the drained cohort's profile
  (100% first-active 2018, shared bankrolls, ≥2 unlinked clusters, and
  **multiple unrelated drainers holding the same keys** in 2025–26).
- **Vector B / D — weak client-side keygen or custodial backend.** A phone app
  minting wallets for non-technical users (§3–§4) is exactly where low-entropy
  RNG bites, and a custodial backend is exactly what leaks as a set.
  **Direct precedent in the same scene:** *"Trust Wallet's Fomo3D Summer"*
  (SECBIT, 2024) — Trust Wallet's 2018 iOS build seeded its RNG with
  `srand((unsigned)time(NULL))`, so two wallets made in the same second
  collided; **>2,100 ETH victims**, later brute-forced by generating one
  mnemonic per second and matching on-chain. Many of those wallets were created
  **to play FoMo3D**. A LastWinner in-app wallet with similar seeding would be
  independently reproducible by anyone → explains several simultaneous
  drainers, none sharing infrastructure.

**Still open (needs the artifact, not more search):** the **2018 LastWinner
Android/iOS binary or its backend** — to see whether keys were generated on the
device, with what entropy source, and whether they were also held server-side.

---

## 6b. The "LastWinner copied FoMo3D's weak wallet keygen" hypothesis — assessed 2026-09-09

**Prompt:** SECBIT showed FoMo3D-era players' Trust-Wallet keys had weak entropy;
LastWinner copied FoMo3D's contract verbatim, so maybe it also copied the wallet
generation and inherited the flaw.

**The chain has a broken link, and a sharper version.**

- **FoMo3D shipped NO wallet.** It was a browser dApp. Per SECBIT's own 2024
  write-up, the weak keys belonged to *Trust Wallet's* 2018 **iOS** build, and
  FoMo3D enters the story only because many of those Trust-Wallet users
  *happened to play FoMo3D* ("119 wallets created on July 21, 2018 … most … were
  involved in the famous Fomo3D game"). So "LastWinner copied FoMo3D's wallet
  keygen" cannot be literally true — there was nothing to copy. Copying the
  *Solidity* tells us nothing about the *app*.
- **The real question** is LastWinner's OWN app. Primary source confirms it had
  one: the archived 2018-08-12 guide (`web.archive.org/web/20180812093336id_/
  http://lastwinner.me:80/en/guide.html`) says *"LW built-in Ethereum wallet …
  solves the problem that most users can't install browser wallet plug-in"*,
  *"The way to create a new account will generate an Ethereum wallet for the
  player"*, *"Players can import wallets using mnemonics and private Seeds"*,
  and *"you need to set a wallet PIN for payment verification. LW does not store
  user PIN code"*. => an on-device BIP39 generator — exactly the surface where a
  low-entropy RNG bites. Whether the PIN is folded into the BIP39 seed as a
  passphrase (which would defeat timestamp regeneration) is unclear; the guide
  frames it as payment/signing auth, which suggests it is NOT a seed passphrase.
- **Timeline (revised 2026-09-09 — an earlier draft was too glib with "fixed
  before launch").** Dependency pins mean an upstream fix does NOT reach an app
  until its team runs `pod update` and ships a new build. SECBIT's fix chain:
  `trezor-crypto-ios` 0.0.7 **2018-07-16** → `trust-core` 0.1.2 **2018-08-08** →
  `trust-keystore` 0.4.3 **2018-08-08** → `trust-wallet-ios` **2018-08-21**.
  LastWinner launched **2018-08-06**, so an app frozen at launch was built
  against the still-vulnerable `trust-core`/`trust-keystore` (or an older pinned
  `TrezorCrypto` pod, or a hand-copied `srand(time())` snippet — the bug *class*
  was a widespread 2018 copy-paste, not unique to trezor). Trust Wallet's libs
  were THE reference for "embed a wallet in your dApp" in 2018; a fast Chinese
  FoMo3D-clone team grabbing them mid-2018 is very plausible.
- **The app was v1.0.0 and shows no sign of ever being updated.** Wayback CDX for
  `lastwinner.me` (full history, via the Wayback CDX API): only one
  APK filename ever (`lastwinner_1.0.0.apk`); `download.html` / `guide.html`
  return **404 by 2018-10-12** — the site was gutted ~2 months after launch. No
  forced-update path, no server-side patch. => whatever v1.0.0 shipped is what
  minted **every** fleet wallet, in BOTH the Aug-2018 and Nov-2018 waves. That
  is exactly why the 2026 drainer can hold the complete fleet as one roster: one
  never-patched build, one keyspace.

**On-chain circumstantial evidence (moderate; not proof):**

1. **The fleet's key-generation window is narrow and known.** 200-wallet sample
   of confirmed players: 96% first used their key **2018-08-06 … 08-14** (peak
   Aug 7-9), plus the Nov-2018 second wave (~1 month). Wallet creation precedes
   first use by minutes-to-days, so the whole keyset was minted inside roughly
   **~2 weeks (Aug) + ~1 month (Nov) 2018 ≈ 3.8 million one-second timestamps.**
   A SECBIT-style regeneration (per candidate second: seed PRNG → 32-byte
   entropy → BIP39 → PBKDF2-2048 → derive `m/44'/60'/0'/0/0` → keccak → set-
   membership) over that window is **minutes of compute on one machine** and
   recovers the ENTIRE fleet in a single pass — which is exactly the observed
   2026 fact (one entity, complete ~44k roster, uniform drain). A leaked
   keystore file also explains the completeness, so this doesn't decide it — but
   weak-RNG is *reproducible by anyone*, which fits **multiple independent
   drainers** (0xA707 + our entity, possibly more later); a keystore leak is
   finite.
2. **0xA707 independently drained 11-16 fleet wallets.** Their first-tx dates are
   spread evenly across the Aug-2018 launch fortnight (3/day, Aug 6-10) + a
   couple later — NOT a tight contiguous block, i.e. consistent with 0xA707
   having covered the whole window (or a cross-app keyspace) rather than a lucky
   narrow guess. 16 independent hits on 44k addresses out of 2^160 is not
   coincidence: a real fraction of the fleet has keys in a regenerable class.
   (Counter-reading, which the repo currently prefers: 0xA707 was publicly tied
   by TRM to the 2022 **LastPass** breach — a credential-theft cause unrelated to
   RNG — and the overlap is incidental.)
3. **8-year dormancy** (0/40 sampled fleet wallets moved ETH in 2020-2025) rules
   out *trivially* weak keys (small ints / brainwallets, continuously swept since
   2016) but fits the "needs a dedicated regeneration campaign" profile of the
   Trust-Wallet class precisely.
4. **Plausible trigger timeline:** SECBIT published the Trust-Wallet timestamp
   method **Jan 2024** → someone applies it to other 2018 FoMo3D-era apps through
   2024-25 → LastWinner fleet drained 2025-26. Narrative, not evidence.

### 6b.1 STRONG new evidence (2026-09-09): the on-chain account names leak the client-side creation millisecond

A local script (not published) decoded the first LastWinner-contract call of 260
random confirmed-player fleet wallets. Findings:

- **The app auto-generates the account name and stamps `Date.now()` into it.**
  99/99 `registerNameXID` names in the sample match **exactly**
  `^[A-Za-z]{15}\d{13}$` — 15 random mixed-case letters + a **13-digit Unix
  millisecond timestamp**. Examples:
  `cHbQxzxPPRtIhkX1533634629710`, `peLtodMEQSPZIKT1533568698892`,
  `RJHCkfSMUpueZIw1533962392980`. No human types this; it is machine-generated
  on "create account".
- **That embedded ms timestamp is the wallet-creation moment.** Converted to UTC
  it precedes the on-chain registration tx by a **median of 22 seconds** (65/99
  within 60 s, 93/99 within 1 h; 1 marginally negative from clock skew). i.e. the
  name is generated client-side the instant the account/keypair is created, then
  the tx is signed and mined seconds later.
- **Consequence:** for every fleet wallet that registered a name (~38% of the
  sample — order ~13,000 wallets), the exact **millisecond** of wallet creation
  is sitting in public calldata. A SECBIT-style key regeneration no longer has to
  bound the creation time from funding — the name *hands you the seed candidate*
  to ms precision. Search space per such wallet collapses from ~days to ~1000 ms.
- **The 15-char `[A-Za-z]` prefix is a public sample of the app's client-side RNG
  stream** at creation time — the same RNG that (on the weak-RNG hypothesis)
  produced the mnemonic entropy. If it is `Math.random()`-class, the prefix
  further constrains the PRNG state.
- **This makes the generator JavaScript.** `Date.now()` (ms) + `[A-Za-z]{15}`
  random strings are the JS idiom (`Math.random().toString(36)` /
  `String.fromCharCode`) — so the app is RN / Cordova / webview, and the relevant
  precedent is a **weak JS wallet RNG** (`Math.random()` / `Date`-seeded), a
  known 2018 class, not only the trezor-crypto C bug.
- Still NOT proven: that the mnemonic entropy came from the same weak call. But
  the "we can't pin the timestamp" obstacle is now gone, and we have a public RNG
  readout to test against.

**Supporting details from the same 260-wallet pull:**
- **95% of fleet wallets' first LastWinner tx is their nonce-0 tx** (first tx
  ever) — the fleet is app-minted, not imported. 96% of first *outbound* txs go
  straight to the LW contract.
- First call: **160 `buyXid` / 99 `registerNameXID` / 1 `withdraw`**, 100% to the
  main contract `0xDd9fd6b6…` (LastWinner folded PlayerBook into the main
  contract). `registerNameXID` value is a flat **0.02 ETH** (matches the guide).
- **`gas` limit = 800000 on 253/260 (97%)** — app-hardcoded, scripted, not
  hand-set. `gasPrice` bimodal (10 gwei / 60 gwei) = ~two builds or pre/post the
  Aug-2018 congestion.
- **Referrer codes: 254 distinct / 259** — NOT one shared upline; a broad flat
  pyramid, `affCode==0` never used (the app always injects a referrer, as the
  guide requires). Low pIDs (12, 15, 37, 82, 313…) recur as referrers = early
  seed accounts / top of pyramid.
- **Funding NOT sponsored by a relayer:** 67% first-funded by the six HTX/BW hot
  wallets, 86 distinct funders, no single non-exchange address fanning out to the
  fleet. Users self-funded from an exchange; the app auto-registered a median
  ~52 min later.

(Scripts run locally, not published.)

### 6b.1b App-created census — 1,600 drained vs 1,600 undrained LW players

Classified each sampled address by its first LastWinner-contract call. (Alchemy
free tier caps `eth_getLogs` at 10 blocks, so this is sample-based, not a full
`onNewName` sweep. `onNewName` topic0 =
`0xdd6176433ff5026bbce96b068584b7bbe3514227e72df9c630b749ae87e64442`; the player
name is `bytes32 indexed` in topic3 — lowercased by the contract's NameFilter, so
mixed case survives only in calldata.)

- **The whole LastWinner playerbase is app-minted; the drained set is a slightly
  *purer* cut of it.** On the shared signals drained ≈ undrained: **~40% vs ~38%**
  of LW-callers carry the app's auto-generated `[a-z]{15}\d{13}` name; **`named_other`
  (a human-chosen name) = 0 of 1,311 drained callers and 1 of 1,561 undrained** —
  essentially nobody chose a name. The ~40% with a name just paid 0.02 ETH to
  register the auto-name; the rest (`buy_first_no_name`) ran the same app and
  skipped it (still nonce-0).
- **But the imported-wallet tail differs ~6×.** Genuine pre-deployment / external
  wallets (first-ever tx before LW's 2018-08-06 13:52 deploy, real 2018 play):
  **12 / 1,311 drained callers (0.9%) vs 90 / 1,561 undrained (5.8%)**. Nonce-0
  first-LW-tx among callers: **94.2% drained vs 87.9% undrained.** So the general
  LW-player population has a real ~6% "played with my own MetaMask/imToken wallet"
  tail — and the 2026 drainer **barely touched it**.
- **Implication for the vector — a modest lean toward weak-RNG regeneration.** An
  attacker who regenerated the *app's* keyspace can only reach app-created keys;
  externally-created wallets are out of reach, so they're near-absent from the
  drained set — which is what we see (0.9%). A keystore/backend leak could also
  miss imported wallets (if import wasn't custodied), so this isn't proof, but
  "the drain's reach ≈ exactly the app keyspace" is the regeneration signature.
- **Blast radius:** if the RNG is weak, the at-risk population is the entire ~63k+
  app userbase (`lastwinner_all_callers.json` + `balances.json`), not just the
  drained 44k. The other ~19k were presumably left because they were empty.
- **Window (feeds #5 / a regeneration):** app-pattern `Date.now()` values span
  **2018-08-06 14:38:44 UTC** (46 min after LW deployed at 13:52) **→ mid-Nov
  2018**, ~73% of the sample in the first 36 h; the sample is Aug-heavy only
  because the caller list converged mid-Sep — the Nov hit confirms the same
  never-updated app minted the Nov wave. **Genuine ms resolution: 1/756 values
  end in `000`.** name `Date.now()` → registration tx: median 21 s (p90 ~17 min;
  12/756 funded >1 day later). So for the ~40% with a name the creation instant
  is public to the millisecond; for the rest, first-tx time bounds it to
  seconds-minutes.
- **~4% of drained wallets flag a "pre-LW" first tx** — but on inspection ~all are
  artifacts: 2026 gas-drip forwards (class `withdraw_first`) or a single 2018
  token contract (`0xade2fc8d` "FusChain"), plus Alchemy `getAssetTransfers`
  metadata-timestamp skew (observed: one tx reported 09:37 vs true block time
  18:40). No evidence of a genuine imported-wallet cohort in the drained set.

(Scripts run locally, not published.)

### 6b.2 The decisive test is still blocked on the artifact

Still need `lastwinner_1.0.0.apk` (Android link on the 2018 `download.html`) or
the iOS `.ipa`, to read the keygen and regenerate — now over the millisecond
timestamps the account names hand us, not a blind window — matching against
`data/drained_eoas.csv`.

**Checked and exhausted (2026-09-09):**
- OSS bucket `lastwinnerapp.oss-cn-shanghai.aliyuncs.com` → **`NoSuchBucket`**
  (deleted); no Wayback captures of the bucket at all.
- Wayback CDX for `lastwinner.me`: only 2018 HTML (`download.html`/`guide.html`,
  retrieved from Wayback) + **2020 domain-parking pages** for
  `lastwinner_1.0.0.apk` and `assets/lw.js` (19,649-byte ad HTML, not the files).
- **Common Crawl** (CC-MAIN-2018-39/47): only `guide.html` / `error.html` /
  `robots.txt` — no JS bundle, no APK. Same guide digest as Wayback.
- `archive.org` full-text + `advancedsearch` for "lastwinner": **0 results**.
- Web search for `lastwinner_1.0.0.apk` / `lastwinner.plist` / `com.lastwinner`
  / the app name + apkpure/apkcombo/koodous/malwarebazaar: **no hits**.
- SECBIT's 2018 writeup confirms the mobile client existed but neither links it
  nor touches key generation (it's about the airdrop-RNG contract attack).
- iOS enterprise cert display name **"most media servis, ooo"** ("ООО" = Russian
  "LLC") — fits the 2018 wave of gambling apps abusing Apple enterprise certs
  (TechCrunch Feb-2019); no sample surfaced by cert name.

**Avenues that need resources outside this repo:**
- **AndroZoo** — its nightly metadata CSV (~2.7 GB compressed) has package name +
  market source for ~25M APKs; grep for `lastwinner`, get the SHA256, download via
  API. Needs an API key (academic-email request). Best structured lead.
- **VirusTotal Intelligence / Hybrid-Analysis / Intezer** — search
  `content:"lastwinner.me"` or `content:"lastwinnerapp.oss-cn-shanghai"` +
  `type:android`. Gambling apps are almost always uploaded. Needs an
  enterprise/API account.
- **Chinese app-store history & CN APK mirrors** (酷安/coolapk, 应用宝/sj.qq.com,
  豌豆荚, 360, liqucn, apk.tw, 7723) via a CN-friendly connection / Baidu.
- **Reach out to SECBIT / AnChain.AI / Zhongqiang Chen** — they reversed the LW
  contract in 2018; SECBIT also did the Trust-Wallet-FoMo3D wallet work. Good
  odds one kept the APK or its JS bundle.

(Script run locally, not published. Archived pages retrieved from web.archive.org.)

---

## 7. Sources

- CoinDesk — *Unstoppable Scams? Ethereum's Gambling Problem Is Only Getting Worse* (LW, ~200k ETH bot ether): https://www.coindesk.com/markets/2018/08/17/unstoppable-scams-ethereums-gambling-problem-is-only-getting-worse
- SECBIT — *Last Winner 的最后赢家 — 智能合约超大规模黑客攻击手法曝光* (2018-08-20): https://secbit.io/blog/2018/08/20/last-winner-of-lastwinner/
- SECBIT (zh mirror, Zhihu): https://zhuanlan.zhihu.com/p/42318584
- Zhongqiang Chen — *Randomness in smart contracts is predictable and vulnerable: LastWinner, Part 1*: https://medium.com/@zhongqiangc/randomness-in-smart-contracts-is-predictable-and-vulnerable-lastwinner-part-1-da40131b7ab0
- Zhongqiang Chen — *Exploiting FoMo3D Family, Part 2*: https://medium.com/@zhongqiangc/exploiting-fomo3d-family-part-2-b792fc1fb3f3
- AnChain.AI — *Largest Smart Contract Attacks… Part 1* (BAPT-LW20, 12,948 ETH): https://anchainai.medium.com/largest-smart-contract-attacks-in-blockchain-history-exposed-part-1-93b975a374d0
- 界面新闻 / Jiemian — *8万笔交易「封死」以太坊网络，只为抢夺Fomo3D大奖？* (app, built-in wallet, Ant Swarm pyramid, custodial-key criticism): https://www.jiemian.com/article/2372992.html
- Bianews mirror: https://www.bianews.com/news/details?id=18071&type=0
- SECBIT — *Trust Wallet's Fomo3D Summer: Fresh Discovery of Low Entropy Flaw From 2018* (2024-01-19): https://secbit.io/blog/en/2024/01/19/trust-wallets-fomo3d-summer-vuln/
- SECBIT CSDN — *last-winner-airdrop*: https://blog.csdn.net/Secbit/article/details/81782999
- *Characterizing Code Clones in the Ethereum Smart Contract Ecosystem* (FC20): https://www.ifca.ai/fc20/preproceedings/106.pdf
- LastWinner guide (defunct site, via search cache; Wayback `20220331044704`): https://lastwinner.me/en/guide.html
- Generic FoMo3D clone repos (reference only): https://github.com/reedhong/fomo3d_clone · https://github.com/Jaetoxi/fomo3d

### Not yet checked (leads for a follow-up with web.archive.org access)
- Wayback CDX dump of `lastwinner.me*` → 2018 snapshots + front-end JS bundles (client-side keygen).
- Wayback of `lastwinner.io` / `lastwinner.co` / other TLDs, and the Chinese landing page.
- Chinese APK archives / app-store mirrors for the LW Android package.
- iOS: any archived enterprise-cert / TestFlight / ipa listing.
- BAPT-LW20 / SECBIT follow-up posts naming the proxy-contract deployer addresses (cross-check against our 2018 bankroll clusters).
