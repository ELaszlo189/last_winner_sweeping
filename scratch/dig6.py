import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
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
CAS=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f","0xf7a8af16acb302351d7ea26ffc380575b741724c","0x1b93129f05cc2e840135aab154223c75097b69bf","0xc837f51a0efa33f8eca03570e3d01a4b2cf97ffd","0x636b76ae213358b9867591299e5c62b8d014e372","0x04645af26b54bd85dc02ac65054e87362a72cb22","0x6f50c6bff08ec925232937b204b0ae23c488402a","0xa03400e098f4421b34a3a44a1b4e571419517687"])
LWDEP="0xeae69cadeb04e66767bd69f52e0fffc28e37d799"
COTOKEN=set(x.lower() for x in ["0x03cb0021808442ad5efb61197966aef72a1def96","0xcbeb72c160b4b3610171c393fad311e6ee8daf72","0x105631c6cddba84d12fa916f0045b1f97ec9c268"])

a="0x9c1065e4a2fe67715ce82772cfc223bd76009451"  # BAPT-LW20 paymaster
n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":10000,"sort":"asc"})
i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":2000,"sort":"asc"})
n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
al=n+i
print(f"BAPT-LW20 paymaster {a}: {len(n)} normal + {len(i)} internal txs")
if n: print(f"  first {U(n[0]['timeStamp'])}  last {U(n[-1]['timeStamp'])}")
# funder
ins=sorted([t for t in al if (t.get("to") or "").lower()==a and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
if ins:
    print(f"  first funded by {ins[0]['from']}  ({int(ins[0]['value'])/1e18:.3f} ETH, {U(ins[0]['timeStamp'])})")
    # is that funder a CEX?
cp=collections.Counter()
for t in al:
    o=(t.get("to") if t["from"].lower()==a else t["from"]) or ""
    cp[o.lower()]+=1
print("  top counterparties:", [(k[:14],v) for k,v in cp.most_common(10)])
# links
ca_hits=[t for t in al if t["from"].lower() in CAS or (t.get("to") or "").lower() in CAS]
lwdep_hits=[t for t in al if t["from"].lower()==LWDEP or (t.get("to") or "").lower()==LWDEP]
ct_hits=[t for t in al if t["from"].lower() in COTOKEN or (t.get("to") or "").lower() in COTOKEN]
lw_hits=[t for t in al if (t.get("to") or "").lower()=="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"]
print(f"\n  links: Cluster-A={len(ca_hits)}  LW-deployer={len(lwdep_hits)}  coToken-cluster={len(ct_hits)}  LW-contract-direct={len(lw_hits)}")
for t in ca_hits[:5]: print(f"    CA: {U(t['timeStamp'])} {t['from'][:12]}->{(t.get('to') or '')[:12]} {int(t['value'])/1e18:.3f}")

# how many distinct proxy deployers did it fund?
outs=[t for t in al if t["from"].lower()==a and int(t["value"])>0]
print(f"\n  it made {len(outs)} outbound funding txs; distinct recipients: {len(set((t.get('to') or '').lower() for t in outs))}")
vc=collections.Counter(round(int(t['value'])/1e18,4) for t in outs)
print("  funding amount histogram:", vc.most_common(6))
