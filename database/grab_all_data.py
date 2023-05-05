"""
Get CSV Data : https://www.cryptodatadownload.com/data/binance/
"""

import sqlite3
import time
from database.dataframe import GetDataframe
import pickle
from exchange_info import BinanceExchange
import binance

total_years = 2
months = 12 * total_years
days = 30 * months
hours = 24 * days
minute = hours * 60
print(f"We are grabbing '{minute}' candles")
# print(input("Find Minutes:"))
time_of_data = int(minute)

# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

from get_symbol.find_symbols import FindSymbols
import pandas as pd
pd.set_option('mode.chained_assignment', None)
#
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
#
from api_callling.api_calling import APICall
ticker_info = pd.DataFrame(APICall.client.get_ticker())
# print(ticker_info)
# fs = FindSymbols()
p_symbols = BinanceExchange()
all_symbols_payers = p_symbols.get_specific_symbols()

print("All symbols: ", len(all_symbols_payers))

# TODO: Fine how many symbol are left to download

# print(all_symbols_payers)
# symbol_data_already_collected

try:
    with open('symbol_data_already_collected.pkl', 'rb') as f:
        symbol_data_already_collected = pickle.load(f)
    print("symbol list loaded from file")
    print("Len of Symbol list: ",len(symbol_data_already_collected) )
except FileNotFoundError:
    print("symbol file not found, creating new list.")
    symbol_data_already_collected = []

# print(input(":"))

print(symbol_data_already_collected)
print("Symbols downloaded:", len(symbol_data_already_collected))
# print(input(":"))

for symbol in all_symbols_payers:

    if symbol in symbol_data_already_collected:
        continue
    print(symbol)
    # symbol = 'BTCBUSD'
    try:
        data = GetDataframe().get_minute_data(symbol, 1, time_of_data)
    except binance.exceptions.BinanceAPIException as e:
        print(f"Binance API exception: {e}")
        continue
    print(data)

    # Time Counting
    EndTime = time.time()
    print("\nThis Script End " + time.ctime())
    totalRunningTime = EndTime - StartTime
    print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
    print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")

    # print(input("All Minutes Data :"))
    # connection = sqlite3.connect("big_data.db")
    connection = sqlite3.connect("p_data.db")
    cur = connection.cursor()

    for i in range(len(data)):

        if 'VolumeBUSD' not in data.columns:
            continue
        # print(single_data)
        open_position = data['Open'].iloc[i]
        high_position = data['High'].iloc[i]
        low_position = data['Low'].iloc[i]
        close_position = data['Close'].iloc[i]

        symbol_volume_position = data[f'Volume{symbol[:-4]}'].iloc[i]
        close_time = data['CloseTime'].iloc[i]
        VolumeBUSD = data['VolumeBUSD'].iloc[i]
        trades = data['Trades'].iloc[i]
        buy_quote_volume = data['BuyQuoteVolume'].iloc[i]

        change_position = data['Change'].iloc[i]
        symbol_position = data['symbol'].iloc[i]
        time_position = data.index[i]
        unix_time = time_position.timestamp()
        # print(f"{open_position}, {high_position}, {low_position}, {close_position}, {symbol_volume_position},{int(close_time)}, {VolumeBUSD}, {trades}, {buy_quote_volume}, {change_position}, {symbol_position}, {time_position}, {int(unix_time)}")
        # print(input("...:"))
        cur.execute(
            "INSERT INTO asset VALUES (:id, :symbol, :Open, :High, :Low,  :Close, :VolumeBTC, :Change , :CloseTime, :VolumeBUSD, :Trades, :BuyQuoteVolume, :Time )",
            {
                'id': None,
                'symbol': symbol,
                'Open': open_position,
                'High': high_position,
                'Low': low_position,
                'Close': close_position,
                'VolumeBTC': symbol_volume_position,
                'Change': change_position,
                'CloseTime': int(close_time),
                'VolumeBUSD': float(VolumeBUSD),
                'Trades': trades,
                'BuyQuoteVolume': buy_quote_volume,
                'Time': int(unix_time)
            })

    symbol_data_already_collected.append(symbol)
    with open('symbol_data_already_collected.pkl', 'wb') as f:
        pickle.dump(symbol_data_already_collected, f)
    print("The current loop is fully complete.")


    connection.commit()
    cur.close()



# print(input(":"))

# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")