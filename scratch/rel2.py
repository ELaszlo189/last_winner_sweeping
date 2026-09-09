import requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.2); continue
        return []
    return []

collectors=["0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xd7649a840575d5e75b0dc1de1b5e3f1c4f6e0f0c",
 "0x8d7c20e3b88bc70246306d9620c2d555448523f7","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1",
 "0x8393153f2bf8e6a72db78955f9f7f5df3f6c9c8a","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762",
 "0x260d1c4724d15ae5c882d365886fb8cae70a746c","0x86c6391dccf7c73b2119c0fa2630f1fdb5819741",
 "0xdc8f936eaaffd26a68934f43d223fc30e635d3a8","0xc5cd9c9c26aaa150e818a4e841e509baf598e3ad",
 "0x8faa7d838dfe67866452e0cc5159ec603f76e66a","0xbfae3c62faa277c6b7492a1e606aa8675ee62a1a",
 "0x602410c93985a2b2a748bae761c25c3e3e5c4e3a"]

# use etherscan address labels if any (nametag) via 'getaddressinfo' not on free; instead check big known CEX list
CEX = {
 "0x28c6c06298d514db089934071355e5743bf21d60":"Binance 14",
 "0x21a31ee1afc51d94c2efccaa2092ad1028285549":"Binance 15",
 "0xdfd5293d8e347dfe59e90efd55b2956a1343963d":"Binance 16",
 "0x56eddb7aa87536c09ccc2793473599fd21a8b17f":"Binance 17",
 "0x9696f59e4d72e237be84ffd425dcad154bf96976":"Binance 18",
 "0x4976a4a02f38326660d17bf34b431dc6e2eb2327":"Binance 19",
 "0xd551234ae421e3bcba99a0da6d736074f22192ff":"Binance 2",
 "0x564286362092d8e7936f0549571a803b203aaced":"Binance 3",
 "0x0681d8db095565fe8a346fa0277bffde9c0edbbf":"Binance 4",
 "0xfe9e8709d3215310075d67e3ed32a380ccf451c8":"Binance 5",
 "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8":"Binance 7",
 "0xf977814e90da44bfa03b6295a0616a897441acec":"Binance 8 (hot)",
 "0x001866ae5b3de6caa5a51543fd9fb64f524f5478":"Binance 19b",
 "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be":"Binance 1",
 "0x46340b20830761efd32832a74d7169b29feb9758":"Binance: hot",
 "0xa910f92acdaf488fa6ef02174fb86208ad7722ba":"OKX",
 "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b":"OKX 2",
 "0x236f9f97e0e62388479bf9e5ba4889e46b0273c3":"OKX 3",
 "0xa7efae728d2936e78bda97dc267687568dd593f3":"OKX 4",
 "0x2c8fbb630289363ac80705a1a61273f76fd5a161":"OKX 5",
 "0x5041ed759dd4afc3a72b8192c143f72f4724081a":"OKX 6",
 "0x1522900b6dafac587d499a862861c0869be6e428":"Bitfinex",
 "0xdc76cd25977e0a5ae17155770273a65d5f8b3 f9":"?",
 "0x28ffe35688ffffd0659aee2e34778b0ae4e193ad":"Cryptocom",
 "0x21a31ee1afc51d94c2efccaa2092ad1028285549":"Binance",
 "0x0d0707963952f2fba59dd06f2b425ace40b492fe":"Gate.io",
 "0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c":"Gate.io 2",
 "0xd793281182a0e3e023116004778f45c29fc14f19":"Binance-peg tmp",
}
CEX={k.lower():v for k,v in CEX.items()}

conv=collections.Counter()
for a in collectors:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":400,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":400,"sort":"desc"})
    outs=[t for t in n if t["from"].lower()==a.lower() and int(t["value"])>0]
    outv=collections.defaultdict(float); 
    for t in outs: outv[t["to"].lower()]+=int(t["value"])/1e18
    lab = "  ".join(f"{v:.3f}->{d[:12]}{'['+CEX[d]+']' if d in CEX else ''}" for d,v in sorted(outv.items(),key=lambda x:-x[1])[:6])
    bal=call({"module":"account","action":"balance","address":a})
    balv = int(bal)/1e18 if isinstance(bal,str) else (int(bal[0])/1e18 if bal else 0)
    print(f"\n{a}")
    print(f"   ntx(400)={len(n)} bal={balv:.3f} ETH  first={U(n[-1]['timeStamp']) if n else '?'} last={U(n[0]['timeStamp']) if n else '?'}")
    print(f"   out: {lab}")
    for d,v in outv.items(): conv[d]+=v
print("\n=== aggregate downstream destinations from all collectors (ETH) ===")
for d,v in conv.most_common(20):
    print(f"   {v:10.3f}  {d}  {CEX.get(d,'')}")
