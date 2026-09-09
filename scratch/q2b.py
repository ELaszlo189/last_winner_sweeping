import requests, time, datetime as dt, json
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(7):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.3)
    return []
# is each infra-funder a 2018 LastWinner fleet wallet? check first tx + LW balance + trackA membership
ta=json.load(open("trackA_senders.json")); trackA=set(ta["a279"])|set(ta["8d7c"])
bal={r["address"].lower():r["balance_eth"] for r in json.load(open("balances.json"))["balances"]}
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
funders={
 "0x696e01b63189fc476051122c15fcf57b05292cac":"Jul collector 0xa279ffef funder",
 "0x260d1c4724d15ae5c882d365886fb8cae70a746c":"Aug-24 collector 0x8d7c20e3 funder",
 "0x86c6391dccf7c73b2119c0fa2630f1fdb5819741":"burst-2 collector 0x5723168b funder",
 "0x0004c3cac4a399d4edae4a157485f2eb28aade92":"burst-1 collector 0x8f55b448 funder",
 "0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8":"burst-1 gas funder",
 "0x262386755624eefd0c2d46ccf4a8ad35d480f1ee":"burst-2 fanout 0x3f3ee0a9 funder",
}
for a,lab in funders.items():
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":3,"sort":"desc"})
    n=n if isinstance(n,list) else []; nd=nd if isinstance(nd,list) else []
    lwtx=call({"module":"account","action":"txlist","address":a,"page":1,"offset":100,"sort":"asc"})
    lw_hits=sum(1 for t in (lwtx if isinstance(lwtx,list) else []) if t.get("to","").lower()==LW)
    print(f"{lab}")
    print(f"   {a}  first_tx={U(n[0]['timeStamp']) if n else '?'}  last={U(nd[0]['timeStamp']) if nd else '?'}  LW_txs={lw_hits}  in_trackA={a in trackA}  had_LW_vault={a in bal}")
