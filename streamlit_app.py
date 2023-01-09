import pandas_datareader as pdr
import plotly.graph_objects as go
import streamlit as st
import datetime as dt


def get_stock_data(ticker, start_date, end_date):
    tickers = pdr.get_nasdaq_symbols()
    # Convert the ticker symbol to uppercase
    ticker = ticker.upper()
    # Retrieve the data for the stock
    stock_data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    # Map the ticker symbol to the corresponding company name
    company_name = tickers.loc[ticker, 'Security Name']
    return stock_data, company_name


def get_sp_data(start_date, end_date):
    # Retrieve the data for the S&P 500 over the same time period
    sp_data = pdr.get_data_yahoo('^GSPC', start=start_date, end=end_date)
    return sp_data


def get_returns(stock_data, sp_data):
    # Calculate the return of the stock over the time period
    stock_return = (stock_data['Adj Close'][-1] /
                    stock_data['Adj Close'][0]) - 1
    # Calculate the return of the S&P 500 over the time period
    sp_return = (sp_data['Adj Close'][-1] / sp_data['Adj Close'][0]) - 1
    return stock_return, sp_return


def create_chart(stock_data, sp_data, stock):
    # Create a candlestick chart with plotly.graph_objects
    fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                         open=stock_data['Open'],
                                         high=stock_data['High'],
                                         low=stock_data['Low'],
                                         close=stock_data['Close'],
                                         name=stock)])
    # Add the S&P 500 data to the chart
    fig.add_scatter(x=sp_data.index, y=sp_data['Adj Close'], name='S&P 500')
    return fig


def main():
    st.set_page_config(
        page_title="Stock Backtesting App",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    with st.sidebar:
        with st.form('my_form'):
            # Retrieve the stock data
            tickers = pdr.get_nasdaq_symbols()
            ticker_list = tickers['NASDAQ Symbol'].tolist()
            stock = st.selectbox('Select a ticker symbol', ticker_list)

            # Use the number_input component to create an input box for the simulated investment amount
            investment_amount = st.number_input(
                'Simulated investment amount', value=1000)

            start, end = st.columns(2)
            with start:
                start_date = st.date_input(
                    'Start date', value=dt.date(2017, 12, 22))
            with end:
                end_date = st.date_input('End date')
            submit = st.form_submit_button(label="Submit")

    if submit:
        # Get the stock data and company name
        stock_data, company_name = get_stock_data(stock, start_date, end_date)
        st.subheader(company_name)

        # Get the S&P 500 data
        sp_data = get_sp_data(start_date, end_date)

        # Get the returns for the stock and the S&P 500
        stock_return, sp_return = get_returns(stock_data, sp_data)

        # Convert the investment_amount variable to a float
        investment_amount = float(investment_amount)

        # Calculate the return of the simulated investment
        simulated_return_delta = investment_amount * stock_return

        # Print the simulated return
        col1, col2, col3 = st.columns(3)
        # Display the simulated return using st.metric
        if simulated_return_delta > 0:
            # Calculate simulated_return_delta
            simulated_return = investment_amount + simulated_return_delta
            col1.metric(
                label="Simulated return",
                value=f"${simulated_return:.2f}",
                delta=f"${simulated_return_delta:.2f}"
            )
        else:
            if simulated_return_delta < 0:
                # Calculate simulated_return_delta
                simulated_return = investment_amount + simulated_return_delta
                col1.metric(
                    label="Simulated return",
                    value=f"${simulated_return:.2f}",
                    delta=f"${simulated_return_delta:.2f}"
                )

        # Display the stock return using st.metric
        col2.metric(label=f"{stock} stock return", value=f"{stock_return:.2%}")
        # Display the S&P 500 return using st.metric
        col3.metric(label="S&P 500 return", value=f"{sp_return:.2%}")

        # Create the charts
        st.info(f'{company_name} and S&P 500 Chart')
        fig = create_chart(stock_data, sp_data, company_name)
        # Use st.plotly_chart to display the line chart
        st.plotly_chart(fig, use_container_width=True)

   
if __name__ == '__main__':
    main()
