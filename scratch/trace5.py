import json, requests, collections, time, datetime as dt, sys
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.5); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.5); continue
        return []
    return []
def txs(addr, sort="asc", n=100):
    return call({"module":"account","action":"txlist","address":addr,"page":1,"offset":n,"sort":sort})
def bal(addr):
    r=call({"module":"account","action":"balancemulti","address":addr}) or []
    return None
G="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C".lower()
intl=call({"module":"account","action":"txlistinternal","address":G,"page":1,"offset":1000,"sort":"desc","startblock":0,"endblock":99999999})
io=sorted([t for t in intl if t["from"].lower()==G], key=lambda x:-int(x["value"]))
print("top vaults in last ~1000 internal txs:", U(int(io[-1]['timeStamp'])), "->", U(int(io[0]['timeStamp'])))
for t in io[:15]:
    print(f"  {int(t['value'])/1e18:9.4f} ETH  {t['to']}  {U(t['timeStamp'])}")
sys.stdout.flush()

print("\n=== 2-hop follow of top 6 ===")
for t in io[:6]:
    a=t["to"]; amt=int(t["value"])/1e18
    tl=txs(a,"asc",60)
    outs=[x for x in tl if x["from"].lower()==a.lower() and int(x["value"])>0]
    print(f"\n{a}  ({amt:.3f} ETH withdrawn)  ntx={len(tl)}")
    for o in outs[-3:]:
        d=o["to"]
        print(f"  hop1 -> {int(o['value'])/1e18:.4f} ETH  {d}  @{U(o['timeStamp'])}")
        tl2=txs(d,"asc",60)
        o2=[x for x in tl2 if x["from"].lower()==d.lower() and int(x["value"])>0]
        for x in o2[-3:]:
            print(f"        hop2 -> {int(x['value'])/1e18:.4f} ETH  {x['to']}  @{U(x['timeStamp'])}  (dest ntx={len(txs(x['to'],'desc',1))})")
    sys.stdout.flush()
