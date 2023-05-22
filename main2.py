import time
import sqlite3
from database.db_dataframe import GetDbDataframe
from database.exchange_info import BinanceExchange
from datetime import datetime
from email_option.sending_mail import MailSender
from database.missing_data import MissingDataCollection
from discord_bot.discord_message import Messages

sender = MailSender()
sender.login()

from googlesheet.connection import Connection
ws = Connection().connect_worksheet("tracker2")

discord_messages = Messages()

def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    p_symbols = BinanceExchange()
    all_symbols_payers = p_symbols.get_specific_symbols()
    print(all_symbols_payers)
    print(len(all_symbols_payers))
    missing_data = MissingDataCollection(database="database/big_crypto.db")

    for index, symbol in enumerate(all_symbols_payers):
        print(index, symbol)

        missing_data.grab_missing_1m(symbol)
        missing_data.grab_missing_resample(symbol)

        connection = sqlite3.connect("database/big_crypto.db")
        db_frame = GetDbDataframe(connection)
        data = db_frame.get_minute_data(symbol, 1, 90)
        df = db_frame.get_all_indicators(symbol, 1, 90)
        df.index = data.index
        df = df.add_prefix("1m_")
        data['sum'] = df.sum(axis=1)
        times = [3, 5, 15, 30]
        total_sum_values = 0
        total_sum_values += data['sum']

        for time in times:
            temp_data = db_frame.get_minute_data(symbol, time, 90)
            temp_df = db_frame.get_all_indicators(symbol, time, 90)
            temp_df.index = temp_data.index
            temp_data = temp_data[~temp_data.index.duplicated(keep='first')]
            temp_df = temp_df[~temp_df.index.duplicated(keep='first')]
            temp_df = temp_df.add_prefix(f"{time}m_")
            df = pd.concat([df, temp_df], axis=1)
            temp_data['sum'] = temp_df.sum(axis=1)
            total_sum_values += temp_data['sum']
        total_sum_values.fillna(0, inplace=True)
        data['sum'] = total_sum_values

        total_sum = 800

        print("Last 5 sum:")
        print(data['sum'])
        if not (any(data['sum'][-5:] >= total_sum) or any(data['sum'][-5:] <= -total_sum)):
            continue

        buy_indices = data.index[data['sum'] >= total_sum]
        sell_indices = data.index[data['sum'] <= -total_sum]

        for i, index in enumerate(buy_indices):
            if df.index.get_loc(index) >= len(df) - 5:
                p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
                p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"

                # Email Sending
                print("The Bullish sound")
                subject = symbol + " Bullish"
                Body = f"Bullish signal for {symbol} symbol.\nTotal signal value: {data['sum'][index]}." \
                       f"\n{p}."
                sender.send_mail("zihad.bscincse@gmail.com", subject, Body)
                sender.send_mail("tradingaitalib@gmail.com", subject, Body)

                body = [str(datetime.now()), symbol, int(data['sum'][index]), p]
                ws.append_row(body)

                discord_messages.send_massage(Body)

                print(p)
            # plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='bottom', fontsize=8)
        for i, index in enumerate(sell_indices):
            if df.index.get_loc(index) >= len(df) - 5:
                p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
                p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"

                # Email Sending
                print("The Bearish sound")
                subject = symbol + " Bearish"
                Body = f"Bearish signal for {symbol} symbol.\nTotal signal value: {data['sum'][index]}." \
                       f"\n{p}."
                sender.send_mail("zihad.bscincse@gmail.com", subject, Body)
                sender.send_mail("tradingaitalib@gmail.com", subject, Body)

                body = [str(datetime.now()), symbol, int(data['sum'][index]), p]
                ws.append_row(body)

                discord_messages.send_massage(Body)

                print(p)


# while True:
#     time.sleep(3)
#     try:
#         main()
#     except:
#         main()
#         time.sleep(61)
#         print("Testing")
main()
