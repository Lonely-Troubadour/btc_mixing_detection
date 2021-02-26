import tools
import re

# import blocksci

mysql = tools.connect_mysql()
rpc = tools.connect_prc()
counter = 0


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
            out_values.append((tx_output['n'], float(tx_output['value'])))

    if skip == 1 or len(out_values) > 2:
        return None, None

    in_values = []
    for tx_input in ins:
        last_txid = tx_input['txid']
        vout = tx_input['vout']

        asm_list = tx_input['scriptSig']['asm'].split(' ')
        for item in asm_list:
            # Signature
            if "[" in item and "]" in item:
                continue
            # pub key
            if item[0:2] == "02" or item[0:2] == "03" or item[0:2] == "04":
                continue
            # skip non hex string
            if len(item) % 2 != 0 or re.search('[^0-9a-f]+', item) is not None:
                continue

            # Decode redemption script
            decoded = rpc.decodescript(item)
            decoded_asm = decoded['asm']
            if "OP_CHECKMULTISIG" in decoded_asm:
                last_tx = rpc.getrawtransaction(last_txid, True)
                in_values.append((vout, float(last_tx['vout'][vout]['value'])))

    return in_values, out_values


with mysql.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM btc_transactions.multisig;")
    result = cursor.fetchall()
    num = result[0]['COUNT(*)']

for n in range(267400, num, 1000):
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM btc_transactions.multisig LIMIT %d, 1000;" % n)
        txs = cursor.fetchall()

    for i in range(len(txs) - 1):
        tx = txs[i]
        next_index = i + 1
        next_tx = txs[next_index]
        next_txes = []
        height = tx['height']
        next_height = next_tx['height']
        print("\rCurrent height: %d" % height, end="", flush=True)

        # Skip txes whose time gap is larger than 30 blocks
        while height > (next_height - 30):
            next_txes.append(next_tx)
            next_index += 1
            next_tx = txs[next_index]
            next_height = next_tx['height  ']

        if len(next_txes) == 0:
            continue

        tx = rpc.getrawtransaction(tx['txid'], True)
        for next_tx in next_txes:
            next_tx = rpc.getrawtransaction(next_tx['txid'], True)
            ins = tx['vin']
            outs = tx['vout']
            next_ins = next_tx['vin']
            next_outs = next_tx['vout']
            # print(next_ins)
            # print(next_outs)

            cur_in_values, cur_out_values = get_values(ins, outs)
            if not cur_in_values and not cur_out_values:
                continue

            next_in_values, next_out_values = get_values(next_ins, next_outs)
            if not next_in_values and not next_out_values:
                continue

            # Skip cases that have more than 2 sets of 2-of-2 multisig transactions
            if len(next_in_values) > 2 or len(next_out_values) > 2 or len(cur_in_values) > 2 or len(cur_out_values) > 2:
                continue

            # print(tx['txid'], end="\t")
            # print(cur_in_values, end=" ")
            # print(cur_out_values, end=" ")
            # print(next_in_values, end=" ")
            # print(next_out_values)
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

            if next_in_values and not next_out_values:
                next_values = next_in_values
                next_flag_in = 1
            elif next_out_values and not next_in_values:
                next_values = next_out_values
                next_flag_in = 0
            else:
                # print("Special:", end="\t")
                # print(tx['txid'])
                continue

            for cur_value in cur_values:
                for next_value in next_values:
                    if abs(cur_value[1] - next_value[1]) < 0.002:
                        # print("Found: %s" % tx['txid'])
                        # print(cur_in_values, end=" ")
                        # print(cur_out_values, end=" ")
                        # print(next_in_values, end=" ")
                        # print(next_out_values, end=" ")
                        # print(cur_value, end=" ")
                        # print(next_value)

                        with mysql.cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO btc_transactions.coinswap (`id`, `txid_1`, `txid_2`, `in_or_out_1`, `in_or_out_2`, `index_1`, `index_2`) VALUES (%s, '%s', '%s', %s, %s, %s, %s)" % (
                                    counter, tx['txid'], next_tx['txid'], cur_flag_in, next_flag_in,  cur_value[0], next_value[0]))
                            mysql.commit()
                        counter += 1



mysql.close()
