### QUICK BUILD OF ASSETS UNIVERSE
fx_universe = {
    "USD": {"Name": "USD", "Ticker": "USDSGD=X"},
    "EUR": {"Name": "EUR", "Ticker": "EURSGD=X"},
    "GBP": {"Name": "GBP", "Ticker": "GBPSGD=X"},
}

asset_universe = {
    "TSLA": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Tesla"},
    "COIN": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Coinbase"},
    "SNOW": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Snowflake"},
    "SPCE": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Virgin Galactic"},
    "HOOD": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Robinhood"},
    "META": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Meta Inc."},
    "USDSGD=X": {"Ccy": "USDSGD=X", "Class": "Cash", "Name": "USD"},
    "SGD": {"Ccy": "SGD", "Class": "Cash", "Name": "SGD"},
    "EURSGD=X": {"Ccy": "EURSGD=X", "Class": "Cash", "Name": "EUR"},
    "PDD": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Pinduoduo"},
    "ABNB": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Airbnb"},
    "NVDA": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Nvidia"},
    "TOST": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Toast"},
    "ETH-USD": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Ethereum"},
    "SOL-USD": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Solana"},
    "KAPE.L": {"Ccy": "GBPSGD=X", "Class": "Investment", "Name": "Kape Technologies"},
    "PBEE.L": {"Ccy": "GBPSGD=X", "Class": "Investment", "Name": "Pensionbee"},
    "SGRO.L": {"Ccy": "GBPSGD=X", "Class": "Investment", "Name": "Segro"},
    "GBPSGD=X": {"Ccy": "GBPSGD=X", "Class": "Cash", "Name": "GBP"},
    "MKTX": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "MarketAxess Holdings"},
    "SCHW": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Charles Schwab"},
    "TSM": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Taiwan SMC"},
    "GROW.L": {"Ccy": "GBPSGD=X", "Class": "Investment", "Name": "Molten Ventures Plc"},
    "AT1.L": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Invesco AT1 Capital Bond ETF"},
    "BIRD": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Allbirds"},
    "DLO": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Dlocal"},
    "VET": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Vermilon Energy"},
    "ARCH": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Arch Resources"},
    "Venture_asset_1": {"Ccy": "USDSGD=X", "Class": "Venture", "Name": "Venture_asset_1"},
    "Venture_asset_2": {"Ccy": "USDSGD=X", "Class": "Venture", "Name": "Venture_asset_2"},
    "SHOP": {"Ccy": "USDSGD=X", "Class": "Investment", "Name": "Shopify"},
}

### EXTRACTING THE LIST OF INVESTMENTS IN ASSET UNIVERSE
asset_universe_inv = {k:v for (k,v) in asset_universe.items() if "Investment" in v["Class"] or "Venture" in v["Class"]}
liq_asset_universe_inv = {k:v for (k,v) in asset_universe.items() if "Investment" in v["Class"]}
venture_inv = {k:v for (k,v) in asset_universe.items() if "Venture" in v["Class"]}

liq_investments = liq_asset_universe_inv.keys()
investments = asset_universe_inv.keys()
venture_assets = venture_inv.keys()

### EXTRACTING THE LIST OF UK STOCKS IN ASSET UNIVERSE
uk_stocks_dict = {k:v for (k,v) in asset_universe.items() if "GBPSGD=X" in v["Ccy"] and "Investment" in v["Class"]}
uk_stocks = list(uk_stocks_dict.keys())
uk_stocks

