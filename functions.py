from flask import Flask, render_template, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#from google.oauth2.service_account import Credentials
import googleapiclient.discovery
from datetime import date, datetime, timedelta


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import base64
import yfinance as yf
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
import pickle

from assets import fx_universe, asset_universe, investments, uk_stocks
from units_summary import units_summary
from historical_positions import historical_portfolio

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'app_key.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def get_spreadsheet_data_into_a_df(spreadsheet_url, sheet_name):

    service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)
    # Get the spreadsheet ID from the URL
    spreadsheet_id = spreadsheet_url.split('/')[-2]
    # Get the data from the first sheet
    sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    # Convert the data to a Pandas DataFrame
    values = sheet.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

def benchmark_history(ticker, startdate, date_range):

    quote = yf.download(tickers=ticker, start=startdate, interval="1d")
    prices = quote['Adj Close'].ffill()
    df_prices = pd.DataFrame({'Price': prices})
    df_days = pd.DataFrame({'Date': date_range})
    df_prices = df_days.merge(df_prices, on="Date", how="outer")
    df_prices.loc[:, 'Price'] = df_prices.loc[:, 'Price'].ffill() / df_prices.loc[:, 'Price'].iloc[0]
    return df_prices

def portfolio_vs_benchmark(tx_df, custom_prices_df, date_range):

    hist_ptf_df = historical_portfolio(tx_df, custom_prices_df)
    list_values_NAV = get_NAV(tx_df = tx_df, date_range = date_range, hist_ptf_df=hist_ptf_df)
    bench = request.form['benchmark']
    benchmark_hist = benchmark_history(bench, startdate=date_range[0], date_range=date_range)
    list_values_benchmark = benchmark_hist['Price'].tolist()
    portfolio_vs_benchmark_df = pd.DataFrame([date_range, list_values_benchmark, list_values_NAV], index=['Date', bench, 'portfolio'])
    return portfolio_vs_benchmark_df


def orders_by_stock_over_time(tx_df, type, calendar):

    orders = tx_df[(tx_df['Type']==type) & (tx_df['Class']=="Investment")]
    orders['Amount'] = pd.to_numeric(orders['FX'])  * pd.to_numeric(orders['Quantity']) * pd.to_numeric(orders['Cost'])
    orders['Date'] = pd.to_datetime(orders['Date'])
    historical_orders = calendar.merge(orders, on="Date", how="outer")
    historical_orders = historical_orders.fillna(0)
    if type == "SELL":
        historical_orders['Amount'] = - historical_orders['Amount']
    return historical_orders


def cumul_invested(transactions_df, calendar):

    invested = transactions_df[transactions_df['Type']=='IMPORT']
    invested['Amount'] = pd.to_numeric(invested['FX'])  * pd.to_numeric(invested['Quantity']) * pd.to_numeric(invested['Cost'])
    imports_by_day = invested.groupby('Date')['Amount'].sum()
    imports_by_day_df = pd.DataFrame(imports_by_day).reset_index()
    imports_by_day_df['Date'] = pd.to_datetime(imports_by_day_df['Date'])
    cumul_invested = calendar.merge(imports_by_day_df, on="Date", how="outer")
    cumul_invested['Amount'] = cumul_invested['Amount'].fillna(0)
    cumul_invested['Cumul'] = cumul_invested['Amount'].cumsum()
    
    return cumul_invested

def hist_ptf_value_and_cumul_invested(tx_df, calendar, custom_prices_df):

    hist_ptf_value_and_cumul_invested = cumul_invested(tx_df, calendar)[['Date', 'Cumul']].merge(historical_portfolio(tx_df, custom_prices_df), on="Date", how="outer")
    hist_ptf_value_and_cumul_invested = hist_ptf_value_and_cumul_invested.set_index('Date')
    hist_ptf_value_and_cumul_invested['Gains_Losses'] = hist_ptf_value_and_cumul_invested['Total Portfolio Value (SGD)'] - hist_ptf_value_and_cumul_invested['Cumul']
    return hist_ptf_value_and_cumul_invested

