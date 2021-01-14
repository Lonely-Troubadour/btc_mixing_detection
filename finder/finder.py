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

    def find_multisig_and_fair_exchange(self, start, end):
        """Find multisig transaction and fair exchange transactions in bitcoin from block height start to block height
        end.

        :param start: Starting block height
        :type start: int
        :param end: Ending block height
        :type end: int
        """
        print("Searching multisig tx and fair exchange tx from height {} to {}".format(start, end))
        counter_multisig = 0
        counter_fe = 0
        if not start:
            start = 100000
        if not end:
            end = self.get_height()

        # Multi thread?
        for n in range(start, end):
            block_hash = self.rpc_connection.getblockhash(n)
            block = self.rpc_connection.getblock(block_hash, 2)
            time = tools.convert_time(block['time'])
            txs = block['tx']
            print("\rCurrent block: {}".format(n), end='', flush=True)

            for tx in txs:
                txout = tx["vout"]
                txin = tx["vin"]
                txid = tx["txid"]

                for item in txout:
                    asm = item["scriptPubKey"]["asm"]
                    with self.mysql_connection.cursor() as cursor:
                        op = self.check_tx_type(asm)
                        if op == 1:
                            # Create a new record
                            sql = "INSERT INTO `multisig` (`id`, `txid`, `height`, `time`) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (str(counter_multisig), txid, str(n), time))
                            counter_multisig += 1
                        elif op == 2:
                            sql = "INSERT INTO `fair_exchange` (`id`, `txid`, `height`, `time`) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (str(counter_fe), txid, str(n), time))
                            counter_fe += 1

                    if op is not 0:
                        self.mysql_connection.commit()
                        break

        # Finish
        self.close_connection()

    def close_connection(self):
        """Close MySql connection"""
        self.mysql_connection.close()

    @staticmethod
    def check_tx_type(asm):
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
    find.find_multisig_and_fair_exchange(100000, 650000)
