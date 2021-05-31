# btc_mixing_detection

Undergraduate Project Report 2020/21

**Design and Implementation of Detection and Tracking System for Bitcoin Mixed transactions**

本项目包含两个部分，一：搜索比特币区块链网络中的混币交易，位于finder/文件夹下；二：用于展示混币交易数据的网站，包括前端和后端两个部分，位于app/和react-frontend/文件夹下。

# Mixed transactions detection and tracking system

Requirement: Bitcoin Core Client, Bitcoin Full node, BlockSci, Python 3,

### Set up MySQL database

数据库需要有4个tables： *multisig*, *fair_exchange*, *coinjoin*, and *stealth_address*. 属性如下： id, txid, height, and time. time 是DATETIME格式.

### Configure your Bitcoin RPC connection and MySQL connection

在tools.py中, 设置 rpc user, password, port 在 *connect_rpc* 函数中. 设置 mysql user, password,etc. 在 *connect_mysql* 函数中.

### First Filter from all transactions. (Use Btc core client's rpc)

In *finder.py*, set up **start**, **end**, **option**. *Start* is the starting height and *end* is the ending height. *Option* is a byte value indicating which type of transaction to search.  By default, the finder searches all types of transactions from 0 block height to the latest block.

| Option(0b) | 0/1      | 0/1           | 0/1                               | 0/1             |
| ---------- | -------- | ------------- | --------------------------------- | --------------- |
| Type       | multisig | fair_exchange | coinjoin(deprecated, dot NOT use) | stealth_address |

for example, option 0b1101 means search multisig, fair_exchange, and stealth_address transactions.

After correctly configuring the finder, run the program by

```bash
python finder.py
```

**Note 1:** due to the limitation of Bitcoin core client, filtering larget amount of transactions might take very long time. (personally, more than 1 week to go through around 672,000 blocks). 

**Note 2:** Do not use this to filter CoinJoin transactions. It is much faster to use blockSci. Personally, the time to go through all transactions to filter out CoinJoin transactions is reduced to several hours. See **Section CoinJoin** below.

**Note 3:** Batch processing is deprecated, since it causes connection failure under heavy data flow.

## Fair Exchange

In *finder.py*, we have preliminary found all transactions that have the characteristics of Fair Exchange protocol, i.e. transactions' script included in an OP_IF and OP_ELSE code block. Now we further filter out Fair Exchange transactions.

```reStructuredText
 OP_CHECKSIGVERIFY OP_IF .* OP_CHECKSIG OP_ELSE .* (OP_EQUAL.*OP_SWAP.*OP_BOOLOR|OP_EQUALVERIFY.*OP_EQUAL.*) .* OP_ENDIF
```

In *prune_fe.py*, we construct regular expression as above pattern. And search all scripts, including input script and output script from potential fair exchange transactions. 

There is no output after running this program, which means there is no usage of transactions implemented Fair Exchange protocol.

## CoinSwap

In *finder.py*, we get a dataset of all 2-of-2 multisignature transactions. We further prune the dataset by removing transactions having too many intputs or outputs, script contains OP_RETURN,  etc.

Create new table in the database, 

| Property name | id   | hash     | index | value   | height | spending_tx_index | age  |
| ------------- | ---- | -------- | ----- | ------- | ------ | ----------------- | ---- |
| Type          | Int  | Var(255) | Int   | Big_int | Int    | Int               | Int  |

then run

```bash
python prune_multisig.py
```

to get the pruned multsignature transactions.

After getting the pruned multisignature dataset, run *coinswap_blocksci.py* to get all potential paired CoinSwap transactions.

```bash
python coinswap_blocksci.py
```

By default, the results are written in a *coinswap_results.csv* file.

## CoinJoin

Simply run *coinjoin.py* to get possible CoinJoin transactions.

```bash
python coinjoin.py
```

The results are stored in *coinjoin_results.sql* file.

## Stealth Address

We already get the results in *finder* program. The results are stored in *stealth_address* table.

# Website

Package lists:

- flask
- pymysql
- Python 3

### Configure database connection

in *app/db.py*, change host, user to your own db configuration.

### Run

in the parent git repository, run

```bash
flask run
```

 to start the web server.

**Note:** The web uses google-font, use VPN if necessary to accelerate the loading speed if you encounter network issue.





## 
