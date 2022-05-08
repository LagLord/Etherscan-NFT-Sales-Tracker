# Etherscan-NFT-Sales-Tracker

Hello, I created this script to track NFT project sales without the use of Opensea API,
directly extracting buffer data from Etherscan logs of any Contract address( of your NFT).


1) You need to have a API key from etherscan.io.
2) Put your API key and the Contract address under OPENSEA_CONTRACT of you want to track sales for.
3) There's a NUMBER_OF_DAYS global variable for how many past days you want to look for sales.
4) There's also another global variable PRICE_TO_LOOK_ABOVE for the filtering out sales based on price of ETH it sold for.
5) Run the script and wait for the results in final_addresses.csv which will store the addresses which sold their NFT.
6) Finally the program will also find the NFTs the addresses bought after selling your NFT.
