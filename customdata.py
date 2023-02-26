import backtrader as bt
import pandas as pd

class CustomData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', None),
        ('timeframe', bt.TimeFrame.Minutes),
        ('compression', 1),
        ('timezone', None),
        ('historic', False),
    )

    def __init__(self, dataname, **kwargs):
        self.df = pd.read_csv(dataname, index_col=0, parse_dates=True)
        self.df.drop(columns=['Unnamed: 0'], inplace=True)
        self.df.rename(columns={'timestamp': 'datetime'}, inplace=True)

        if kwargs.get('historic', False):
            self.df['datetime'] = pd.to_datetime(self.df['datetime'], unit='s')
            self.df.set_index('datetime', inplace=True)

        if kwargs.get('timeframe', None):
            resample_period = str(kwargs['compression'] * int(kwargs['timeframe'].replace('m', ''))) + 'T'
            self.df = self.df.resample(resample_period).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
            self.df.dropna(inplace=True)

        super().__init__(dataname=self.df, **kwargs)

    def start(self):
        super().start()

    def _load(self):
        return self.df.iterrows()

    def _getstatus(self):
        return 0.0

    def stop(self):
        pass
