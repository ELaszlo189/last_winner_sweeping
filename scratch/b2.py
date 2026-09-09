import json, requests, time, collections, datetime as dt, csv
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
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
def page(module,action,addr):
    out=[]; cur=0
    while True:
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    return out

# --- track-A loose-ETH sweep sender sets ---
aSenders=set(); dSenders=set()
for t in page("account","txlist","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1"):
    if t["to"].lower()=="0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1" and int(t["value"])>0:
        aSenders.add(t["from"].lower())
for t in page("account","txlist","0x8d7c20e3b88bc70246306d9620c2d555448523f7"):
    if t["to"].lower()=="0x8d7c20e3b88bc70246306d9620c2d555448523f7" and int(t["value"])>0:
        dSenders.add(t["from"].lower())
print("0xa279ffef senders:", len(aSenders), " 0x8d7c20e3 senders:", len(dSenders))
json.dump({"a279":list(aSenders),"8d7c":list(dSenders)}, open("trackA_senders.json","w"))

FLEET_FUNDERS=set(x.lower() for x in [
 "0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914",
 "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
 "0x73957709695e73fd175582105c44743cf0fb6f2f","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1",
 "0xb2a48f542dc56b89b24c04076cbe565b3dc58e7b","0x6e0bf5fd188f59cc8b64569d211912d8248d883d",
 "0x03cb0021808442ad5efb61197966aef72a1def96","0x105631c6cddba84d12fa916f0045b1f97ec9c268"])

u=json.load(open("unclaimed.json"))
TOP=[a for a,v in u[:350]]
BAL=dict(u)
rows=[]
cls=collections.Counter(); clseth=collections.defaultdict(float)
for idx,a in enumerate(TOP):
    code=call({"module":"proxy","action":"eth_getCode","address":a})
    isC = isinstance(code,str) and len(code)>2
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":80,"sort":"asc"})
    if not isinstance(n,list): n=[]
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":40,"sort":"asc"})
    if not isinstance(i,list): i=[]
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":10,"sort":"desc"})
    if not isinstance(nd,list): nd=[]
    first_blk=int(n[0]["blockNumber"]) if n else 0
    first_dt=U(n[0]["timeStamp"]) if n else "?"
    last_dt=U(nd[0]["timeStamp"]) if nd else "?"
    ntx=len(n)
    ins=sorted([t for t in n+i if t.get("to","").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    funder=ins[0]["from"].lower() if ins else None
    launch = 6095000 <= first_blk <= 6135000
    fleetfund = funder in FLEET_FUNDERS
    trackA = a in aSenders or a in dSenders
    dormant = (last_dt < "2026-01-01") if nd else False
    # classify
    if isC:
        c="CONTRACT"
    elif trackA:
        c="FLEET_trackA_swept_not_yet_withdrawn"
    elif fleetfund and launch:
        c="FLEET_funded_by_known_bankroll"
    elif launch and dormant:
        c="cohort_dormant_unattributed"
    elif last_dt>="2026-01-01":
        c="ACTIVE_2026_independent"
    else:
        c="other"
    cls[c]+=1; clseth[c]+=BAL[a]
    rows.append(dict(address=a,bal=round(BAL[a],4),is_contract=isC,first=first_dt,first_blk=first_blk,
                     last=last_dt,ntx=ntx,funder=funder,launch_week=launch,fleet_funder=fleetfund,
                     trackA_swept=trackA,cls=c))
    if idx%50==0: print(f"  {idx}/{len(TOP)}",flush=True)

with open("unclaimed_top_classified.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("\n=== classification of top",len(TOP),"unclaimed (", round(sum(BAL[a] for a in TOP),2),"ETH ) ===")
for c,n in cls.most_common():
    print(f"  {n:4d} addrs  {clseth[c]:9.3f} ETH   {c}")
