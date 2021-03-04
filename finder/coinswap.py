import blocksci
import csv
chain = blocksci.Blockchain("config.txt")

# f = open("multisig_merge.csv", newline='')
f = open("multisig_merge.csv", 'r')
results = open("coinswap_results.csv", "w")
# with open('multisig_merge.csv', newline='') as f:
# reader = csv.reader(f)
lines = f.read().split('\n')
lines_length = len(lines)

# txs = [chain.tx_with_hash(line.split(',')[1]) for line in lines]
def get_values(tx, index1, index2):
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


txs = []
for i in range(0, 500):
    row = lines[i].split(',') 
    txid = row[1]
    height = int(row[2])
    index1 = row[3]
    index2 = row[4]
    tx = chain.tx_with_hash(txid)
    txs.append((txid, height, index1, index2, tx))

cursor = 499
counter = 0
while txs is not None:
    tx_info = txs.pop(0)
    txid = tx_info[0]
    height = tx_info[1]
    index1 = tx_info[2]
    index2 = tx_info[3]
    tx = tx_info[4]
    
    print("\rcurrent height: " % height, end = " ", flush = True)

    tmp = 0
    len_txs = len(txs)
    values = get_values(tx, index1, index2)
    while tmp <= len_txs:
        next_tx_info = txs[tmp]
        
        if height <= next_tx_info[1] - 30:
            break
        
        next_txid = next_tx_info[0]
        next_height = next_tx_info[1]
        next_index1 = next_tx_info[2]
        next_index2 = next_tx_info[3]
        next_tx = next_tx_info[4]
        next_values = get_values(next_tx, next_index1, next_index2)
        tmp += 1

        flag = 0
        for value in values:
            for next_value in next_values:
                if not abs(value.value-next_value.value) < 200000:
                    continue
                # if tx
                    results.write("%d,%s,%s,%d\n"%(counter, txid, next_txid, height))
                    counter += 1
                    flag = 1
                    break
            if flag == 1:
                break

    cursor += 1
    if cursor < lines_length:
        row = lines[cursor].split(',')
        txs.append((row[1], int(row[2]), row[3], row[4], chain.tx_with_hash(row[1])))
        

f.close()
results.close()