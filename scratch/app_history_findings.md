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
