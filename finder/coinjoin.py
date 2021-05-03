import blocksci
from collections import Counter
chain = blocksci.Blockchain("config.txt")
f = open('results.txt', 'a') 

block = chain.blocks[253486]
#block = chain.blocks[285212]

counter  = 0
# Problem: wrong condition. Not unique address.
while(block):
    print("\rCurrent height: %d"%(block.height), end="", flush=True)
    txes = block.txes.where(lambda tx:tx.inputs.size>1).where(lambda tx:tx.outputs.size>3)
    for tx in txes:
        ins = tx.inputs.group_by(lambda o1:o1.address, lambda o2:o2.value.size)
        outs = tx.outputs.group_by(lambda o1:o1.address, lambda o2:o2.value.sum)
        num_inputs = len(ins)
        num_outputs = len(outs)
        #print(tx.hash, end=" ")
        #print(ins)
        #print(outs)
        #print(num_inputs, end=" ")
        #print(num_outputs)
    

        if num_inputs < 2 or num_outputs < 4 or num_inputs >= num_outputs or num_inputs < num_outputs/2:
            continue
        # ---
        # Remove satoshi dice address and Op_Return
        skip = 0
        for addr in outs:
            if isinstance(addr, blocksci.MultisigAddress) or isinstance(addr, blocksci.NonStandardAddress):
                #print(tx.hash)
                #print(addr)
                #e.g. 5a6ebc8fb1969f4d79af34006affd69aa0cac5c25bf9e434aec6333f5f71926e
                continue

            if isinstance(addr, blocksci.OpReturn):
                skip = 1
                break
            if addr.address_string[0:5] == "1dice":
                skip = 1
                break
        if skip == 1:
            continue

        count_result = dict(Counter(outs.values()))
        sorted_result = sorted(count_result.items(), key=lambda d: d[1], reverse=True)
        coinjoin_outputs = [val[1] for val in sorted_result if val[1] > 1]
        if not coinjoin_outputs:
            continue
        num_coinjoin_outputs = sum(coinjoin_outputs)
        non_coinjoin_outputs = num_inputs - num_coinjoin_outputs
        if coinjoin_outputs[0] <= num_inputs and num_coinjoin_outputs > non_coinjoin_outputs:
            f.write("INSERT INTO `btc_transactions.coinjoin` (`id`, `txid`, `height`, `time`) VALUES (%s, %s, %d, %s)\n"%(counter, str(tx.hash), tx.block_height, str(tx.block_time)))
            counter += 1
            #print(num_inputs, end=" ")
            #print(num_outputs, end=" ")
            #print(coinjoin_outputs, end="\t")
            #print(tx.hash)

    block=block.next_block

f.close()
