import backtrader as bt
import backtrader.feeds as btfeeds
import telegram_send
from alpha_vantage.timeseries import TimeSeries

class MyStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('stop_loss_pct', 0.02),
        ('trailing_stop_loss_pct', 0.02)
    )

    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.order = None
        self.stop_loss = None
        self.trailing_stop_loss = None
        self.stop_loss_pct = self.params.stop_loss_pct
        self.trailing_stop_loss_pct = self.params.trailing_stop_loss_pct
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.macd = bt.indicators.MACD(
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )

        self.trade_opened = False
        self.buyprice = 0
        self.sellprice = 0

        ts = TimeSeries(key='N5JL6CMI87ND79YS', output_format='pandas')
        data_btc, _ = ts.get_daily(symbol='BTC', market='USD')
        data_eth, _ = ts.get_daily(symbol='ETH', market='USD')

        self.data_btc = bt.feeds.PandasData(dataname=data_btc)
        self.data_eth = bt.feeds.PandasData(dataname=data_eth)

        self.cerebro.adddata(self.data_btc)
        self.cerebro.adddata(self.data_eth)

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_lower and self.macd.lines.macd > self.macd.lines.signal:
                self.buy()
                self.buyprice = self.data_btc.close[0]
                self.stop_loss = self.buyprice * (1.0 - self.stop_loss_pct)
                self.trailing_stop_loss = self.buyprice * (1.0 - self.trailing_stop_loss_pct)
        else:
            if self.data_btc.close[0] > self.trailing_stop_loss:
                self.trailing_stop_loss = self.data_btc.close[0] * (1.0 - self.trailing_stop_loss_pct)
            if self.data_btc.close[0] < self.stop_loss:
                self.close()
                return

    def notify_order(self, order):
        """ Triggered when an order changes status """
        if order.status in [order.Submitted, order.Accepted]:
            return  # Ignore these events

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at {order.executed.price:.2f}')
                self.buyprice = order.executed.price
                self.trade_opened = True
                self.stop_loss_price = self.buyprice * (1.0 - self.params.stop_loss_pct)
                self.trailing_stop_loss_price = self.buyprice * (1.0 - self.params.trailing_stop_loss_pct)
            else:
                self.log(f'SELL EXECUTED at {order.executed.price:.2f}')
                self.sellprice = order.executed.price
                telegram_send.send(messages=[f'Sell Order: {order.executed.price:.2f}'])
                self.trade_opened = False
                self.stop_loss = None
                self.trailing_stop_loss = None

        # Check if an order has been canceled or rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = order

    def notify_trade(self, trade):
        """ Triggered when a trade is closed """
        if not trade.isclosed:
            return

        self.log(f'OPERATION RESULT (Gross Profit/Loss): {trade.pnl:.2f}')
        self.trade_opened = False
        self.stop_loss = None
        self.trailing_stop_loss = None
