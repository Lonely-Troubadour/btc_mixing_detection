import blocksci
import tools
import re
from time import sleep

# import blocksci
chain = blocksci.Blockchain("config.txt")
mysql = tools.connect_mysql()
rpc = tools.connect_prc()
counter = 0
results = open("pruned_multisig.csv", "w")

def get_values(ins, outs):
    skip = 0
    # skip all txes that contain "op_return"
    out_values = []
    for tx_output in outs:
        script = tx_output['scriptPubKey']
        if script['type'] == "nulldata":
            skip = 1
            break
        elif "OP_CHECKMULTISIG" in tx_output['scriptPubKey']['asm']:
            out_values.append(tx_output['n'])

    if skip == 1 or len(out_values) > 2:
        return None, None

    in_values = []
    for i in range(len(ins)):
        tx_input = ins[i]
        asm_list = tx_input['scriptSig']['asm'].split(' ')

        if asm_list[0] != "0":
            continue
        if asm_list[-1][0:2] == "52" and asm_list[-1][-4:] == "52ae":
            in_values.append(i)

    return in_values, out_values

def get_outputs(tx, index1, index2):
    value_list = []
    if index1[0] == "1":
        value_list.append(tx.inputs[int(index1[1])].spent_output)
        # print(value1)
    else:
        value_list.append(tx.outputs[int(index1[1])])

    if index2 == "null":
       return value_list 

    if index2[0] == "1":
       value_list.append(tx.inputs[int(index2[1])].spent_output)
       # print(value2)
    else:
        value_list.append(tx.outputs[int(index2[1])])
    
    return value_list

with mysql.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM btc_transactions.multisig;")
    result = cursor.fetchall()
    num = result[0]['COUNT(*)']
    
for n in range(0, num, 1000):
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM btc_transactions.multisig LIMIT %d, 1000;" % n)
        txs = cursor.fetchall()

    for i in range(len(txs)):
        tx = txs[i]
        height = tx['height']
        print("\rCurrent height: %d" % height, end = "", flush=True)
        tx = rpc.getrawtransaction(tx['txid'], True)
        ins = tx['vin']
        outs = tx['vout']

        cur_in_values, cur_out_values = get_values(ins, outs)
        if not cur_in_values and not cur_out_values:
            continue

        # Skip cases that have more than 2 sets of 2-of-2 multisig transactions
        if len(cur_in_values) > 2 or len(cur_out_values) > 2:
            continue

        if cur_in_values and not cur_out_values:
            cur_values = cur_in_values
            cur_flag_in = 1
        elif cur_out_values and not cur_in_values:
            cur_values = cur_out_values
            cur_flag_in = 0
        else:
            print("Special:", end="\t")
            print(tx['txid'])
            continue

        dat1 = "%s%s" % (cur_flag_in, cur_values[0])
        if len(cur_values) == 2:
            dat2 = "%s%s" % (cur_flag_in, cur_values[1])
        else:
            dat2 = "null"

        tx = chain.tx_with_hash(tx['txid'])
        outputs = get_outputs(tx, dat1, dat2)

        for output in outputs:
            if not output.is_spent:
                continue
            age = output.spending_input.age
            if age > 30:
                continue
            # results.write("%d, %s, %d, %d, %d\n" % (counter, output.tx.hash, output.index, output.value, output.block.height))
            with mysql.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pruned_multisig (`id`, `hash`, `index`, `value`, `height`, `spending_tx_index`, `age`) VALUES (%s, '%s', %s, '%s', '%s', '%s', '%s')" % (
                        counter, output.tx.hash, output.index, output.value, output.block.height, output.spending_tx_index, age))
                counter += 1
    mysql.commit()

mysql.close()
