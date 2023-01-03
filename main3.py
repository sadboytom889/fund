import backtest; 
import pandas as pd;

# # 杠杠倍数;
# leverage = 125;

# # 手续费率;
# fee_rate = 0.0004;

# # 蜡烛图
# ohlc = pd.read_csv( "./example.csv", header = 0,
#                                      index_col = 0,
#                                      parse_dates = [ "Date" ] );
# # 信号日期 index
# index = pd.date_range(
#     start = pd.to_datetime( "1993-03-01 00:00:00", utc = True,
#                                                    errors = "raise",
#                                                    format = "%Y-%m-%d %H:%M:%S" ),

#     end = pd.to_datetime( "1993-03-30 00:00:00", utc = True,
#                                                  errors = "raise",
#                                                  format = "%Y-%m-%d %H:%M:%S" ) );

# # buy: 市价开仓做多信号
# buy = pd.Series( data = [ ( 16529.20 * 0.1000 ) / 125 / 14976.8306,
#                           ( 16540.80 * 0.2000 ) / 125 / 14976.8306,
#                           ( 16527.10 * 0.3000 ) / 125 / 14976.8306,
#                           ( 16523.10 * 0.3000 ) / 125 / 14976.8306,
#                           ( 16534.10 * 0.2000 ) / 125 / 14976.8306,
#                           ( 16547.40 * 0.4000 ) / 125 / 14976.8306,
#                           ( 16560.00 * 0.3000 ) / 125 / 14976.8306,
#                           ( 16547.60 * 0.1000 ) / 125 / 14976.8306,
#                           ( 16557.70 * 0.2000 ) / 125 / 14976.8306,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                           ( 16545.00 * 0.2000 ) / 125 / 14976.8306,
#                           ( 16570.00 * 0.3000 ) / 125 / 14976.8306,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0,
#                                                                  0 ], index = index );

# # sell: 多单平仓信号
# sell = pd.Series( data = [               0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                            0.2100 / 2.1000,
#                            0.1100 / 1.8900,
#                            0.3000 / 1.7800,
#                            0.2000 / 1.4800,
#                                          0,
#                                          0,
#                            0.2000 / 1.7800,
#                            0.3000 / 1.5800,
#                            0.4000 / 1.2800,
#                            0.2000 / 0.8800,
#                            0.5000 / 0.6800,
#                                          1,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0,
#                                          0 ], index = index );

# # short: 市价开仓做空信号
# short = pd.Series( data = [                                        0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                                                                    0,
#                             ( 16560.90 * 0.2000 ) / 125 / 14955.6993,
#                             ( 16554.80 * 0.1000 ) / 125 / 14955.6993,
#                             ( 16557.80 * 0.1500 ) / 125 / 14955.6993,
#                                                                    0,
#                             ( 16551.70 * 0.1000 ) / 125 / 14955.6993,
#                                                                    0,
#                                                                    0,
#                                                                    0 ], index = index );

# # cover: 空单平仓信号
# cover = pd.Series( data = [               0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                                           0,
#                             0.1120 / 0.4500,
#                                           0,
#                             0.2190 / 0.4380,
#                                           1,
#                                           0 ], index = index );

# pd.set_option( "display.float_format", lambda x: "%.8f" % x );

# bt = backtest.Backtest( locals(), "Unknown" );

# print( "\n>  bt.ohlc\n%s\n\n" % bt.ohlc );
# print( "\n>  bt.signals\n%s\n\n" % bt.signals );
# print( "\n>  bt.positions\n%s\n\n" % bt.positions );
# print( "\n>  bt.trades\n%s\n\n" % bt.trades );

# bt.summary();
# bt.plot()


ohlc = pd.read_csv( "./helpers/kline/XBTUSD-P1DT0H0M0S-2016-01-01 00:00:00-2022-03-30 00:00:00.csv",
                    header = 0,
                    index_col = 0,
                    parse_dates = [ "Date" ] );

bt = backtest.Backtest( locals(), "Unknown" );
bt.plot()
