from datetime import date, datetime, timedelta
import yfinance as yf
from assets import fx_universe, asset_universe, investments, uk_stocks
import pandas as pd


def historical_portfolio(tx_df, custom_prices_df):

    ### DEFINING THE HISTORICAL RANGE (CALENDAR) IN A DATAFRAME THAT WE WILL RE-USE
    startdate = tx_df["Date"][1]
    date_range = pd.date_range(start=startdate, end=date.today(), freq='D')
    df_days = pd.DataFrame({'Date': date_range})

    ### BUILDING DAILY HISTORICAL PRICES OF ASSETS AND THEIR FX
    assets_data = {}
    for asset in tx_df['Asset'].unique():

        if asset == 'SGD':
            num = [1] * len(date_range)
            s = pd.Series(num)

            df_prices = pd.DataFrame({'Date': date_range, 'Price': s})
            fx_prices = pd.DataFrame({'Date': date_range, 'FX_Price': s})
            df_days = pd.DataFrame({'Date': date_range})

            asset_prices = df_days.merge(df_prices, on="Date", how="outer")
            asset_prices = asset_prices.ffill()
            asset_prices_df = pd.DataFrame({'Date': date_range, 'Price': asset_prices['Price']})
            asset_prices_df = asset_prices_df.set_index('Date')

            assets_data[asset] = {"Prices": asset_prices_df}

            fx_prices_df = df_days.merge(fx_prices, on="Date", how="outer")
            fx_prices_df = fx_prices_df.ffill()
            fx_prices_df = pd.DataFrame({'Date': date_range, 'FX_Price': fx_prices_df['FX_Price']})
            fx_prices_df = fx_prices_df.set_index('Date')

            assets_data[asset]["FX_Prices"] = fx_prices_df

        elif asset_universe[asset]["Class"] in ["Investment", "Cash"]:
            if asset in uk_stocks:
                assets_data[asset] = asset
                quote = yf.download(tickers=asset, start=startdate, interval="1d") / 100
            else:
                assets_data[asset] = asset
                quote = yf.download(tickers=asset, start=startdate, interval="1d")

            prices = quote['Adj Close'].ffill()

            asset_prices = pd.DataFrame({'Price': prices})
            assets_data[asset] = {"Prices": asset_prices}
            fx_quote = yf.download(tickers=asset_universe[asset]["Ccy"], start=startdate, interval="1d")
            fx_prices = fx_quote['Adj Close'].ffill()
            fx_prices = pd.DataFrame({'FX_Price': fx_prices})
            assets_data[asset]["FX_Prices"] = fx_prices

        elif asset_universe[asset]["Class"] == "Venture":

            #### FILTER CUSTOM PRICES JUST FOR THIS ASSET AND REBUILD DAILY HISTORICAL PRICES
            filtered_custom_prices_df = custom_prices_df[custom_prices_df['Asset'] == asset]
            filtered_custom_prices_df['Unit Price'] = pd.to_numeric(filtered_custom_prices_df['Unit Price'])
            filtered_custom_prices_df["Date"] = pd.to_datetime(filtered_custom_prices_df["Date"], format="%d/%m/%Y")

            if not filtered_custom_prices_df.empty:
                local_start_date=filtered_custom_prices_df["Date"].iloc[0]
            else:
                print("Dataframe is empty!")

            local_date_range = pd.date_range(start=local_start_date, end=date.today(), freq='D')
            local_df_days = pd.DataFrame({'Date': local_date_range})

            prices = local_df_days.merge(filtered_custom_prices_df, on="Date", how="outer")
            prices = prices.sort_values(by="Date", ascending=True)

            prices = prices.ffill()

            prices = prices[prices['Date'] >= startdate]

            asset_prices = pd.DataFrame({'Price': prices['Unit Price']}, index=prices['Date'])
            assets_data[asset] = {"Prices": asset_prices}
            fx_quote = yf.download(tickers=asset_universe[asset]["Ccy"], start=startdate, interval="1d")
            fx_prices = fx_quote['Adj Close'].ffill()
            fx_prices = pd.DataFrame({'FX_Price': fx_prices})
            assets_data[asset]["FX_Prices"] = fx_prices

        else:
            print("Can't find this asset")

    ### ADDING HISTORICAL CUMUL QUANTITIES FOR EACH ASSET TO ASSETS DATA DICT

    for asset in tx_df['Asset'].unique():

        print("############ " + asset + " ############")
        asset_transactions = tx_df[(tx_df['Asset']==asset)]
        asset_transactions = asset_transactions.assign(Date = pd.to_datetime(asset_transactions['Date']))
        asset_transactions = asset_transactions.assign(Quantity = pd.to_numeric(asset_transactions['Quantity']))
        asset_transactions = asset_transactions.groupby('Date').sum()
        asset_transactions = df_days.merge(asset_transactions, on="Date", how="outer")
        asset_transactions = asset_transactions.fillna(0)
        asset_transactions["Cumul_Qty"] = asset_transactions['Quantity'].cumsum()
        asset_transactions = asset_transactions[['Date', 'Cumul_Qty']]
        assets_data[asset]["Qty"] = asset_transactions.set_index(['Date'])
        print("Done!")

    historical_positions = []

    for asset in tx_df['Asset'].unique():
    
        print("#####" + asset + "######")

        df_list = [assets_data[asset]['Prices'], assets_data[asset]['Qty'], assets_data[asset]['FX_Prices']]
        df = pd.concat(df_list, axis=1).reset_index()
        df['Price'] = df['Price'].ffill()
        df['FX_Price'] = df['FX_Price'].ffill()
        df['Asset'] = asset
        df['Class'] = asset_universe[asset]["Class"]
        df['Currency'] = asset_universe[asset]["Ccy"]
        df = df.fillna(0)

        if asset_universe[asset]['Class'] == 'Cash':
            df[str('total_position_'+ asset)] = df['Cumul_Qty'] * df['Price']
        else:
            df[str('total_position_' + asset)] = df['Cumul_Qty'] * df['Price'] * df['FX_Price']
        
        historical_positions.append(df)

    concat_list = []

    for df in historical_positions:
        df = df.filter(regex=("total_position_.*"))
        concat_list.append(df)

    hist_ptf_df = pd.concat(concat_list, axis=1)
    hist_ptf_df = hist_ptf_df.ffill()

    cols = hist_ptf_df.columns
    hist_ptf_df["Total Portfolio Value (SGD)"] = hist_ptf_df.sum(axis=1)

    hist_ptf_df[cols]  = hist_ptf_df[cols].div(hist_ptf_df[cols].sum(axis=1), axis=0)
    hist_ptf_df["perf"] = hist_ptf_df["Total Portfolio Value (SGD)"].pct_change()

    hist_ptf_df = hist_ptf_df.set_index(date_range)
    hist_ptf_df = hist_ptf_df.reset_index()
    hist_ptf_df = hist_ptf_df.rename({'index': 'Date'}, axis=1)

    return hist_ptf_df