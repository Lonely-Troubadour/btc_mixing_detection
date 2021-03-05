import blocksci
import pandas as pd
import pymysql

# Blockchain
chain = blocksci.Blockchain("config.txt")
mysql_ip = "127.0.0.1"
user = "admin"
password = "admin"
db = "coinswap"
mysql = pymysql.connect(host=mysql_ip, user=user, password=password, db=db,
                                    cursorclass=pymysql.cursors.DictCursor)

# Open pruned multisig dataset
# df = pd.read_csv("pruned_multisig.csv", skipinitialspace=True)
# Remove transactions that contain too many multisig outputs
# df = df.groupby("hash").filter(lambda x: len(x) < 3)
# Sort by height
# df = df.sort_values("height", ignore_index=True)

length = len()
results = open("coinswap_results.csv", "w")

def check_connection(tx, tx_index, height):
    for input in tx.inputs:
        spent_tx = input.spent_tx
        if spent_tx.index == tx_index:
            return 1
        elif spent_tx.block_height >= height:
            result = check_connection(spent_tx, tx_index, height)
            if result == 1:
                return result
    return 0
    
  
txs = []  
for i in range(0, 10000):
    row = df.iloc[i]
    txid = row[1]
    index = row[2]
    value = row[3]
    height = row[4]
    spending_tx_indx = row[5]
    age = row[6]
    tx = chain.tx_with_hash(txid)
    txs.append((txid, index, value, height, tx, spending_tx_indx, age))
    

cursor = 9999
counter = 0
while txs is not None:
    tx_info = txs.pop(0)
    txid = tx_info[0]
    index = tx_info[1]
    value = tx_info[2]
    height = tx_info[3]
    tx = tx_info[4]
    spending_tx_indx = row[5]
    age = row[6]
     
    print("\rcurrent height: " % height, end = " ", flush = True)

    tmp = 0
    len_txs = len(txs)
    while tmp <= len_txs:
        next_tx_info = txs[tmp]
        
        if height < next_tx_info[3] - 30:
            break
        
        next_txid = next_tx_info[0]
        next_index = next_tx_info[1]
        next_value = next_tx_info[2]
        next_height = next_tx_info[3]
        next_tx = next_tx_info[4]
        next_spending_tx_index = next_tx_info[5]
        next_age = next_tx_info[6]
        tmp += 1
        
        if next_height > height + age:
            continue
        
        if not abs(value.value-next_value.value) < 200000:
            continue
        if check_connection == 1:
            continue
        
        results.write("%d,%s,%s,%d\n"%(counter, txid, next_txid, height))
        counter += 1
            

    cursor += 1
    if cursor < length:
        row = df.iloc[cursor]
        txs.append((row[1], row[2], row[3], row[4], chain.tx_with_hash(row[1]), row[5], row[6]))
