class ResampleData:
    def __init__(self, symbol="BTCBUSD"):
        self.symbol = symbol
        self.aggregation = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            f'Volume{self.symbol[:-4]}': "sum",
            "Change": "last",
            "CloseTime": "last",
            "VolumeBUSD": "sum",
            "Trades": "sum",
            "BuyQuoteVolume": "sum",
            "symbol": "first",
            "Time": "first"
        }

    def resample_to_minute(self, df, minute):
        time = minute
        return df.resample(f"{time}T").agg(self.aggregation)[-len(df)//minute:]

    def resample_to_hours(self, df, hour):
        time = hour * 60
        return df.resample(f"{time}T").agg(self.aggregation)

    def resample_to_day(self, df, day):
        time = day * 24 * 60
        return df.resample(f"{time}T").agg(self.aggregation)


if __name__ == "__main__":
    from dataframe import GetDataframe
    from database.future_dataframe import GetFutureDataframe
    symbol = "SOLBUSD"
    data = GetDataframe().get_minute_data(symbol, 1, 60)
    data = data.rename_axis('Time_index')
    data['Time'] = data.index
    print(data)
    rd = ResampleData(symbol)
    new_data = rd.resample_to_minute(data, 30)
    print(new_data)
    data = GetDataframe().get_minute_data(symbol, 30, 2)
    data = data.rename_axis('Time_index')
    data['Time'] = data.index
    print(data)
