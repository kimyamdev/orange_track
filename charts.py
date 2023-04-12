from functions import portfolio_vs_benchmark
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



def NAV_chart(tx_df, custom_prices_df, date_range, bench):

    portfolio_vs_benchmark_df = portfolio_vs_benchmark(tx_df, custom_prices_df, date_range)
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.plot(portfolio_vs_benchmark_df.T['Date'], portfolio_vs_benchmark_df.T['portfolio'], label="portfolio")
    ax.plot(portfolio_vs_benchmark_df.T['Date'], portfolio_vs_benchmark_df.T[bench], label=bench)
    ax.set_title('Portfolio Performance vs ' + bench)
    ax.set_xlabel('Date')
    ax.set_ylabel('Unit Price')
    ax.legend()
    chart_file = 'static/NAV_chart.png'
    fig.savefig(chart_file)
    return chart_file

def current_vs_invested(df):

    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_title('Portfolio current value in SGD vs cumulative invested')
    ax.plot(df['Cumul'], label='Cumul Invested')
    ax.plot(df['Total Portfolio Value (SGD)'], label='Total Portfolio Value SGD')
    ax.plot(df['Gains_Losses'], label='Gains/Losses')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount (SGD)')
    ax.legend()
    chart_file = 'static/current_vs_invested_chart.png'
    fig.savefig(chart_file)
    return chart_file

def scatter_orders_over_time(df, buys_df, sells_df, buy_bubble_sizes, sell_bubble_sizes):
    # create the scatter plot
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.scatter(buys_df['Date'], buys_df['Amount'], s=buy_bubble_sizes, alpha=0.5)
    ax.scatter(sells_df['Date'], sells_df['Amount'], s=sell_bubble_sizes, alpha=0.5)

    # set the x-axis label and format the dates
    ax.set_xlabel('Date')
    fig.autofmt_xdate()

    # add labels to each bubble
    for i, txt in enumerate(buys_df['Asset']):
        ax.annotate(txt, (buys_df['Date'].iloc[i], buys_df['Amount'].iloc[i]))

    for i, txt in enumerate(sells_df['Asset']):
        ax.annotate(txt, (sells_df['Date'].iloc[i], sells_df['Amount'].iloc[i]))

    ax.plot(df['Date'], df['Gains_Losses'], c="black", label="Gains & Losses")

    # add legends
    ax.legend(["BUY", "SELL", "Gains & Losses"])
    chart_file = 'static/scatter_orders_over_time_chart.png'
    fig.savefig(chart_file)
    return chart_file


def pnl_by_stock(sorted_data):

    # create a bar graph with title, x-label, y-label, and values
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.bar(sorted_data.keys(), sorted_data.values())
    ax.set_xticklabels(sorted_data.keys(), rotation=45)
    ax.set_title('P&L by asset (S$k)', fontsize=12)
    ax.set_xlabel('Assets', fontsize=8)
    ax.set_ylabel('Values (in thousands)', fontsize=10)
    # set font size of tick labels
    ax.tick_params(axis='both', which='major', labelsize=7)
    # add values to the top of each bar
    for i, v in enumerate(sorted_data.values()):
        ax.text(i, v, str(round(v/1000, 1)), ha='center', va='bottom')
    # format y-axis labels to display values in thousands
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y/1000) + 'K'))
    chart_file = 'static/pnl_chart.png'
    fig.savefig(chart_file)
    return chart_file

def portfolio_today_chart(portfolio_today_df):

    ### Add AA pie chart
    fig, ax = plt.subplots(figsize=(15, 10))
    plt.title('Asset Allocation')
    plt.pie(portfolio_today_df['val'], labels=portfolio_today_df['Asset_Name'], autopct='%1.1f%%')
    chart_file = 'static/portfolio_today_chart.png'
    fig.savefig(chart_file)
    return chart_file