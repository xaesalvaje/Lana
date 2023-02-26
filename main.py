import backtrader as bt
from my_strategy import MyStrategy

if __name__ == '__main__':
    cerebro = bt.Cerebro()  # Create an instance of Cerebro
    cerebro.adddata(MyStrategy().data_btc)

# define parameters
start_cash = 10000.0 
commission_rate = 0.002
stop_loss_pct = 0.05
trailing_stop_loss_pct = 0.02

# add strategy to Cerebro
cerebro.addstrategy(
    MyStrategy,
    rsi_period=14,
    rsi_upper=70,
    rsi_lower=30,
    macd_fast=12,
    macd_slow=26,
    macd_signal=9,
    stop_loss_pct=stop_loss_pct,
    trailing_stop_loss_pct=trailing_stop_loss_pct
)

# add data feed to Cerebro
cerebro.adddata(MyStrategy().data_btc)
cerebro.adddata(MyStrategy().data_eth)

# set broker parameters
cerebro.broker.setcash(start_cash)
cerebro.broker.setcommission(commission=commission_rate)

# run the backtest
cerebro.run()

# print final results
portvalue = cerebro.broker.getvalue()
pnl = portvalue - start_cash
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))
