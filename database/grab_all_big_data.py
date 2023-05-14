import sqlite3
import time
import pickle
import pandas as pd
import binance
from database.dataframe import GetDataframe
from database.future_dataframe import GetFutureDataframe
from exchange_info import BinanceExchange
from create_resample_data import Resample
from store_in_db import StoreData
from api_callling.api_calling import APICall
import warnings

warnings.filterwarnings("ignore")


class DataCollection:
    def __init__(self):
        self.total_years = 1
        self.months = 1 * self.total_years
        self.days = 1 * self.months
        self.hours = 24 * self.days
        self.minute = self.hours * 60
        print(f"We are grabbing '{self.minute}' candles")
        self.time_of_data = int(self.minute)

        self.StartTime = time.time()
        print("This Script Start " + time.ctime())

    def collect_data(self):
        ticker_info = pd.DataFrame(APICall.client.get_ticker())
        p_symbols = BinanceExchange()
        all_symbols_payers = p_symbols.get_specific_symbols()
        print("All symbols: ", len(all_symbols_payers))

        try:
            with open('symbol_data_already_collected.pkl', 'rb') as f:
                symbol_data_already_collected = pickle.load(f)
            print("symbol list loaded from file")
            print("Len of Symbol list: ", len(symbol_data_already_collected))
        except FileNotFoundError:
            print("symbol file not found, creating new list.")
            symbol_data_already_collected = []

        print(symbol_data_already_collected)
        print("Symbols downloaded:", len(symbol_data_already_collected))

        symbols_get_api_exceptions = []
        symbols_get_none_data = []

        for i, symbol in enumerate(all_symbols_payers):

            if symbol in symbol_data_already_collected:
                continue
            print(i, symbol)
            try:
                data = GetFutureDataframe().get_minute_data(symbol, 1, self.time_of_data)
            except binance.exceptions.BinanceAPIException as e:
                print(f"Binance API exception: {e}")
                symbols_get_api_exceptions.append(symbol)
                continue
            print(data)

            if data is None:
                print("Can not find any data for ", symbol)
                symbols_get_none_data.append(symbol)
                continue

            connection = sqlite3.connect("big_crypto.db")
            cur = connection.cursor()

            store_data = StoreData(data, connection, cur, symbol)

            print("Storing data in symbol table")
            symbol_id = store_data.store_symbol()

            print("Storing data in asset table")
            store_data.store_asset(symbol_id)

            print("Storing data in cryptoCandle table")
            asset_id = store_data.store_cryptoCandle(symbol_id)

            print("Storing data in rsi table")
            store_data.store_rsi(symbol_id, asset_id)

            print("Storing data in movingAverage table")
            store_data.store_movingAverage(symbol_id, asset_id)

            print("Storing data in macd table")
            store_data.store_macd(symbol_id, asset_id)

            print("Storing data in bollinger band table")
            store_data.store_bollingerBand(symbol_id, asset_id)

            print("Storing data in super trend table")
            store_data.store_superTrend(symbol_id, asset_id)

            print("Creating and storing resample data")
            resample = Resample(data)
            s_id = symbol_id
            resample.create_minute_data(s_id, symbol)

            EndTime = time.time()
            print("\nThis Script End " + time.ctime())
            totalRunningTime = EndTime - self.StartTime
            print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")

            symbol_data_already_collected.append(symbol)
            with open('symbol_data_already_collected.pkl', 'wb') as f:
                pickle.dump(symbol_data_already_collected, f)
            print("The current loop is fully complete.")

            connection.commit()
            cur.close()
        print("Symbols got API exception:", symbols_get_api_exceptions)
        print("Symbols got no data: ", symbols_get_none_data)

if __name__ == "__main__":
    data_collection = DataCollection()
    data_collection.collect_data()