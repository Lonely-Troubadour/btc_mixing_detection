import blocksci
chain = blocksci.Blockchain("config.txt")

f = open("multisig_merge.csv", "r")
results = open("pruned_multisig.csv", "w")
count = 0
lines = f.read().split("\n")
length = len(lines)

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

txs = []
for i in range(0, length):
    row = lines[i].split(",")
    txid = row[1]
    height = int(row[2])
    index1 = row[3]
    index2 = row[4]
    tx = chain.tx_with_hash(txid)
    outputs = get_outputs(tx, index1, index2)
    print("\rCurrent count: %d" % count, end = "", flush = True)
    for output in outputs:
        if not output.is_spent:
            continue
        if output.spending_input.age > 30:
            continue
        results.write("%d, %s, %d, %d, %d\n" % (count, output.tx.hash, output.index, output.value, output.block.height))
        count += 1
        
f.close()
results.close()