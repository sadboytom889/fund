import backtest; 
import pandas as pd;

# 杠杠倍数;
leverage = 1;

# 手续费率;
fee_rate = 0.0004;

ohlc = pd.read_csv( "./example.csv", header = 0,
                                     index_col = 0,
                                     parse_dates = [ "Date" ] ).head( 8 );
index = pd.date_range(
    start = pd.to_datetime( "1993-02-01 00:00:00", utc = True,
                                                   errors = "raise",
                                                   format = "%Y-%m-%d %H:%M:%S" ),

    end = pd.to_datetime( "1993-02-08 00:00:00", utc = True,
                                                 errors = "raise",
                                                 format = "%Y-%m-%d %H:%M:%S" ) );

######################################################################################
# buy: 市价开仓做多( 余额占比 );
buy =   pd.Series( data = [  True, False, False, False,
                            False, False, False, False ], index = index );

# sell: 多单平仓( 总仓位占比 );
sell =  pd.Series( data = [ False, False,  True, False,
                            False, False, False, False ], index = index );

# short: 市价开仓做空( 余额占比 );
short = pd.Series( data = [ False, False, False,  True,
                            False, False, False, False ], index = index );

# cover: 空单平仓( 总仓位占比 );
cover = pd.Series( data = [ False, False, False, False,
                            False,  True, False, False ], index = index );

######################################################################################

pd.set_option( "display.float_format", lambda x: "%.6f" % x );

bt = backtest.Backtest( locals(), "Unknown" );

print( "\n>  bt.ohlc\n%s\n\n" % bt.ohlc );
print( "\n>  bt.signals\n%s\n\n" % bt.signals );
print( "\n>  bt.positions\n%s\n\n" % bt.positions );
print( "\n>  bt.trades\n%s\n\n" % bt.trades );

bt.summary();
