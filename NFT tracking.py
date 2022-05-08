import time
import requests
import json
import pandas as pd

url = 'https://api.etherscan.io/api'
NFT = "Otherdeed"
API_KEY = "your API KEY"
OPENSEA_CONTRACT = "0x34d85c9CDeB23FA97cb08333b511ac86E1C4E258"
WETH_CONTRACT = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
NUMBER_OF_DAYS = 7
PRICE_TO_LOOK_ABOVE = 20


# trx = eth.get_erc721_token_transfer_events_by_address("0x2ea4815F47D685eD317e8bd243b89bCb26b369Fa", startblock=14714933, endblock=14716164, sort="asc")
timestamp = int((time.time() - (NUMBER_OF_DAYS * 86400)) // 1)
ADDRESSES = []


def get_transaction_receipt(txn):
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'apikey': API_KEY,
        'txhash': txn
    }
    try:
        r = requests.get(url, params=params)
        json_data = json.loads(r.text)["result"]["logs"]
        return json_data
    except:
        time.sleep(120)
        print("No Internet")
        return get_transaction_receipt(txn)


def remove_duplicates():
    df = pd.read_csv(filepath_or_buffer="final_address.csv")
    df.drop_duplicates(["address"], inplace=True, ignore_index=True)
    df = df[["address", "price", "block"]]
    print(df)
    df.to_csv(path_or_buf="final_address.csv")


# def get_price(trxh, seller, buyer):
#     url_trx = f"https://api.etherscan.io/api?module=account&action=txlistinternal&txhash={trxh}&apikey={API_KEY}"
#     r = requests.get(url_trx).json()
#     for event in r["result"]:
#         if event["to"] == seller:
#             price = int(event["value"], 0)
#             price = price / 10 ** 18
#             print(price)
#             if price > 20:
#                 ADDRESSES.append({"address": seller, "price": price})

# getting the past block

block_params = {
  'module': 'block',
  'action': 'getblocknobytime',
  'timestamp' : timestamp,
  'closest': 'before',
  'apikey': API_KEY
}
r = requests.get(url, params=block_params)
json_data = json.loads(r.text)["result"]
PAST_BLOCK = int(json_data)

# getting the latest block

block_params = {
  'module': 'block',
  'action': 'getblocknobytime',
  'timestamp' : int(time.time()//1),
  'closest': 'before',
  'apikey': API_KEY
}
r = requests.get(url, params=block_params)
json_data = json.loads(r.text)["result"]
LATEST_BLOCK = int(json_data)
NEXT_BLOCK = PAST_BLOCK+40

no_of_loops = int((LATEST_BLOCK-PAST_BLOCK)/40)
with open("results.csv", mode="a") as new:
    new.write("\n")
with open("final_address.csv", mode="a") as new:
    new.write("\n")

for i in range(no_of_loops):

    params = {
      'module': 'logs',
      'action': 'getLogs',
      'fromBlock': PAST_BLOCK,
      'toBlock': NEXT_BLOCK,
      'address': OPENSEA_CONTRACT,
      'apikey': API_KEY
    }
    PAST_BLOCK = NEXT_BLOCK
    NEXT_BLOCK += 40
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]
    string = "0x0000000000000000000000000000000000000000000000000000000000000000"
    for transaction in json_data:
        try:
            mint_lands = int(transaction["topics"][2], 0)
            if transaction["data"] == "0x" and transaction["topics"][1] != string and transaction["topics"][2] != string and mint_lands > 1000:
                df = pd.DataFrame([[transaction["transactionHash"], transaction["topics"][1], transaction["topics"][2]]])
                df.to_csv(path_or_buf="results.csv", mode="a", index=False, header=False)
        except:
            print(transaction["data"], transaction["topics"])

result_df = pd.read_csv(filepath_or_buffer="results.csv")
result_df.drop_duplicates(["transaction_hash"], inplace=True, ignore_index=True)
result_df.to_csv(path_or_buf="results.csv", index=False)

df = result_df

for index, row in df.iterrows():
    trxh = row["transaction_hash"]
    seller = row["Seller"]
    buyer = row["Buyer"]
    price_hex = "0"
    print(trxh)
    # get_price(trxh, seller, buyer)
    data = get_transaction_receipt(trxh)
    if len(data[-1]['data']) < 500:
        price_hex = data[-1]['data'][-64:]
    elif len(data[-2]['data']) < 500:
        price_hex = data[-2]['data'][-64:]
    elif len(data[-3]['data']) < 500:
        price_hex = data[-3]['data'][-64:]
    elif len(data[-4]['data']) < 500:
        price_hex = data[-4]['data'][-64:]
    elif len(data[-5]['data']) < 500:
        price_hex = data[-5]['data'][-64:]
    else:
        continue
    seller_hex = row["Seller"][26:]
    if price_hex == '0x':
        continue
    currency = 'ETH'
    for event in data:

        if seller in event["topics"] and buyer in event["topics"] and price_hex in event["data"]:
            block = event["blockNumber"]
            price_wei = int("0x" + price_hex, 16)
            price_eth = price_wei / 10 ** 18
            print(price_eth, currency)
            if price_eth >= PRICE_TO_LOOK_ABOVE:
                ldf = pd.DataFrame([[seller, price_eth, block]])
                ldf.to_csv(path_or_buf="final_address.csv", mode="a", index=False, header=False)
                ADDRESSES.append({"address": seller, "price": price_eth, "block": block})
        if seller_hex in event["data"] and price_hex in event["data"] and len(event["data"]) < 500:
            block = event["blockNumber"]
            price_wei = int("0x" + price_hex, 16)
            price_eth = price_wei / 10 ** 18
            print(price_eth, currency)
            if price_eth >= PRICE_TO_LOOK_ABOVE:
                ldf = pd.DataFrame([[seller, price_eth, block]])
                ldf.to_csv(path_or_buf="final_address.csv", mode="a", index=False, header=False)
                ADDRESSES.append({"address": seller, "price": price_eth, "block": block})
    print(len(ADDRESSES))
print(ADDRESSES)
odf = pd.DataFrame(ADDRESSES)
odf.to_csv("final_address.csv")
remove_duplicates()

# Getting the NFTs bought after selling
df = pd.read_csv(filepath_or_buffer="final_address.csv")
for index, row in df.iterrows():
    address = "0x" + row["address"][26:]
    block = int(row["block"], 16)
    url_erc721 = f"https://api.etherscan.io/api?module=account&action=tokennfttx&address={address}&page=1&offset=100&startblock={block}&endblock={LATEST_BLOCK}&sort=asc&apikey={API_KEY}"
    r = requests.get(url_erc721).json()
    nfts = []
    [nfts.append(nft["tokenName"]) for nft in r["result"] if nft["tokenName"] != NFT and nft["tokenName"] not in nfts]
    print(r)
    with open(file="purchases.txt", mode="a", encoding="utf-8") as file:
        for nft in nfts:
            file.writelines(f"{address} bought {nft} after selling {NFT}.\n")
        file.writelines("\n")
