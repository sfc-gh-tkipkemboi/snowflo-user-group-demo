import pandas_datareader as pdr
import plotly.graph_objects as go
import streamlit as st
import datetime as dt
import pandas as pd


def get_stock_data(ticker, start_date, end_date):
    tickers = pdr.get_nasdaq_symbols()
    ticker = ticker.upper()
    stock_data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    company_name = tickers.loc[ticker, 'Security Name']
    return stock_data, company_name


def get_sp_data(start_date, end_date):
    sp_data = pdr.get_data_yahoo('^GSPC', start=start_date, end=end_date)
    return sp_data


def get_returns(stock_data, sp_data):
    stock_return = (stock_data['Adj Close'][-1] /
                    stock_data['Adj Close'][0]) - 1
    sp_return = (sp_data['Adj Close'][-1] / sp_data['Adj Close'][0]) - 1
    return stock_return, sp_return


def create_chart(stock_data, sp_data, stock):
    fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                         open=stock_data['Open'],
                                         high=stock_data['High'],
                                         low=stock_data['Low'],
                                         close=stock_data['Close'],
                                         name=stock)])
    fig.add_scatter(x=sp_data.index, y=sp_data['Adj Close'], name='S&P 500')
    return fig


def main():
    st.set_page_config(
        page_title="Stock Backtesting App",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title('💹 Backtesting App')
    with st.sidebar:
        st.sidebar.image('assets/gilly-wcWN29NufMQ-unsplash.jpg')
        with st.form('my_form'):
            tickers = pdr.get_nasdaq_symbols()
            ticker_list = tickers['NASDAQ Symbol'].tolist()
            stock = st.selectbox('Select a ticker symbol', ticker_list)
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
        with st.spinner('Loading data...'):
            stock_data, company_name = get_stock_data(stock, start_date, end_date)
            st.subheader(company_name)
            sp_data = get_sp_data(start_date, end_date)
            stock_return, sp_return = get_returns(stock_data, sp_data)
            investment_amount = float(investment_amount)
            simulated_return_delta = investment_amount * stock_return

            with st.container():
                col1, col2, col3 = st.columns(3)
                if simulated_return_delta > 0:
                    simulated_return = investment_amount + simulated_return_delta
                    col1.metric(
                        label="Simulated return",
                        value=f"${simulated_return:.2f}",
                        delta=f"${simulated_return_delta:.2f}"
                    )
                else:
                    if simulated_return_delta < 0:
                        simulated_return = investment_amount + simulated_return_delta
                        col1.metric(
                            label="Simulated return",
                            value=f"${simulated_return:.2f}",
                            delta=f"${simulated_return_delta:.2f}"
                        )
                col2.metric(label=f"{stock} Stock return", value=f"{stock_return:.2%}")
                col3.metric(label="S&P 500 return", value=f"{sp_return:.2%}")

        sp_df = sp_data.rename(columns={'High':'SP_High', 'Low':'SP_Low', 'Open':'SP_Open', 
        'Close':'SP_Close', 'Volume':'SP_Volume', 'Adj Close':'SP_Adj_Close'})

        stock_data_norm = stock_data / stock_data.max()
        stock_return = stock_data_norm['Close'].pct_change()

        sp_data_norm = sp_df / sp_df.max()
        sp_return = sp_data_norm['SP_Close'].pct_change()

        stock_sp = pd.concat([stock_return, sp_return], axis=1)
        tab1, tab2, tab3 = st.tabs(['Daily Return', 'Trading Volume', 'Moving Average Chart'])
        with tab1:
            st.info(f'{company_name} and S&P 500 Daily Return (normalized returns)')
            st.bar_chart(stock_sp, use_container_width=True)
        with tab2:
            st.info(f'{company_name} Trading Volume')
            st.bar_chart(stock_data['Volume'], use_container_width=True)
        with tab3:
            stock_data['MA10'] = stock_data['Close'].rolling(window=10).mean()
            st.info('10-day stock moving average for the closing price')
            st.line_chart(stock_data[['Close', 'MA10']], use_container_width=True)

        st.balloons()

if __name__ == '__main__':
    main()    