# Sources

On-chain data is the ground truth (Etherscan / any archive node). The items below are the
secondary sources this investigation drew on. Nothing here is endorsed as fully accurate —
several are 2018 contemporaneous reports and 2026 news coverage.

## LastWinner (2018) — security & background

- **SECBIT Labs — "Last Winner 的最后赢家"** (2018-08-20)
  https://secbit.io/blog/2018/08/20/last-winner-of-lastwinner/
  Chinese-language analysis of LastWinner. Used here for the background it establishes:
  LastWinner shipped Android + iOS apps, was promoted by a "蟻群 / Ant Swarm" fundraising-pyramid
  group, and the alleged ~200,000 ETH of operator bot funding.
  Mirrors: https://zhuanlan.zhihu.com/p/42318584 · https://www.freebuf.com/vuls/181486.html

- **SECBIT Labs — "Trust Wallet's Fomo3D Summer"** (2024)
  The direct precedent for the "weak key generation" hypothesis: Trust Wallet's 2018 iOS build
  seeded its RNG with `srand((unsigned)time(NULL))`, producing same-second wallet collisions;
  >2,100 ETH later drained, and many of the affected wallets had been created specifically to
  play FoMo3D.

- **jiemian.com — "8万笔交易「封死」以太坊网络，只为抢夺 Fomo3D 大奖？"** (2018)
  https://www.jiemian.com/article/2372992.html
  Contemporaneous account of LastWinner congesting Ethereum (~80k tx in 2 days) and the
  bot-driven volume.

- **CoinDesk — "Unstoppable Scams? Ethereum's Gambling Problem Is Only Getting Worse"** (2018-08-17)
  https://www.coindesk.com/markets/2018/08/17/unstoppable-scams-ethereums-gambling-problem-is-only-getting-worse
  English-language coverage of the FoMo3D-clone wave including LastWinner; the "operator used
  its own ETH to fuel bot transactions to fake popularity" framing.

- **"Characterizing Code Clones in the Ethereum Smart Contract Ecosystem"** (FC'20)
  https://www.ifca.ai/fc20/preproceedings/106.pdf
  Establishes LastWinner's bytecode as a near-identical FoMo3D clone.

## The April 2026 dormant-wallet drain (the `0xA707` actor)

- **WazzCrypto** and **Specter** — flagged the incident on X on 2026-04-30. Specter's report is
  what prompted Etherscan to label the destination `Fake_Phishing2831105`.
- **Etherscan** — address label `Fake_Phishing2831105` on
  `0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7`.
- **CryptoSlate — "Someone just drained long-forgotten dormant Ethereum wallets, and the cause
  may trace back years"**
  https://cryptoslate.com/someone-drained-long-forgotten-ethereum-wallets-and-the-cause-may-trace-back-years/
- **CryptoTimes — "Mysterious Wallet Drains 326 ETH from Over 570 Ethereum Addresses"** (2026-05-01)
  https://www.cryptotimes.io/2026/05/01/mysterious-wallet-drains-326-eth-from-over-570-ethereum-addresses/
  Gives the drainer address and the "leaked credentials / LastPass 2022" theory.
- **KuCoin — "Over 500 Dormant Ethereum Wallets Drained in $800K Theft"**
  https://www.kucoin.com/news/flash/over-500-dormant-ethereum-wallets-drained-in-800k-theft
- **TradingView / Coinpedia — "Ethereum Hack Hits 500 Long-Dormant Wallets, $800K Lost"**
  https://www.tradingview.com/news/coinpedia:9b7085b59094b:0-ethereum-hack-hits-500-long-dormant-wallets-800k-lost/
- **Jeff Schvey (Etherscan co-founder), on X:** "Strange wallet draining happening on Eth …
  likely some 3rd party service has access to the private keys and got compromised."
  https://x.com/jeff_schvey/status/2050240258906763360
- Additional coverage (same event): Bitget, Cryptopolitan, Our Crypto Talk, MEXC, HOKANEWS,
  Chainbull, coingabbar — all published 2026-04-30 → 2026-05-03.

## Mechanics reference

- **FoMo3D source (`FoMo3Dlong` + PlayerBook)** — for `determinePID`, `withdraw`,
  `registerNameXID`, `addMeToGame`, and the pID↔address binding rules referenced
  in `llm.txt`. Widely mirrored; the LastWinner deployment is unverified but bytecode-identical
  in the relevant functions.
