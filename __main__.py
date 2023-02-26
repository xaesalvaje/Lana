import backtrader as bt
from strategies import MyStrategy

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.adddata(MyStrategy().data_btc)
    cerebro.run()
    cerebro.plot(style='candlestick')
