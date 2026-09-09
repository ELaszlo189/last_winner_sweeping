import json, requests, time, collections, datetime as dt, random
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.5); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.7); continue
        return res
    return None

# known 2018 game/dapp contracts
GAMES={
 "0xa62142888aba8370742be823c1782d17a0389da1":"FoMo3D long",
 "0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c":"LastWinner",
 "0x8f8a0f36 e0e6a6a6a": "x",
 "0x39ddc00fbbf3c00d3aac9becb87157de4c637c93":"FoMo3D short(guess)",
 "0xa1b8054de9086f2fb1e5c62a5e0e6a6a6a6a6a6a":"x",
}
KNOWN_CEX={
 "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b":"OKX",
 "0x0d0707963952f2fba59dd06f2b425ace40b492fe":"Gate.io",
 "0x1151314c646ce4e0efd76d1af4760ae66a9fe30f":"Bitfinex",
 "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0":"Kraken",
}
d=json.load(open("drained_eoas.json"))
nlw=[r["address"] for r in d if r["drained_via"]=="looseETH" and r["lw_participant"]=="no"]
random.seed(5); random.shuffle(nlw); SN=nlw[:120]
print("=== what did the NON-LW drained wallets DO in 2018? (sample 120) ===")
cp_hits=collections.Counter(); had_lw_tx=0; had_fomo=0; distinct_contracts=collections.Counter()
firstacts=collections.Counter()
for idx,a in enumerate(SN):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    if not isinstance(n,list): continue
    outs=[t for t in n if t["from"].lower()==a.lower()]
    tos=[ (t["to"] or "").lower() for t in outs]
    if "0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c" in tos: had_lw_tx+=1
    if "0xa62142888aba8370742be823c1782d17a0389da1" in tos: had_fomo+=1
    for t in tos:
        if t and t!=a.lower(): distinct_contracts[t]+=1
    # first outbound action
    if outs:
        fo=outs[0]
        lbl = GAMES.get((fo["to"] or "").lower()) or KNOWN_CEX.get((fo["to"] or "").lower()) or ("EOA/other:"+(fo["to"] or "")[:10])
        firstacts[lbl]+=1
    if idx%30==0: print(f"  {idx}/120",flush=True)
print(f"\ncalled LastWinner in 2018: {had_lw_tx}/120   called FoMo3D-long: {had_fomo}/120")
print("\nmost common contracts these wallets sent to (2018):")
for c,n in distinct_contracts.most_common(15):
    lbl=GAMES.get(c,"") or KNOWN_CEX.get(c,"")
    print(f"   {n:4d}  {c}  {lbl}")
print("\nfirst outbound action of each wallet:")
for k,v in firstacts.most_common(12): print(f"   {v:3d}  {k}")

# --- Cluster A <-> coToken link check ---
print("\n=== Cluster A <-> coToken cluster linkage (2-hop) ===")
A=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f"])
CT=set(x.lower() for x in ["0x03cb0021808442ad5efb61197966aef72a1def96","0xcbeb72c160b4b3610171c393fad311e6ee8daf72","0x105631c6cddba84d12fa916f0045b1f97ec9c268","0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4"])
for a in A:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"desc"})
    al=(n if isinstance(n,list) else [])+(nd if isinstance(nd,list) else [])
    hits=[t for t in al if t["from"].lower() in CT or (t["to"] or "").lower() in CT]
    print(f"  {a}: {len(hits)} direct txs with coToken cluster")
    for t in hits[:3]: print(f"      {U(t['timeStamp'])} {t['from'][:10]}->{(t['to'] or '')[:10]} {int(t['value'])/1e18:.3f}")
