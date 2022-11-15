import pandas as pd;
import mplfinance as mpf;
from ohlcfetcher import Ohlcfetcher;

# ohlcfetcher = Ohlcfetcher(
#     params = [ "-s", "XBTUSD",
#                "-st", "2016-01-01 00:00",
#                "-et", "2022-03-30 23:59",
#                "-i", "5", "10", "15", "20", "30",
#                      "60", "120", "180", "240", "360", "480", "720",
#                      "1440", "10080" ] );
# 
# 
# dataframe = ohlcfetcher.getdata( pd.Timedelta( value = 1, unit = "W" ) );

dataframe = pd.read_csv( "./../example.csv", header = 0,
                                             index_col = 0,
                                             parse_dates = [ "Date" ] );


dataframe = dataframe.head( 20 );

mpf.plot( data = dataframe,
          type = "candle",
          title = "candlestick",
          style = "binance",
          ylabel = "price($)",
          ylabel_lower = "volume(shares)",
          figratio = ( 12, 6 ),
          volume = True,
          show_nontrading = True );
