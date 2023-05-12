import talib
import pandas as pd
import matplotlib.pyplot as plt
from database.dataframe import GetDataframe


class BollingerBand:
    def __init__(self):
        pass

    def create_bollinger_band(self, data):
        prices = data['Close']

        # Calculate the Bollinger Bands using TA-Lib
        upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=9, nbdevup=2, nbdevdn=2, matype=0)

        # Initialize empty lists to store the signals
        buy_signals = []
        sell_signals = []

        # Iterate through the prices and generate the signals
        for i in range(len(prices)):
            if prices[i] < lowerband[i]:
                buy_signals.append(100)
                sell_signals.append(0)
            elif prices[i] > upperband[i]:
                buy_signals.append(0)
                sell_signals.append(-100)
            else:
                buy_signals.append(0)
                sell_signals.append(0)

        signal = [buy_signals[i] + sell_signals[i] for i in range(len(buy_signals))]
        data = pd.DataFrame({'prices': prices,
                             'upperband': upperband,
                             'middleband': middleband,
                             'lowerband': lowerband,
                             'buy_signals': buy_signals,
                             'sell_signals': sell_signals,
                             'signal': signal})
        return data

    def plot_bollinger_band(self, data, ax=None,  total_sum=100):
        # Create a figure and axis
        if ax is None:
            fig, ax = plt.subplots()

        # Plot the prices, Bollinger Bands, and signals
        ax.plot(data['prices'], label='Prices', linewidth=2.0)
        ax.plot(data['upperband'], label='Upper Band')
        ax.plot(data['middleband'], label='Middle Band')
        ax.plot(data['lowerband'], label='Lower Band')
        # ax.fill_between(range(len(prices)), upperband, lowerband, alpha=0.1)
        ax.scatter(data.index[data['buy_signals'] == total_sum], data['lowerband'][data['buy_signals'] == total_sum],
                    marker='^', s=20, color='green', label='Buy signal', zorder=3)
        ax.scatter(data.index[data['sell_signals'] == -total_sum], data['upperband'][data['sell_signals'] == -total_sum],
                    marker='v', s=20, color='red', label='Sell signal', zorder=3)

        # Add a legend and show the plot
        # ax.set_title('Bollinger Band')
        ax.legend()
        # plt.show()
        return ax


if __name__ == '__main__':
    # Load data
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    bb = BollingerBand()
    data = bb.create_bollinger_band(data)
    print(data[600:])
    ax = bb.plot_bollinger_band(data)
    plt.show()