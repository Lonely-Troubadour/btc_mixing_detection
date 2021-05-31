import tools
import re
from multiprocessing import Process, Lock, Value
from time import sleep

# !important
# Loosen the method for detecting coinjoin transactions from height 340090.
# Need to re-examine the coinjoin found after height 340090.

class Finder:
    def __init__(self):
        print("Initializing...")
        self.rpc = tools.connect_prc()
        self.mysql = tools.connect_mysql()

        if not self.rpc:
            raise Exception("No RPC connection!")
        if not self.mysql:
            raise Exception("No MySql connection!")
        print("Initialization complete. \nConnection setup.")

    def get_height(self):
        """Get current blockchain height

        :return: Current blockchain height
        :rtype: int
        """
        return self.rpc.getblockcount()

    def start(self, start=0, end=0, batch=4, option=0b1111):
        """Find multisig transaction and fair exchange transactions in bitcoin from block height start to block height
        end.

        :param int start: Starting block height
        :param int end: Ending block height
        :param int batch: Batch processing for each rpc connection round trip. Default is 4.
        """
        # init variables
        counter_multisig, height_multisig = self.get_latest_db_info(0)
        counter_fe, height_fe = self.get_latest_db_info(1)
        # counter_coinswap, height_coinswap = self.get_latest_db_info(2)
        counter_coinjoin, height_coinjoin = self.get_latest_db_info(2)
        counter_sa, height_sa = self.get_latest_db_info(3)

        # flags
        flag_multisig = (option & 0b1000) >> 3
        flag_fe = (option & 0b0100) >> 2
        flag_coinjoin = (option & 0b0010) >> 1
        flag_sa = (option & 0b0001)

        if end == 0:
            end = self.get_height()

        print("Search options: multisig: %d\t Fair Exchange: %d\t CoinJoin: %d\t Stealth Address: %d"%(flag_multisig, flag_fe, flag_coinjoin, flag_sa))
        print("Searching txs from height {} to {}".format(start, end))

        # Multi thread?
        for n in range(start, end):
            # t1 = tools.get_time()
            # Using batch commands to speed up searching process
            # commands = [["getblockhash", i] for i in range(n, n + batch)]
            # block_hashes = self.rpc.batch_(commands)
            # blocks = self.rpc.batch_([["getblock", hash, 2] for hash in block_hashes])

            # Times and Txs
            # time_list = [block['time'] for block in blocks]
            # times = [tools.convert_time(time) for time in time_list]
            # txs_list = [block['tx'] for block in blocks]

            block_hash = self.rpc.getblockhash(n)
            block = self.rpc.getblock(block_hash, 2)
            ttime = tools.convert_time(block['time'])
            txs = block['tx']
            # t2 = tools.get_time()

            # Go through transactions in one block
            # t3 = tools.get_time()
            for tx in txs:
                txout = tx["vout"]
                txin = tx["vin"]
                txid = tx["txid"]
                op = 0

                # Skip coinbase tx:
                if "scriptSig" not in txin[0]:
                    continue

                # Checking tx in
                for item in txin:
                    asm = item["scriptSig"]["asm"]
                    op = self.check_scriptSig(asm)
                    if op == 0:
                        continue
                    elif flag_multisig and op == 1 and n > height_multisig:
                        # Create a new record
                        self.insert_into_db(op, str(counter_multisig), txid, n, ttime)
                        counter_multisig += 1
                        break
                    elif flag_fe and op == 2 and n > height_fe:
                        self.insert_into_db(op, str(counter_fe), txid, n, ttime)
                        counter_fe += 1
                        break
                    elif flag_sa and op == 3 and n > height_sa:
                        self.insert_into_db(4, str(counter_sa), txid, n, ttime)
                        counter_sa += 1
                        break

                # print("Check txin: %.4f" % (t6-t5), end="\t")

                # If already found special tx, continue to next tx
                if op != 0:
                    # print(" ")
                    continue

                # Checking tx out
                for item in txout:
                    asm = item["scriptPubKey"]["asm"]
                    op = check_script_type(asm)
                    if op == 0:
                        continue
                    elif flag_multisig and op == 1 and n > height_multisig:
                        # Create a new record
                        self.insert_into_db(op, str(counter_multisig), txid, n,ttime)
                        counter_multisig += 1
                        break
                    elif flag_fe and op == 2 and n > height_fe:
                        self.insert_into_db(op, str(counter_fe), txid, n, ttime)
                        counter_fe += 1
                        break
                    elif flag_sa and op == 3 and n > height_sa:
                        self.insert_into_db(4, str(counter_sa), txid, n, ttime)
                        counter_sa += 1
                        break

                
                if op != 0:
                    continue

                
                # t5 = tools.get_time()
                # if n > height_coinjoin and self.find_coinjoin(tx):
                #     self.insert_into_db(3, str(counter_coinjoin), txid, n, ttime)
                #     counter_coinjoin += 1
                # t6 = tools.get_time()
                # t_cj += t6-t5
                # print("Check coinjoin: %.4f" % (t6-t5), end = "\n")

            # Entering next block, height plus 1
            
            # print("This block: %.2f" % (t4-t3))
            # print("\rFetching blocks in %.2f seconds， check block time %.2f, txin: %.5f, txout: %.5f, coinjoin: %.5f...Current block: %d" % ((t2-t1), (t4-t3), t_txin, t_txout, 0, n), end="", flush=True)
            print("\rCurrent block: %d" % (n), end="", flush=True)

        # Finish
        self.close_connection()

    def get_latest_db_info(self, option):
        """Get the height of latest transaction in db

        :param int option: Option for which table
        :return: 0 if invalid option. Id and Height for the specific option.
        """
        if option == 0:
            table = 'multisig'
        elif option == 1:
            table = 'fair_exchange'
        elif option == 2:
            table = 'coinjoin'
        elif option == 3:
            table = 'stealth_address'
        else:
            return 0

        sql = "select id, height from " + table + " order by id DESC limit 1"
        with self.mysql.cursor() as cursor:
            cursor.execute(sql)
            rv = cursor.fetchall()
            if rv:
                return int(rv[0]['id'])+1, int(rv[0]['height'])
        return 0, 0

    def find_coinjoin(self, tx):
        if len(tx['vin']) < 2 or len(tx['vout']) < 4:
            return 0
        num_inputs = self.get_unique_input_addr_len(tx['vin'])
        print(num_inputs)
        if num_inputs < 2:
            return 0
        coinjoin_outputs, num_outputs = self.get_indistinguishable_output(tx['vout'])
        print(num_outputs)
        if num_outputs < 4:
            return 0
        print(num_outputs)
        print(coinjoin_outputs)
        # Skip all unqualified txs
        if not coinjoin_outputs or num_inputs >= num_outputs or num_inputs < num_outputs/2:
            return 0

        # Calculate all coinjoin outputs
        num_coinjoin_outputs = 0
        for item in coinjoin_outputs:
            num_coinjoin_outputs += item[1]

        non_coinjoin_outputs = num_inputs - num_coinjoin_outputs

        if int(coinjoin_outputs[0][1]) <= num_inputs and num_coinjoin_outputs > non_coinjoin_outputs:
            return 1

        return 0

    def get_last_tx(self, txid):
        hex_tx = self.rpc.getrawtransaction(txid)
        decoded_tx = self.rpc.decoderawtransaction(hex_tx)
        return decoded_tx

    def get_input_address(self, tx, vout):
        pubkey = tx['vout'][vout]['scriptPubKey']
        if pubkey['type'] == 'pubkeyhash':
            return pubkey['addresses']
        # e.g.
        # txid: cba1a3cdf32dc9c9515056d5c0fcba00537cbea1a9ad24ab58b3319b781478a9
        # {'asm': '0424a173e1dcb5a77d7558f479e08fa1806c1a749ea095f10aa4baf888873dfff74f3e7c715d16
        #  d1c4f83a46f50b6cc135348f30e3db4f4a43c4a01d130dc9f510 OP_CHECKSIG', 'type': 'pubkey'}
        elif pubkey['type'] == 'pubkey':
            return pubkey['asm'].split(' ')[0]
        else:
            return 0

    def get_unique_input_addr_len(self, inputs):
        """Get unique input addresses numbers"""
        pubkey_list = []

        for input in inputs:
            last_tx = self.get_last_tx(input['txid'])
            addr = self.get_input_address(last_tx, input['vout'])

            if addr == 0 or addr in pubkey_list:
                continue
            pubkey_list.append(addr)

        return len(pubkey_list)

    def get_indistinguishable_output(self, outputs):
        """Get list of indistinguishable outputs"""
        values = {}
        addr_list = []
        for out in outputs:
            value = out['value']
            # Exclude 1dice
            if out['scriptPubKey']['type'] != 'pubkeyhash':
                continue

            addr = out['scriptPubKey']['addresses']
            if addr[0:5] == "1dice":
                return 0, 0
            if addr in addr_list:
                continue
            addr_list.append(addr)

            if str(value) in values:
                values[str(value)] += 1
            else:
                values[str(value)] = 1

        list = sorted(values.items(), key=lambda d: d[1], reverse=True)

        return [item for item in list if int(item[1]) > 1], len(addr_list)


    def insert_into_db(self, op, id, txid, height, time):
        """Insert transaction data into mysql database"""
        if op == 1:
            table = 'multisig'
        elif op == 2:
            table = 'fair_exchange'
        elif op == 3:
            table = 'coinjoin'
        elif op == 4:
            table = 'stealth_address'
        else:
            return

        sql = "INSERT INTO `" + table + "` (`id`, `txid`, `height`, `time`) VALUES (%s, '%s', %s, '%s')" % (
            id, txid, height, time)

        with self.mysql.cursor() as cursor:
            cursor.execute(sql)
        self.mysql.commit()

    def close_connection(self):
        """Close MySql connection"""
        self.mysql.close()

    def decode_script(self, hex_code):
        """Decode hex script

        :return: Decoded asm code
        """
        return self.rpc.decodescript(hex_code)

    def check_scriptSig(self, asm):
        """Check scriptSig asm code

        :param str asm: assembly code for tx script Sig
        :return: result: 1 if is multisig tx, 2 if is fair exchange, 3 if stealth address, 0 otherwise
        :rtype: int
        """

        asm_list = asm.split(' ')
        for item in asm_list:
            # signature
            if "[" in item and "]" in item:
                continue
            # pub key
            if item[0:2] == "02" or item[0:2] == "03" or item[0:2] == "04":
                continue
            # skip non hex string
            if len(item) % 2 != 0 or re.search('[^0-9a-f]+', item) is not None:
                continue

            # Decode redemption script
            decoded = self.decode_script(item)
            decoded_asm = decoded['asm']

            # Check decoded script
            if "OP_UNKNOWN" in decoded_asm or "error" in decoded_asm:
                continue
            else:
                res = check_script_type(decoded_asm)
                if res != 0:
                    return res
                continue
        return 0

def check_script_type(asm):
    """Check if the transaction is multisig transaction

    :param str asm: assembly code for tx outscript
    :return: result: 1 if is multisig tx, 2 if is fair exchange, 3 if stealth address, 0 otherwise
    :rtype: int
    """
    if "2 OP_CHECKMULTISIG" in asm and asm[0] == "2":
        return 1
    elif "OP_IF" in asm and "OP_ELSE" in asm:
        return 2
    elif "OP_RETURN" in asm:
        asm_list = asm.split(' ')
        if len(asm_list) > 1 and asm_list[1][0:2] == '01' and len(asm_list[1]) == 160:
            return 3
    else:
        return 0


if __name__ == '__main__':
    find = Finder()
    find.start(start=0, batch=80)
