import tools
import re
from time import sleep

# import blocksci

mysql = tools.connect_mysql()
rpc = tools.connect_prc()
pattern = re.compile(r' OP_CHECKSIGVERIFY OP_IF .* OP_CHECKSIG OP_ELSE .* (OP_EQUAL.*OP_SWAP.*OP_BOOLOR|OP_EQUALVERIFY.*OP_EQUAL.*) .* OP_ENDIF')

with mysql.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM btc_transactions.fair_exchange;")
    result = cursor.fetchall()
    num = result[0]['COUNT(*)']

f = open("fe_asm.txt", "w")
f2 = open("fe_out_asm.txt", "w")
counter = 0
for n in range(0, num, 1000):
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM btc_transactions.fair_exchange LIMIT %d, 1000;" % n)
        txs = cursor.fetchall()

    for i in range(len(txs)):
        tx = txs[i]
        height = tx['height']
        print("\rCurrent height: %d" % height, end="", flush=True)
        tx = rpc.getrawtransaction(tx['txid'], True)
        ins = tx['vin']
        outs = tx['vout']

        skip = 0
        # skip all txes that contain "op_return"
        for tx_output in outs:
            script = tx_output['scriptPubKey']
            if script['type'] == "nulldata":
                skip = 1
                break
            elif re.search(pattern, tx_output['scriptPubKey']['asm']) is not None:
                f2.write("%s: %s\n"%(tx['txid'], tx_output['scriptPubKey']['asm']))

        if skip == 1:
            continue

        for i in range(len(ins)):
            tx_input = ins[i]
            asm_list = tx_input['scriptSig']['asm'].split(' ')
            if len(asm_list[-1]) % 2 != 0 or re.search('[^0-9a-f]+', asm_list[-1]) is not None:
                continue
            asm = rpc.decodescript(asm_list[-1])['asm']
            if re.search(pattern, tx_output['scriptPubKey']['asm']) is not None:
                f.write("%s: %s\n"%(tx['txid'], asm))

        # with mysql.cursor() as cursor:
        #     cursor.execute(
        #         "INSERT INTO btc_transactions.pruned_multisig_strict (`id`, `txid`, `height`) VALUES (%s, '%s', %s, '%s', '%s')" % (
        #             counter, tx['txid'], height))
        #     counter += 1

    # mysql.commit()

f.close()
f2.close()
mysql.close()
