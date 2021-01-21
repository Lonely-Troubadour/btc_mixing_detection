import tools
import time
rpc = tools.connect_prc()
hash = rpc.getblockhash(314248) #423431
block = rpc.getblock(hash, 2)
# hex = "00483045022100bd16b2ffa112937856716909162c00a66e7c5e6cccd0093ec9aece127632f8dc02205a567c53161e5fb62ac8d202acf8f8cc2f5a6496f47a878555dae7ffde85a41d01483045022100ac3c0365e103d97d3cc935755d5177e8f383993a558998200f8537e64f6b520002202216716f7fa54adc69095c4127ff6f97d42e28517a103f7691808db3cde6ee5b014cc9524104a7ada7c84ae36e98735597ee770a7cfd2d5d9398154b088ee352d3a83b21bbf537c0b8e4ea0acc172285b37571a9b1e36c0da387d6d1f361f0b65cad5c3f659e4104fe411f77e5aa50b54e0f2be0204b26cd1d2bf77bf95f2108a6b012e34637289121cd351c696c8a519b4b58674a87e7907385b4a5e7c0cfa5019346c1b04040914104eeffa9bbfe6dd2c99a9747ca5d1c1ebd15fe0344f52ff2915e3c11b3be9be11236895e5514b085c1f8a1bd8ef9c3db0cf1095aaf442cae11d88c3af026fabd1653ae"

txs = block["tx"]
tx = txs[1]
txin = tx['vin']
asm = txin[0]['scriptSig']['asm']

print(asm)
l = asm.split(' ')
print(l)
for item in l:
    if "ALL" in item:
        print("ALL")
        continue
    if item[0:2] == "03" or "04":
        print(item[0:2])
        print("addr")
        continue

# print(tx)
# print(rpc.decodescript(asm))
# asm = rpc.decodescript(hex)['asm']
# list = asm.split(' ')
# print(list[-1])
# print(rpc.decodescript(list[-1]))
# print(rpc.decodescript(asm))
# f = open("tre.txt", "w")
# f.write(str(block))
# f.close()

# t1 = time.time()
# for i in range(100000, 101000):
#     hash = rpc.getblockhash(i)
#     block = rpc.getblock(hash, 2)
#     times = block['time']
#
# t2 = time.time()
# print(t2-t1)
#
# t3 = time.time()
# commands = [ ["getblockhash", i] for i in range(170000, 171000) ]
# hashes = rpc.batch_(commands)
# blocks = rpc.batch_([ [ "getblock", h ] for h in hashes ])
# block_times = [ block["time"] for block in blocks ]
# t4 = time.time()
# print(t4-t3)
