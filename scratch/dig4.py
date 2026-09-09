import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.7); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.9); continue
        return res
    return None
infra=set(r["address"].lower() for r in json.load(open("infra_addresses.json")))
also=set(x.lower() for x in ["0x696e01b63189fc476051122c15fcf57b05292cac","0x260d1c4724d15ae5c882d365886fb8cae70a746c","0x86c6391dccf7c73b2119c0fa2630f1fdb5819741","0x0004c3cac4a399d4edae4a157485f2eb28aade92","0x99e03db23a79125f0128288611feedf270a758e4","0x0ec193f5341ac1c7295ef2248ade76a2f8a17dcc","0x3051ea1a3a4a49c7ba5d4833be31da98b1b6a451","0xa271266ea7cf6863e518edc7bb2607349cde2cf1"])
DRAIN=infra|also
CEXP={"dc76cd25977e":"Kraken","28ffe35688ff":"Crypto.com","46340b208307":"Binance","a910f92acdaf":"OKX","6cc5f688a315":"OKX","0d0707963952":"Gate","1c4b70a39684":"Gate","fe9e8709d321":"Binance","5041ed759dd4":"OKX"}

for lab,a in [("2026-03-14 sweep dest","0xa03400e098"),("2023-09-26 sweep dest","0xb9f775179b"),
              ("2018 1551-ETH dest 0x04645af26b","0x04645af26b"),("2018 4156-ETH dest 0x6f50c6bff0","0x6f50c6bff0")]:
    # need full addr - resolve from a cluster wallet's txlist
    src=call({"module":"account","action":"txlist","address":"0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","page":1,"offset":10000,"sort":"desc"})
    full=None
    for t in (src if isinstance(src,list) else []):
        for x in (t.get("to"),t.get("from")):
            if x and x.lower().startswith(a.lower()): full=x.lower()
    if not full:
        # try neighbor
        src=call({"module":"account","action":"txlist","address":"0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","page":1,"offset":10000,"sort":"desc"})
        for t in (src if isinstance(src,list) else []):
            for x in (t.get("to"),t.get("from")):
                if x and x.lower().startswith(a.lower()): full=x.lower()
    if not full:
        print(f"{lab}: could not resolve full addr for {a}"); continue
    n=call({"module":"account","action":"txlist","address":full,"page":1,"offset":50,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":full,"page":1,"offset":50,"sort":"desc"})
    ncq=call({"module":"proxy","action":"eth_getTransactionCount","address":full,"tag":"latest"})
    bal=call({"module":"account","action":"balance","address":full})
    al=(n if isinstance(n,list) else [])+(nd if isinstance(nd,list) else [])
    cp=collections.Counter()
    cexhit=set()
    for t in al:
        o=(t.get("to") if t["from"].lower()==full else t["from"]) or ""
        cp[o.lower()]+=1
        for pre,name in CEXP.items():
            if pre in o.lower(): cexhit.add(name)
    dr=[t for t in al if t["from"].lower() in DRAIN or (t.get("to") or "").lower() in DRAIN]
    fdt=U(n[0]["timeStamp"]) if isinstance(n,list) and n else "?"
    ldt=U(nd[0]["timeStamp"]) if isinstance(nd,list) and nd else "?"
    print(f"\n{lab}: {full}")
    print(f"   first={fdt} last={ldt} nonce={int(ncq,16) if isinstance(ncq,str) and ncq.startswith('0x') else '?'} bal={int(bal)/1e18 if isinstance(bal,str) and bal.lstrip('-').isdigit() else '?'}")
    print(f"   CEX touches: {cexhit or 'none'}")
    print(f"   drain-infra touches: {len(dr)}")
    print(f"   top counterparties: {[(k[:14],v) for k,v in cp.most_common(8)]}")
