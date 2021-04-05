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
# length = 14396963

# Open pruned multisig dataset
# df = pd.read_csv("pruned_multisig.csv", skipinitialspace=True)
# Remove transactions that contain too many multisig outputs
# df = df.groupby("hash").filter(lambda x: len(x) < 3)
# Sort by height
# df = df.sort_values("height", ignore_index=True)


print("Reading database...")
def get_dat(offset, limit):
    with mysql.cursor() as cursor:
        cursor.execute("SELECT * FROM ordered_multisig LIMIT offset, limit;" % (offset, limit))
        dat = cursor.fetchall()
    return dat

results = open("updated_coinswap_results.csv", "w")
results.write("id, txid, next_txid, height, index, next_index\n")

def check_connection(tx, target_index, height):
    tx_list = [tx]
    index_list = [tx.index]
    visited = []
    while len(tx_list)!=0:
        tx = tx_list.pop(0)
        tx_index = index_list.pop(0)
        if target_index == tx_index:
            return 1

        visited.append(tx_index)
        for tx_input in tx.inputs:
            spent_tx = tx_input.spent_tx
            spent_index = spent_tx.index
            if spent_index in visited or spent_index in index_list:
                continue
            elif spent_tx.block_height >= height:
                tx_list.append(spent_tx)
                index_list.append(spent_tx.index)
    return 0

   
def extract_dat(row):
    txid = row['hash'].strip()
    index = row['index']
    value = row['value']
    height = row['height']
    spending_index = row['spending_index']
    age = row['age']
    tx = chain.tx_with_hash(txid)
    return txid, index, value, height, tx, spending_index, age
  
txs = []
# dat = get_dat(0)
with mysql.cursor() as cursor:
    cursor.execute("SELECT * FROM ordered_multisig LIMIT offset, limit;" % (offset, limit))
    dat = cursor.fetchall()

# n = 10000
for i in range(0, 10000):
    row = dat.pop(0)
    txs.append(extract_dat(row))
    

counter = 0
while len(txs) != 0:
    tx_info = txs.pop(0)
    txid = tx_info[0]
    index = int(tx_info[1])
    value = tx_info[2]
    height = tx_info[3]
    tx = tx_info[4]
    spending_tx_index = tx_info[5]
    age = tx_info[6]
     
    print("\rcurrent height: %s" % height, end = " ", flush = True)
    #print("current height: %s" % height)

    tmp = 0
    len_txs = len(txs)
    while tmp < len_txs:
        next_tx_info = txs[tmp]
        tmp += 1 

        if height < next_tx_info[3] - 30:
            break
        
        next_txid = next_tx_info[0]
        if next_txid == txid:
            continue

        next_index = int(next_tx_info[1])
        next_value = next_tx_info[2]
        next_height = next_tx_info[3]
        next_tx = next_tx_info[4]
        next_spending_tx_index = next_tx_info[5]
        if tx.outputs[index].address == next_tx.outputs[next_index].address:
            continue

        next_age = next_tx_info[6]
        
        if next_height > height + age:
            continue
        
        if not abs(value-next_value) < 200000:
            continue
        
        #print("tx: %s, next_tx: %s, txindex: %s, height: %d"%(txid, next_txid, tx.index, height))
        #print("checking connection")
        if check_connection(next_tx, tx.index, height) == 1:
            continue
        
        results.write("%d,%s,%s,%d,%d,%d\n"%(counter, txid, next_txid, height, index, next_index))
        counter += 1
        txs.pop(tmp - 1)
        if counter % 10000 == 0:
            results.flush()
        break
            
    if len(dat) != 0:
        row = dat.pop(0)
        txs.append(extract_dat(row))
    # else:
    #     dat = get_dat(n)
    #     n += 10000
    #     row = dat.pop(0)
    #     txs.append(extract_dat(row))
