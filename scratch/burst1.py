import requests, time, collections, json, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return r.get("result")
    return []
# burst1 recipients: LW internal-out during W17-18 2026 (~Apr20-May6). Use camp_intl.
intl=json.load(open("camp_intl.json"))
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
b1=[t for t in intl if t["from"].lower()==LW and "2026-04-15"<=U(t["timeStamp"])[:10]<="2026-05-10"]
print("burst-1 internal-out events:",len(b1), "  ETH", sum(int(t['value']) for t in b1)/1e18)
recips=list(dict.fromkeys(t["to"] for t in b1))
print("unique recipients:",len(recips))
# for a sample, find where they swept
dest=collections.Counter(); gasfrom=collections.Counter()
for a in recips[:60]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    if not isinstance(n,list) or not n: continue
    y26=[t for t in n if U(t["timeStamp"])[:7] in ("2026-04","2026-05")]
    gin=[t for t in y26 if t["to"].lower()==a.lower() and int(t["value"])>0]
    gout=[t for t in y26 if t["from"].lower()==a.lower() and int(t["value"])>0 and t["to"].lower()!=LW]
    if gin: gasfrom[gin[0]["from"].lower()]+=1
    if gout: dest[gout[-1]["to"].lower()]+=1
print("\nburst-1 gas funders:", gasfrom.most_common(6))
print("burst-1 sweep destinations:", dest.most_common(6))
