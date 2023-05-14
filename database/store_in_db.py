import sqlite3
import numpy as np
import pandas as pd
from indicator.candle_pattern import MakePattern
from indicator.rsi import Rsi
from indicator.moving_average_signal import MovingAverage
from indicator.macd import Macd
from indicator.bollinger_bands import BollingerBand
from indicator.super_trend import SuperTrend
from create_resample_data import Resample
import warnings
warnings.filterwarnings("ignore")

class StoreData:
    def __init__(self, data, connection, cur, symbol):
        self.data = data
        self.connection = connection
        self.cur = cur
        self.symbol = symbol
    def store_symbol(self):
        self.cur.execute("INSERT INTO symbols (symbolName) VALUES (?) RETURNING id", (self.symbol,))
        symbol_id = self.cur.fetchone()[0]
        return symbol_id
    def store_asset(self, symbol_id):
        df = self.data.copy()
        df.reset_index(inplace=True)  # Convert index to column
        time_col = df.pop('Time')  # Remove Time column and store it in variable
        df.insert(len(df.columns), 'Time', time_col)  # Insert Time column at the end
        df.drop("symbol", axis=1, inplace=True)
        change = df.pop("Change")
        df.insert(df.columns.get_loc(f'Volume{self.symbol[:-4]}') + 1, "Change", change)
        df.rename(columns={f'Volume{self.symbol[:-4]}': "Volume"}, inplace=True)
        df.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        df.to_sql('asset_1m', self.connection, if_exists='append', index=False)
    def store_cryptoCandle(self, symbol_id):
        make_pattern = MakePattern()
        pattern = make_pattern.pattern(self.data)
        pattern.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        asset_id = pd.read_sql(f"SELECT id FROM asset_1m WHERE symbol_id = {symbol_id}", self.connection)['id'].tolist()
        pattern.insert(1, 'asset_id', asset_id)
        pattern.to_sql('cryptoCandle_1m', self.connection, if_exists='append', index=False)
        return asset_id
    def store_rsi(self, symbol_id, asset_id):
        rsi = Rsi()
        rsi_data = rsi.create_rsi(self.data)
        rsi_data = rsi_data["signal"]
        rsi_data = rsi_data.to_frame()
        rsi_data.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        rsi_data.insert(1, 'asset_id', asset_id)
        rsi_data.to_sql('rsi_1m', self.connection, if_exists='append', index=False)
    def store_movingAverage(self, symbol_id, asset_id):
        ma = MovingAverage()
        ma_data = ma.create_moving_average(self.data)
        ma_data = ma_data[['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden']]
        ma_data.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        ma_data.insert(1, 'asset_id', asset_id)
        ma_data.to_sql('movingAverage_1m', self.connection, if_exists='append', index=False)
    def store_macd(self, symbol_id, asset_id):
        macd = Macd()
        macd_data = macd.create_macd(self.data)
        macd_data = macd_data['new_signal']
        macd_data = macd_data.to_frame()
        macd_data = macd_data.rename(columns={'new_signal': 'signal'})
        macd_data.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        macd_data.insert(1, 'asset_id', asset_id)
        macd_data.to_sql('macd_1m', self.connection, if_exists='append', index=False)
    def store_bollingerBand(self, symbol_id, asset_id):
        bb = BollingerBand()
        bb_data = bb.create_bollinger_band(self.data)
        bb_data = bb_data['signal']
        bb_data = bb_data.to_frame()
        bb_data.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        bb_data.insert(1, 'asset_id', asset_id)
        bb_data.to_sql('bollingerBands_1m', self.connection, if_exists='append', index=False)
    def store_superTrend(self, symbol_id, asset_id):
        df = self.data.copy()
        df = df.iloc[:, 1:7]
        df.rename(columns={'VolumeBTC': 'volume'}, inplace=True)
        df.index = df.index.rename('datetime')
        df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)

        st = SuperTrend()
        st_data = st.create_super_trend(df)
        st_data = st_data['signal']
        st_data = st_data.to_frame()
        st_data.insert(0, 'symbol_id', np.ones(len(self.data), dtype=np.int16) * symbol_id)
        st_data.insert(1, 'asset_id', asset_id)
        st_data.to_sql('superTrend_1m', self.connection, if_exists='append', index=False)