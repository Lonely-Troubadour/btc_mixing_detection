import tools


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
        """
        Get current blockchain height

        :rtype: int
        """
        return self.rpc_connection.getblockcount()

    def find_multisig_and_fair_exchange(self, start=0, end=0, batch=4):
        """Find multisig transaction and fair exchange transactions in bitcoin from block height start to block height
        end.

        :param start: Starting block height
        :type start: int
        :param end: Ending block height
        :type end: int
        :param batch: Batch processing for each rpc connection round trip. Default is 4.
        :type batch: int
        """
        print("Searching multisig tx and fair exchange tx from height {} to {}".format(start, end))
        counter_multisig = 0
        counter_fe = 0

        if end == 0:
            end = self.get_height()

        # Multi thread?
        for n in range(start, end, batch):
            # Using batch commands to speed up searching process
            commands = [["getblockhash", i] for i in range(n, n + batch)]
            block_hashes = self.rpc_connection.batch_(commands)
            blocks = self.rpc_connection.batch_([["getblock", hash, 2] for hash in block_hashes])

            # Times and Txs
            time_list = [block['time'] for block in blocks]
            times = [tools.convert_time(time) for time in time_list]
            txs_list = [block['tx'] for block in blocks]
            print("\rCurrent block: {}".format(n), end='', flush=True)

            # Current height
            height = n
            for txs, time in zip(txs_list, times):
                # Go through transactions in one block
                for tx in txs:
                    txout = tx["vout"]
                    txin = tx["vin"]
                    txid = tx["txid"]

                    # Checking tx in
                    for item in txin:
                        if "scriptSig" not in item:
                            continue

                        asm = item["scriptSig"]["asm"]
                        op = self.check_scriptSig(asm)
                        if op == 1:
                            # Create a new record
                            self.insert_into_db(op, str(counter_multisig), txid, height, time)
                            counter_multisig += 1
                        elif op == 2:
                            self.insert_into_db(op, str(counter_fe), txid, height, time)
                            counter_fe += 1

                        if op != 0:
                            break

                    # Checking tx out
                    for item in txout:
                        asm = item["scriptPubKey"]["asm"]
                        op = self.check_script_type(asm)
                        if op == 1:
                            # Create a new record
                            self.insert_into_db(op, str(counter_multisig), txid, height, time)
                            counter_multisig += 1
                        elif op == 2:
                            self.insert_into_db(op, str(counter_fe), txid, height, time)
                            counter_fe += 1

                        if op != 0:
                            break

                # Entering next block, height plus 1
                height += 1

        # Finish
        self.close_connection()

    def insert_into_db(self, op, id, txid, height, time):
        """Insert transaction data into mysql database"""
        if op == 1:
            sql = "INSERT INTO `multisig` (`id`, `txid`, `height`, `time`) VALUES (%s, '%s', %s, '%s')" % (
            id, txid, height, time)
        elif op == 2:
            sql = "INSERT INTO `fair_exchange` (`id`, `txid`, `height`, `time`) VALUES (%s, '%s', %s, '%s')" % (
            id, txid, height, time)
        else:
            return

        with self.mysql_connection.cursor() as cursor:
            cursor.execute(sql)
        self.mysql_connection.commit()

    def close_connection(self):
        """Close MySql connection"""
        self.mysql_connection.close()

    def decode_script(self, hex_code):
        return self.rpc_connection.decodescript(hex_code)

    def check_scriptSig(self, asm):
        """Check scriptSig asm code"""
        asm_list = asm.split(' ')
        for item in asm_list:
            if "ALL" in item:
                continue
            if item[0:2] == "03" or "04":
                continue
            decoded = self.decode_script(item)
            # Check decoded script
            if "2 OP_CHEKMULTISIG" in decoded:
                return 1
            elif "OP_IF" in decoded and "OP_ELSE" in decoded:
                return 2
            else:
                continue
        return 0

    @staticmethod
    def check_script_type(asm):
        """Check if the transaction is multisig transaction
        :param asm: assembly code for tx outscript
        :type asm: list
        :return: result: 1 if is multisig tx, 0 otherwise
        :rtype: int
        """
        if "2 OP_CHECKMULTISIG" in asm and asm[0] == "2":
            return 1
        elif "OP_IF" in asm and "OP_ELSE" in asm:
            return 2
        else:
            return 0


if __name__ == '__main__':
    find = Finder()
    find.find_multisig_and_fair_exchange(batch=500)
