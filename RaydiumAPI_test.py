import requests
import json

# URL to Raydium's liquidity pools data
url = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"

# Fetch the data
response = requests.get(url)
pools = response.json()

# Save the data to a JSON file for easier inspection
with open('raydium_pools_data.json', 'w') as json_file:
    json.dump(pools, json_file, indent=4)

print('Pools data saved to raydium_pools_data.json')
