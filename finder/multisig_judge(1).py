from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import pymysql

RPC_USER = 'bitcoin'
RPC_PASSWORD = '123456'
RPC_IP = '127.0.0.1'

# RPC_IP = '10.108.21.91'
RPC_PORT = 8332
mysql_ip = "10.108.20.101"
user = "root"
password = "123456"
port = 3306
database = "trans_model"
db = pymysql.connect(host=mysql_ip, user=user, password=password, port=port, database=database)
cursor = db.cursor()
start = 100000
end = 650000
rpc_connection = AuthServiceProxy('http://%s:%s@%s:%d' % (RPC_USER, RPC_PASSWORD, RPC_IP, RPC_PORT))

for height in range(start, end):
    print(height)

    block_hash = rpc_connection.getblockhash(height)
    block = rpc_connection.getblock(block_hash, 2)

    # print(block)
    txs = block['tx']

    for tx in txs:
        flag = 0

        txin = tx["vin"]
        txout = tx["vout"]

        for item in txin:
            if "scriptSig" not in item:
                continue

            if "asm" in item["scriptSig"]:
                asm = item["scriptSig"]["asm"]

            if "OP_CHECKMULTISIG" in asm:
                print(asm)

            if "2 OP_CHECKMULTISIG" in asm and asm[0] == "2":
                flag = 1
                break

        for item in txout:
            asm = item["scriptPubKey"]["asm"]

            if "OP_CHECKMULTISIG" in asm:
                print(asm)

            if "2 OP_CHECKMULTISIG" in asm and asm[0] == "2":
                flag = 1
                break

        if flag == 1:
            print(tx["txid"])

        sql = "insert into double_multisig (tx_hash,height) VALUES ('{}','{}')".format(tx["txid"], height)
        cursor.execute(sql)
        db.commit()
