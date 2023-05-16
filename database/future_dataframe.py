from database.dataframe import GetDataframe
import pandas as pd
from api_callling.api_calling import APICall
from datetime import timedelta
import datetime
import pytz

class GetFutureDataframe(GetDataframe):

    def get_month_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}M", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_week_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}w", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_day_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}d", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_hour_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}h", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_minute_data(self, symbol, interval, lookback):
        frames = []
        num_calls = lookback // 1440 + 1
        for i in range(num_calls):
            start_timestamp = int((pd.Timestamp.now() - pd.DateOffset(minutes=(i + 1) * 1440 * interval)).timestamp() * 1000)
            end_timestamp = int((pd.Timestamp.now() - pd.DateOffset(minutes=i * 1440 * interval)).timestamp() * 1000)
            klines = APICall.client.futures_klines(symbol=symbol, interval=f"{interval}m", limit=1440,
                                                startTime=start_timestamp, endTime=end_timestamp)

            if klines:
                frame = pd.DataFrame(klines)
                frames.append(frame)

        if frames:
            result_frame = pd.concat(frames, ignore_index=True)
            result_frame = self.frame_to_symbol(symbol, result_frame)
            result_frame = result_frame.sort_index()
            return result_frame[:lookback]
        else:
            return pd.DataFrame()

    def get_range_data(self, symbol, interval, start_time, end_time):
        utc = pytz.utc
        start_time_utc = start_time.astimezone(utc)
        end_time_utc = end_time.astimezone(utc)
        data = []
        num_calls = (end_time_utc - start_time_utc) // timedelta(minutes=500 * interval) + 1

        for i in range(num_calls):
            start_timestamp = int(start_time_utc.timestamp() * 1000)
            end_timestamp = int((start_time_utc + timedelta(minutes=500 * interval)).timestamp() * 1000)
            klines = APICall.client.futures_klines(symbol=symbol, interval=f"{interval}m", startTime=start_timestamp,
                                                   endTime=end_timestamp)
            if klines:
                data.extend(klines)

            start_time_utc += timedelta(minutes=500 * interval)

        if data:
            frame = pd.DataFrame(data)
            frame = self.frame_to_symbol(symbol, frame)
            return frame
        else:
            return pd.DataFrame()


if __name__ == "__main__":
    data_f = GetFutureDataframe()
    data = data_f.get_minute_data('BTCBUSD', 1, 1440)
    print(data)
    print(len(data))
    # print(data_f.get_minute_data('BTCBUSD', 3, 10))
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(minutes=5)
    end_time = current_time
    print(start_time)
    print(end_time)
    data = data_f.get_range_data('BTCBUSD', 1, start_time, end_time)
    print(data)
    print(len(data))