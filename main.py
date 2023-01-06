import time;
import pandas;

import backtest; 

# 杠杠倍数;
leverage = 125;

# 手续费率;
fee_rate = 0.0004;

class Strategy ( object ):

    def __init__ ( self ):
        self.ohlc = pandas.DataFrame(
            columns = [ "High", "Low", "Open", "Close", "Volume" ] );

    def run ( self, sleep = 0 ):
        data = pandas.read_csv( "./example.csv", header = 0,
                                                 index_col = 0,
                                                 parse_dates = [ "Date" ] );

        for index, row in data.iterrows():

            row = row.to_dict();

            index = { "Date": index.timestamp() };

            params = { **row, **index };

            self.add_row( params );

            print( self.ohlc );

            sleep and time.sleep( sleep )

    def add_row ( self, rowdata ):
        ''' 向 self.ohlc 添加新行;
        '''
        df_row = pandas.DataFrame( [ rowdata ] );

        df_row.set_index( "Date", drop = True,
                                  append = False,
                                  verify_integrity = True,
                                  inplace = True );

        self.ohlc = pandas.concat( [ df_row, self.ohlc ] );


strategy = Strategy();

strategy.run()


