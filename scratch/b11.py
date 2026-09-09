import json, requests
from dotenv import dotenv_values
from eth_utils import keccak
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]; LW="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
S=requests.Session()
def call(data,to=LW):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=20).json()
    return r.get("result")
def sel(sig): return "0x"+keccak(text=sig).hex()[:8]
# plyr_(uint256) public mapping getter -> struct (addr,name,laff,names?) layout varies; try common FoMo3D: (addr, name, laff, keys?, ...)
s_plyr = sel("plyr_(uint256)")
s_pidxaddr = sel("pIDxAddr_(address)")
s_info = sel("getPlayerInfoByAddress(address)")
for pid in [1, 89135, 89136, 89148, 3742]:
    d = s_plyr + hex(pid)[2:].rjust(64,"0")
    r = call(d)
    addr = "0x"+r[26:66] if r and len(r)>=66 else None
    print(f"pID {pid}: plyr_.addr = {addr}")
    if addr:
        # reverse: does that addr resolve back?
        info = call(s_info + addr[2:].rjust(64,"0"))
        if info and len(info)>=66*2:
            w=[info[2+i*64:2+(i+1)*64] for i in range(6)]
            print(f"        getPlayerInfoByAddress({addr[:10]}) -> pID {int(w[0],16)} win {int(w[3],16)/1e18:.3f} gen {int(w[4],16)/1e18:.3f} aff {int(w[5],16)/1e18:.3f}")
        pidx = call(s_pidxaddr + addr[2:].rjust(64,"0"))
        print(f"        pIDxAddr_({addr[:10]}) = {int(pidx,16) if pidx else '?'}")
