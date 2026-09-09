import os, json, requests
from dotenv import dotenv_values

cfg = dotenv_values("../.env")
cfg = {k.strip(): (v.strip() if v else v) for k,v in cfg.items()}
RPC = cfg["RPC_URL"]
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"

def rpc(method, params):
    r = requests.post(RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=60)
    return r.json()

print("== eth_getBalance ==")
b = rpc("eth_getBalance",[C,"latest"])
print(b, int(b["result"],16)/1e18, "ETH")

print("== code size ==")
code = rpc("eth_getCode",[C,"latest"])["result"]
print("bytecode len", len(code))

print("== tx count (nonce) ==")
print(rpc("eth_getTransactionCount",[C,"latest"]))

# Etherscan V2 API
base = "https://api.etherscan.io/v2/api"
p = {"chainid":1,"module":"contract","action":"getsourcecode","address":C,"apikey":ESK}
r = requests.get(base, params=p, timeout=60).json()
res = r["result"][0]
print("== ContractName:", res.get("ContractName"))
print("== Compiler:", res.get("CompilerVersion"))
print("== Proxy:", res.get("Proxy"), res.get("Implementation"))
src = res.get("SourceCode","")
print("== source len", len(src))
open("source_raw.txt","w").write(src)
open("meta.json","w").write(json.dumps(res, indent=2)[:2000])
