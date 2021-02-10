import tools
import time
from multiprocessing import Process


class Finder:
    def __init__(self):
        print("Initializing...")
        self.rpc_connection = tools.connect_prc()
        self.mysql_connection = tools.connect_mysql()

        if not self.rpc_connection:
            raise Exception("No RPC connection!")
        if not self.mysql_connection:
            raise Exception("No MySql connection!")
        print("Initialization complete. \nConnection setup.")

    def get_height(self):
        """Get current blockchain height

        :return: Current blockchain height
        :rtype: int
        """
        return self.rpc_connection.getblockcount()

    def get_time(self):
        return time.time()

    def find(self, start=0, end=0, batch=4, option=0b1111):
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
        for n in range(start, end, batch):
            t1 = self.get_time()
            # Using batch commands to speed up searching process
            commands = [["getblockhash", i] for i in range(n, n + batch)]
            block_hashes = self.rpc_connection.batch_(commands)
            blocks = self.rpc_connection.batch_([["getblock", hash, 2] for hash in block_hashes])
            t2 = self.get_time()

            # Times and Txs
            time_list = [block['time'] for block in blocks]
            times = [tools.convert_time(time) for time in time_list]
            txs_list = [block['tx'] for block in blocks]

            # Current height
            height = n

            # Go though every transaction
            for txs, block_time in zip(txs_list, times):
                print("\rFetching blocks in %.2f seconds...Current block: %d" % ((t2-t1), height), end='', flush=True)
                # Go through transactions in one block
                for tx in txs:
                    txout = tx["vout"]
                    txin = tx["vin"]
                    txid = tx["txid"]
                    op = 0

                    if flag_coinjoin and height > height_coinjoin and self.find_coinjoin(tx):
                        self.insert_into_db(3, str(counter_coinjoin), txid, height, block_time)
                        counter_coinjoin += 1
                        continue

                    # Checking tx in
                    for item in txin:
                        if "scriptSig" not in item:
                            continue
                        asm = item["scriptSig"]["asm"]
                        op = self.check_scriptSig(asm)
                        if op == 1 and flag_multisig and height > height_multisig:
                            # Create a new record
                            self.insert_into_db(op, str(counter_multisig), txid, height, block_time)
                            counter_multisig += 1
                        elif op == 2 and flag_fe and height > height_fe:
                            self.insert_into_db(op, str(counter_fe), txid, height, block_time)
                            counter_fe += 1

                        if op != 0:
                            break

                    # If already found special tx, continue to next tx
                    if op != 0:
                        continue

                    # Checking tx out
                    for item in txout:
                        asm = item["scriptPubKey"]["asm"]
                        op = self.check_script_type(asm)
                        if op == 1 and flag_multisig and height > height_multisig:
                            # Create a new record
                            self.insert_into_db(op, str(counter_multisig), txid, height, block_time)
                            counter_multisig += 1
                        elif op == 2 and flag_fe and height > height_fe:
                            self.insert_into_db(op, str(counter_fe), txid, height, block_time)
                            counter_fe += 1
                        elif op == 3 and flag_sa and height > height_sa:
                            self.insert_into_db(4, str(counter_sa), txid, height, block_time)
                            counter_sa += 1

                        if op != 0:
                            break

                # Entering next block, height plus 1
                height += 1

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
        with self.mysql_connection.cursor() as cursor:
            cursor.execute(sql)
            rv = cursor.fetchall()
            if rv:
                return int(rv[0]['id'])+1, int(rv[0]['height'])
        return 0, 0

    def find_coinjoin(self, tx):
        num_inputs = len(tx['vin'])
        coinjoin_outputs = self.get_indistinguishable_output(tx['vout'])

        num_coinjoin_outputs = 0
        for item in coinjoin_outputs:
            num_coinjoin_outputs += item[1]

        non_coinjoin_outputs = num_inputs - num_coinjoin_outputs

        if coinjoin_outputs and int(coinjoin_outputs[0][1]) <= num_inputs and num_coinjoin_outputs > non_coinjoin_outputs:
            return 1

        return 0

    def get_indistinguishable_output(self, outputs):
        dict = {}
        for out in outputs:
            value = out['value']
            if str(value) in dict:
                dict[str(value)] += 1
            else:
                dict[str(value)] = 1

        list = sorted(dict.items(), key=lambda d: d[1], reverse=True)

        return [item for item in list if item[1] > 1]


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

        with self.mysql_connection.cursor() as cursor:
            cursor.execute(sql)
        self.mysql_connection.commit()

    def close_connection(self):
        """Close MySql connection"""
        self.mysql_connection.close()

    def decode_script(self, hex_code):
        """Decode hex script

        :return: Decoded asm code
        :rtype: str
        """
        return self.rpc_connection.decodescript(hex_code)

    def check_scriptSig(self, asm):
        """Check scriptSig asm code

        :param str asm: assembly code for tx script Sig
        :return: result: 1 if is multisig tx, 0 otherwise
        :rtype: int
        """
        asm_list = asm.split(' ')
        for item in asm_list:
            # signature
            if "ALL" in item:
                continue
            # pub key
            if item[0:2] == "03" or item[0:2] == "04":
                continue
            decoded = self.decode_script(item)
            decoded_asm = decoded['asm']

            # Check decoded script
            if "OP_UNKNOWN" in decoded_asm or "error" in decoded_asm:
                continue
            elif "2 OP_CHEKMULTISIG" in decoded_asm:
                return 1
            elif "OP_IF" in decoded_asm and "OP_ELSE" in decoded_asm:
                return 2
            else:
                continue
        return 0

    @staticmethod
    def check_script_type(asm):
        """Check if the transaction is multisig transaction

        :param str asm: assembly code for tx outscript
        :return: result: 1 if is multisig tx, 2 if is fair exchange, 0 otherwise
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
    find.find(start=375600, batch=100, option=0b0011)
