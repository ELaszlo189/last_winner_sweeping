import json, requests, collections, time
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
base = "https://api.etherscan.io/v2/api"
def get(**kw):
    kw.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        r = requests.get(base, params=kw, timeout=90).json()
        if r.get("status")=="1" or isinstance(r.get("result"),list): return r
        time.sleep(1.5)
    return r

for label,a in [("SWEEP_COLLECTOR","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"),
                ("GAS_FUNDER","0x03cb0021808442ad5efb61197966aef72a1def96"),
                ("DEPLOYER","0xeae69cadeb04e66767bd69f52e0fffc28e37d799")]:
    bal = get(module="account",action="balance",address=a)["result"]
    code = requests.get(base, params={"chainid":1,"module":"proxy","action":"eth_getCode","address":a,"apikey":ESK}, timeout=60).json()["result"]
    tl = get(module="account",action="txlist",address=a,page=1,offset=10,sort="asc")["result"]
    tld = get(module="account",action="txlist",address=a,page=1,offset=10000,sort="desc")["result"]
    il = get(module="account",action="txlistinternal",address=a,page=1,offset=10000,sort="desc")["result"]
    print(f"\n===== {label}  {a}")
    print("  balance:", int(bal)/1e18, "ETH   is_contract:", len(code)>2, "  normal_tx_count(cap10k):", len(tld) if isinstance(tld,list) else tld)
    if isinstance(tl,list) and tl:
        print("  first tx:", tl[0]["timeStamp"], tl[0]["from"][:12],"->",(tl[0]["to"] or "")[:12], int(tl[0]["value"])/1e18)
    # outgoing destinations (where does collector forward?)
    outs = collections.Counter()
    outv = collections.Counter()
    for t in (tld if isinstance(tld,list) else []):
        if t["from"].lower()==a.lower():
            outs[t["to"]]+=1; outv[t["to"]]+= int(t["value"])/1e18
    for t in (il if isinstance(il,list) else []):
        if t["from"].lower()==a.lower():
            outs[t["to"]]+=1; outv[t["to"]]+= int(t["value"])/1e18
    print("  TOP OUTGOING dests (count / total ETH):")
    for d,c in outs.most_common(8):
        print("   ", c, f"{outv[d]:.4f} ETH", d)
    inv = sum(int(t["value"]) for t in (il if isinstance(il,list) else []) if t["to"].lower()==a.lower())/1e18
    print("  total ETH in via internal (cap10k):", inv)
