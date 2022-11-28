import backtest; 
import pandas as pd;

# 杠杠倍数;
leverage = 25;

# 手续费率;
fee_rate = 0.0004;

ohlc = pd.read_csv( "./example.csv", header = 0,
                                     index_col = 0,
                                     parse_dates = [ "Date" ] );

index = pd.date_range(
    start = pd.to_datetime( "1993-02-01 00:00:00", utc = True,
                                                   errors = "raise",
                                                   format = "%Y-%m-%d %H:%M:%S" ),

    end = pd.to_datetime( "1993-03-06 00:00:00", utc = True,
                                                 errors = "raise",
                                                 format = "%Y-%m-%d %H:%M:%S" ) );

######################################################################################
# buy: 市价开仓做多( 余额占比 );
buy =   pd.Series( data = [ 0.01303308928, 0.00781288457, 0.01041900560, 0.01302187712,
                            0.01562230480, 0.00521318200, 0.00781131353,           0.0,
                                      0.0, 0.00522472985, 0.01042013353,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                            0.00796390626,           0.0,           0.0,           0.0,
                            0.00264123454, 0.00264244304,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0 ], index = index );

# sell: 多单平仓( 总仓位占比 );
sell =  pd.Series( data = [           0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0, 0.020 / 0.280,
                            0.040 / 0.260,           0.0,           0.0, 0.030 / 0.280,
                            0.020 / 0.250, 0.030 / 0.230, 0.050 / 0.200, 0.060 / 0.150,
                                      0.0, 0.040 / 0.120, 0.040 / 0.080, 0.020 / 0.040,
                                      0.0,           0.0,           1.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0 ], index = index );

# short: 市价开仓做空( 余额占比 );
short = pd.Series( data = [           0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0,           0.0,
                                      0.0,           0.0,           0.0, 0.01601491700,
                            0.01865928906, 0.02100149481,           0.0, 0.01314905141,
                                      0.0,           0.0, 0.01312052172, 0.01574534521,
                                      0.0,           0.0 ], index = index );

# cover: 空单平仓( 总仓位占比 );
cover = pd.Series( data = [           0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0,           0.0, 0.0,
                                      0.0,           0.0, 0.040 / 0.210, 0.0,
                            0.030 / 0.220, 0.030 / 0.190,           0.0, 0.0,
                            0.270 / 0.270,           0.0 ], index = index );
######################################################################################

pd.set_option( "display.float_format", lambda x: "%.8f" % x );

bt = backtest.Backtest( locals(), "Unknown" );

print( "\n>  bt.ohlc\n%s\n\n" % bt.ohlc );
print( "\n>  bt.signals\n%s\n\n" % bt.signals );
print( "\n>  bt.positions\n%s\n\n" % bt.positions );
print( "\n>  bt.trades\n%s\n\n" % bt.trades );

bt.summary();
bt.plot()


# ohlc = pd.read_csv( "./example.csv", header = 0,
#                                      index_col = 0,
#                                      parse_dates = [ "Date" ] );

# bt = backtest.Backtest( locals(), "Unknown" );
# bt.plot()