def portfolio_today(tx_df, custom_prices_df, asset_universe):

    hist_ptf_df = historical_portfolio(tx_df, custom_prices_df)
    p = hist_ptf_df.tail(1).T.reset_index()
    p = p.rename(columns={p.columns[0]: "attr", p.columns[1]: "val"})
    portfolio_today = p.loc[p.attr.str.match('total_position_.*'), :]
    portfolio_today = portfolio_today.sort_values(by="val", ascending=False)
    portfolio_today['Asset'] = portfolio_today['attr'].map(lambda x: x.lstrip('total_position_').rstrip(''))
    portfolio_today = portfolio_today[['Asset', 'val']]
    portfolio_today = portfolio_today.loc[(portfolio_today['val'] > 0)]
    portfolio_today['Asset_Name'] = portfolio_today['Asset'].map({k: v['Name'] for k, v in asset_universe.items()})
    return portfolio_today

def units_history(tx_df, date_range, hist_ptf_df):
    units_summary_df = units_summary(tx_df, date_range, hist_ptf_df)
    return units_summary_df

def get_NAV(tx_df, date_range, hist_ptf_df):
    list_values_NAV = units_history(tx_df = tx_df, date_range = date_range, hist_ptf_df = hist_ptf_df)['unit price'].tolist()
    return list_values_NAV

# def gen_stock_prices(asset):
#   # Load historical prices of the individual stocks
#   two_yrs_before_start = start_date - timedelta(days=360)
#   quotes = yf.download(tickers=list(investments), start=two_yrs_before_start, interval="1d")
#   df_quotes = quotes['Adj Close'].ffill()
#   stops = df_investments_latest['Trailing Stop Loss']
#   prices = df_quotes[asset]
#   prices_df = pd.DataFrame(prices).reset_index()
#   prices_df["Date"] = pd.to_datetime(prices_df["Date"])
#   asset_transactions = tx_df[(tx_df['Asset']==asset)]
#   asset_transactions = asset_transactions[["Date", "Cost", "Type"]]
#   asset_transactions["Date"] = pd.to_datetime(asset_transactions["Date"])
#   df = prices_df.merge(asset_transactions, on="Date", how="outer")
#   stock_prices = df[["Date", str(asset)]]
#   stock_prices = stock_prices.set_index("Date")
#   stock_prices = stock_prices.dropna()
#   return stock_prices

# def gen_df(asset):
#   # Load historical prices of the individual stocks
#   two_yrs_before_start = start_date - timedelta(days=360)
#   quotes = yf.download(tickers=list(investments), start=two_yrs_before_start, interval="1d")
#   df_quotes = quotes['Adj Close'].ffill()
#   stops = df_investments_latest['Trailing Stop Loss']
#   prices = df_quotes[asset]
#   prices_df = pd.DataFrame(prices).reset_index()
#   prices_df["Date"] = pd.to_datetime(prices_df["Date"])
#   asset_transactions = tx_df[(tx_df['Asset']==asset)]
#   asset_transactions = asset_transactions[["Date", "Cost", "Type"]]
#   asset_transactions["Date"] = pd.to_datetime(asset_transactions["Date"])
#   df = prices_df.merge(asset_transactions, on="Date", how="outer")
#   return df

def generate_nav_chart_image(dates, nav_prices):

    plt.switch_backend('Agg')
    plt.plot(dates, nav_prices)
    plt.xlabel('Date')
    plt.ylabel('NAV')
    plt.title('NAV evolution')
    nav_chart_path = 'static/nav_chart.png'
    plt.savefig(nav_chart_path)
    return nav_chart_path


def send_email(to, subject, body, image_path):
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Create a multipart message container and set the subject and recipient
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # Add the body of the message
        message.attach(MIMEText(body, 'html'))

        # Open the image file and attach it to the message
        with open(image_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<image1>')
            message.attach(img)

        # Create the message and send it
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()

        print(F'sent message to {to} Message Id: {send_message["id"]}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message
