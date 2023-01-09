import pandas;

import backtest; 

# 杠杠倍数;
leverage = 125;

# 手续费率;
fee_rate = 0.0004;

class Strategy ( object ):

    def __init__ ( self ):

        self.__ohlc_columns = [ "High", "Low", "Open", "Close", "Volume" ];

        self.__data_keys = [ "Date", *self.__ohlc_columns ];

        self.ohlc = pandas.DataFrame( columns = self.__ohlc_columns );

    def add_rows ( self, data ):
        ''' 向 self.ohlc 添加新行;
        '''

        if all( [ key in data.keys() for key in self.__data_keys  ] ):

            data[ "Date" ] = pandas.to_datetime( data[ "Date" ],
                                                 unit = "s",
                                                 utc = True,
                                                 errors = "raise" );

            df_row = pandas.DataFrame( [ data ] );

            df_row.set_index( "Date", drop = True,
                                      append = False,
                                      verify_integrity = True,
                                      inplace = True );

            self.ohlc = pandas.concat( [ df_row, self.ohlc ] );

    def add_data ( self, data ):
        ''' 向 self.ohlc 添加数据;
        '''

        if isinstance( data, dict ):

            self.add_rows( data );

        if isinstance( data, list ):

            for item in data:
                self.add_rows( item );

    def run ( self ):

        print( "self.ohlc", self.ohlc )


strategy = Strategy();

def add_list( data ):

    list = [];

    for index, row in data.iterrows():

        row = row.to_dict();

        index = { "Date": index.timestamp() };

        params = { **row, **index };

        list.append( params );

    strategy.add_data( list );


def add_item( data ):

    for index, row in data.iterrows():

        row = row.to_dict();

        index = { "Date": index.timestamp() };

        params = { **row, **index };

        strategy.add_data( params );

data = pandas.read_csv( "./test.csv", header = 0,
                                      index_col = 0,
                                      parse_dates = [ "Date" ] );

# add_item( data );
add_list( data );
strategy.run();
