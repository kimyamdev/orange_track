import requests

# set API key and endpoint
api_key = '4YQUJHWIACZQTSKAAHAW8AFAXU6JYXUGHW'
etherscan_endpoint = 'https://api.etherscan.io/api'

# set parameters for API request
payload = {
    'module': 'stats',
    'action': 'ethsupply',
    'apikey': api_key,
    'format': 'json'
}

# send API request and get response
response = requests.get(etherscan_endpoint, params=payload)

# parse response and print number of active wallets
if response.status_code == 200:
    data = response.json()
    active_wallets = data['result']
    print("Number of active Ethereum wallets: ", active_wallets)
else:
    print("Error: ", response.status_code)
