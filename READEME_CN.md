# btc_mixing_detection

Undergraduate Project Report 2020/21

**Design and Implementation of Detection and Tracking System for Bitcoin Mixed transactions**

本项目包含两个部分，一：搜索比特币区块链网络中的混币交易，位于finder/文件夹下；二：用于展示混币交易数据的网站，包括前端和后端两个部分，位于app/和react-frontend/文件夹下。

## Mixed transactions detection and tracking system

Requirement: Bitcoin Core Client, Bitcoin Full node, BlockSci, Python 3,

### Set up MySQL database

The database should have 4 tables, named *multisig*, *fair_exchange*, *coinjoin*, and *stealth_address*. All of them have same table property: id, txid, height, and time. time is DATETIME format.

### Configure your Bitcoin RPC connection and MySQL connection

In *tools.py*, set up rpc user, password, port in *connect_rpc* function. Set up your mysql user, password,etc. in *connect_mysql* function.

### First Filter from all transactions. (Use Btc core client's rpc)

In *finder.py*, set up **start**, **end**, **option** and **batch**. *Start* is the starting height and *end* is the ending height. *Option* is a byte value indicating which type of transaction to search. *batch* is the batch processed transactions number. By default, the finder searches all types of transactions from 0 block height to the latest block.

| Option(0b) | 0/1      | 0/1           | 0/1                               | 0/1             |
| ---------- | -------- | ------------- | --------------------------------- | --------------- |
| Type       | multisig | fair_exchange | coinjoin(deprecated, dot NOT use) | stealth_address |

After correctly configuring the finder, run the program by

```bash
python finder.py
```

**Note 1:** due to the limitation of Bitcoin core client, filtering larget amount of transactions might take very long time. (personally, more than 1 week to go through around 672,000 blocks). 

**Note 2:** Please do not use this to filter CoinJoin transactions. It is much faster to use blockSci. Personally, the time to go through all transactions to filter out CoinJoin transactions is reduced to several hours. See **Section CoinJoin** below.

### Fair Exchange

In *finder.py*, we have preliminary found all transactions that have the characteristics of Fair Exchange protocol, i.e. transactions' script included in an OP_IF and OP_ELSE code block. Now we further filter out Fair Exchange transactions.

```reStructuredText
 OP_CHECKSIGVERIFY OP_IF .* OP_CHECKSIG OP_ELSE .* (OP_EQUAL.*OP_SWAP.*OP_BOOLOR|OP_EQUALVERIFY.*OP_EQUAL.*) .* OP_ENDIF
```

In *prune_fe.py*, we construct regular expression as above pattern. And search all scripts, including input script and output script from potential fair exchange transactions. 

There is no output after running this program, which means there is no usage of transactions implemented Fair Exchange protocol.

### CoinSwap

In *finder.py*, we get a dataset of all 2-of-2 multisignature transactions. We further prune the dataset by removing transactions having too many intputs or outputs, script contains OP_RETURN,  etc.

#### Code currently lost

有一段代码是找出'multisig'表格里面每个transaction的2-of-2 multisig script的index，不过这段代码我暂时找不到了，

Export data from 'multisig' table from MySQL, change the name of datafile in *prune_multsig.py*.

```python
f = open('your_file_name', 'r')
```

