import pandas as pd
import numpy as np

def units_summary(tx_df, date_range, hist_ptf_df):

  ## BUILDING HISTORICAL CASH MOVEMENTS IN & OUT OF PORTFOLIO
  portfolio_units = tx_df[tx_df['Type']=='IMPORT']
  portfolio_units.loc[:, "FX"] = pd.to_numeric(portfolio_units.loc[:, "FX"])
  portfolio_units.loc[:, "Cash_Move"] = pd.to_numeric(portfolio_units.loc[:, "Quantity"])
  portfolio_units.loc[:, "Cash_Move_SGD"] = portfolio_units.loc[:, 'FX'] * portfolio_units.loc[:, 'Cash_Move']
  portfolio_units.loc[:, "Cash_Move_SGD"] = portfolio_units.loc[:, "Cash_Move_SGD"].fillna(0)
  portfolio_units_summary = portfolio_units.groupby('Date')['Cash_Move_SGD'].sum()
  units_df = pd.DataFrame(portfolio_units_summary)
  units_df = units_df.reset_index()
  units_df = units_df.assign(Date = pd.to_datetime(units_df['Date']))
  print("DATE RANGE")
  print(date_range)
  print("###############")
  df_days = pd.DataFrame({'Date': date_range}, index=range(len(date_range)))
  units_summary = df_days.merge(units_df, on="Date", how="outer")

  ## PATCHING HISTORICAL VALUE OF PORTFOLIO TO CASH MOVEMENTS
  ptf_sum = hist_ptf_df[['Date', 'Total Portfolio Value (SGD)']] # only keeping columns we are interested here from dataframe of historical portfolio value
  units_summary = ptf_sum.merge(units_summary, on="Date", how="outer")
  units_summary.loc[:, "Cash_Move_SGD"] = units_summary.loc[:, "Cash_Move_SGD"].fillna(0)
  units_summary.loc[:, 'Cash_Move_SGD_cumul'] = units_summary.loc[:, 'Cash_Move_SGD'].cumsum()
  
  ## CALCULATING NAV_PRICE BY BUYING AND SELLING UNITS AT LAST NIGHT NAV
  condition_1 = units_summary.loc[:, 'Cash_Move_SGD']
  condition_2 = units_summary.loc[:, 'Cash_Move_SGD'] / (units_summary.loc[:, 'Total Portfolio Value (SGD)'].shift(1) / units_summary.loc[:, 'Cash_Move_SGD_cumul'].shift(1))
  units_summary.loc[:, 'units created'] = np.where(units_summary['Date']==date_range[0], condition_1, condition_2)
  units_summary.loc[:, 'units created cumul'] = units_summary.loc[:, 'units created'].cumsum()
  units_summary.loc[:, 'unit price'] = units_summary.loc[:, 'Total Portfolio Value (SGD)'] / units_summary.loc[:, 'units created cumul']
  units_summary['cumul_gains'] = units_summary['Total Portfolio Value (SGD)'] - units_summary['Cash_Move_SGD_cumul']
  
  return units_summary