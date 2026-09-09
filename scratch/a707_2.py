import json, requests, time, collections, datetime as dt, csv
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
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.2); continue
        return res
    return None
DR="0xa707034429c8e4e01df056c0cbcf478f0fbefad7"
A279="0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1"; D8D7="0x8d7c20e3b88bc70246306d9620c2d555448523f7"
COLL=set(x.lower() for x in ["0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52",A279,D8D7])
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
CA=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f"])

shared=json.load(open("a707_shared_addresses.json"))
# also compute the 5 "LW player, 0xA707 drained, our op didn't"
a707s=set(json.load(open("a707_senders_full.json"))["senders"])
lw=set(json.load(open("lw_senders_ckpt_slim.json"))["senders"])
drained=set(r["address"].lower() for r in json.load(open("drained_eoas.json")))
extra=sorted((a707s & lw) - drained)
print(f"shared (0xA707 + our op): {len(shared)}   |   LW-player-drained-by-A707-only: {len(extra)}\n")

rows=[]
for grp,addrs in [("SHARED",shared),("A707-ONLY (LW player)",extra)]:
    for a in addrs:
        n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":80,"sort":"asc"}) or []
        i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":80,"sort":"asc"}) or []
        n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
        al=n+i
        ins=sorted([t for t in al if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
        funder=ins[0]["from"].lower() if ins else None
        first=U(n[0]["timeStamp"]) if n else "?"
        lw2018=[t for t in n if (t.get("to") or "").lower()==LW]
        # to A707
        toA707=[t for t in n if (t.get("to") or "").lower()==DR]
        a707_amt = sum(int(t["value"]) for t in toA707)/1e18
        a707_when = U(toA707[0]["timeStamp"]) if toA707 else ""
        # to our collectors
        toOurs=[t for t in n if (t.get("to") or "").lower() in COLL]
        ours_detail = "; ".join(f"{int(t['value'])/1e18:.4f}->{(t.get('to') or '')[:10]}@{U(t['timeStamp'])[:10]}" for t in toOurs)
        # withdraw() calls
        wd=[t for t in n if (t.get("functionName","") or "").startswith("withdraw")]
        rows.append({
          "group":grp, "address":a, "first_tx":first, "n_2018_LW_calls":len(lw2018),
          "first_funder":funder, "funder_is_ClusterA":"yes" if funder in CA else "",
          "sent_to_A707_ETH":round(a707_amt,4), "sent_to_A707_when":a707_when,
          "2026_withdraw_calls":len(wd),
          "sent_to_our_collectors":ours_detail,
        })
        print(f"[{grp}] {a}")
        print(f"   first={first}  2018 LW-calls={len(lw2018)}  funder={funder}{'  <ClusterA>' if funder in CA else ''}")
        print(f"   -> 0xA707: {a707_amt:.4f} ETH @ {a707_when}")
        print(f"   -> our collectors: {ours_detail or '(none)'}   [{len(wd)} withdraw() calls in 2026]")
with open("a707_shared_analysis.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("\nwrote a707_shared_analysis.csv")

# 0xA707 downstream 1-ETH recipients
print("\n=== 0xA707's non-THORChain OUT recipients ===")
for a in ["0x4feea1caeea66b3351ddba68bd80c37c9ed6c3c8","0xbb9bb5361a73e8d93ec3b82780b13b756e3bf9ca"]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"desc"})
    n=n if isinstance(n,list) else []; nd=nd if isinstance(nd,list) else []
    print(f"  {a}: first={U(n[0]['timeStamp']) if n else '?'} last={U(nd[0]['timeStamp']) if nd else '?'} ntx~{len(n)}")
