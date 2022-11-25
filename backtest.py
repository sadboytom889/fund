import parts;
import pandas;
from functools import cached_property;

class Backtest ( object ):
    ''' 单向持仓回测;
    '''

    __ohlc_field = "ohlc";

    __leverage_field = "leverage";

    __fee_rate_field = "fee_rate";

    __signal_fields = ( "buy", "sell", "short", "cover" );

    __ohlc_need_include_fields = ( "Open", "High", "Low", "Close", "Volume" );

    __signal_output_fields = ( "Buy", "Sell", "Short", "Cover" );

    def __init__ ( self, store, name = "Unknown" ):
        ''' store: 回测数据来源;
            name: 回测名称;
        '''

        self.name = name;

        self.__store = dict( [ ( k.lower(), v ) for k, v in store.items() ] );

    def __repr__ ( self ):
        return "Backtest( %s )" % ( self.name );

    @property
    def store ( self ):
        return self.__store;

    @cached_property
    def leverage ( self ):
        ''' 杠杆倍数
        '''

        leverage = self.__store.get( self.__leverage_field );

        if isinstance( leverage, int ) and leverage > 0:
            return leverage;

        return 1;

    @cached_property
    def fee_rate ( self ):
        ''' 手续费率
        '''

        fee_rate = self.__store.get( self.__fee_rate_field );

        if isinstance( fee_rate, float ) and 0 < fee_rate < 1:
            return fee_rate;

        return 0;

    @cached_property
    def ohlc ( self ):
        ''' 行情历史数据: 在 store 中以键名 self.__ohlc_field 来查找并返回
                         格式为 DataFrame 且索引为 DatetimeIndex 的 dataframe;
                         若不存在或列名不在 self.__ohlc_need_include_fields 中返回 None;
        '''

        ohlc = self.__store.get( self.__ohlc_field );

        if isinstance( ohlc, pandas.DataFrame ) and \
           isinstance( ohlc.index, pandas.DatetimeIndex ) and \
           ohlc.index.inferred_freq is not None and \
           not bool( [ False for column_fields in self.__ohlc_need_include_fields \
                       if column_fields not in ohlc.columns.values ] ):

            return ohlc;

        return None;

    @cached_property
    def signals ( self ):
        ''' 输入信号数据: 在 store 中以键名 self.__signal_fields 来查找并返回
                         格式为 Series 且索引为 DatetimeIndex 的各信号列合并且与
                         历史数据索引对应的 dataframe, 不符预期的数据填充为 0,
                         若历史数据 ohlc 不存在则返回 None;

            各列数据含义: buy, short 列代表在当次交易初始余额的交易量百分占比;
                         sell, cover 列代表当前持仓的交易量百分占比;
        '''

        if self.ohlc is None:
            return None;

        signals_dict = {};

        for store_key, output_key in zip( self.__signal_fields,
                                          self.__signal_output_fields ):

            series = self.__store.get( store_key );

            signals_dict[ output_key ] = \
                series if isinstance( series, pandas.Series ) and \
                          isinstance( series.index, pandas.DatetimeIndex ) \
                       else pandas.Series( data = 0.0, index = self.ohlc.index );

        return pandas.DataFrame( signals_dict ).reindex(
            self.ohlc.index ).fillna( value = 0 );

    @cached_property
    def positions ( self ):
        ''' 持仓数据总览: 返回使用信号数据 signals 生成的持仓数据 series,
                         因信号根据市价即收盘价而计算得到, 故当前时间周期并未持仓,
                         而实际持仓发生在产生信号的下个周期, 且以开盘价作为交易价格;
        '''

        if self.signals is None:
            return None;

        return parts.calculate_positions(
            self.signals, self.__signal_output_fields ).shift().fillna( value = 0 );

    @cached_property
    def trade_prices ( self ):
        ''' 交易价格数据;
        '''

        if self.ohlc is None:
            return None;

        trade_prices = self.ohlc[ "Open" ];

        trade_prices.name = "Trade Prices";

        return trade_prices;

    @cached_property
    def diff_volumes ( self ):
        ''' 交易金额占比变化数据: 指占本次交易初始资金中的比例( 开仓量占比, 补仓量占比,
                                                            平仓量占比, 减仓量占比 );

            例多头寸平仓:    已持多头头寸 position: 3/100;
                                                * 已持有 3/100 初始资金的多头头寸;

                                信号输入平仓 sell: 1/3;
                                                * 平掉已持有仓位的 1/3;
                                                * 平仓后持有的多头寸占比为 2/3;

                         持仓位变化量 diff_volume: 3/100 * 1/3 = 1/100;
                                                * 平仓量在初始资金的占比为 1/100,
                                                * 平仓后持有的多头寸在初始资金占比为 2/100;
        '''

        if self.positions is None:
            return None;

        return self.positions.diff().fillna( value = 0 );

    @cached_property
    def directions ( self ):
        ''' 持仓方向数据;
        '''

        if self.positions is None:
            return None;

        return self.positions.apply( lambda x: 0 if x == 0 else -1 if x < 0 else 1 );

    @cached_property
    def change_points ( self ):
        ''' 持仓方向改变数据;
        '''

        return self.directions != self.directions.shift();

    @cached_property
    def start_points ( self ):
        ''' 开始持仓数据: 当前时间周期存在持仓方向改变且当前时间周期存在仓位,
                        返回是否为交易购入即开始持仓的时间周期;
        '''

        if self.positions is None:
            return None;

        return self.change_points & self.positions;

    @cached_property
    def end_points ( self ):
        ''' 结束持仓数据: 当前时间周期存在持仓方向改变且前一时间周期存在仓位,
                        返回是否为交易出售即结束持仓的时间周期;
        '''

        if self.positions is None:
            return None;

        return self.change_points & self.positions.shift();

    @cached_property
    def times ( self ):
        ''' 交易次数统计;
        '''

        if self.positions is None:
            return None;

        return self.start_points.cumsum();

    @cached_property
    def entry_prices ( self ):
        ''' 开仓均价数据;

            开仓均价: entry_price

                     last_size * entry_price + now_size * trade_prices
                  =  -------------------------------------------------
                                    last_size + now_size

                     avbl * last_volume                  avbl * now_volume
                    -------------------- * entry_price + ------------------ * trade_prices
                         entry_price                        trade_prices
                  = ----------------------------------------------------------------------;
                                  avbl * last_volume   avbl * now_volume
                                  ------------------ + -----------------
                                      entry_price         trade_prices

                     last_volume + now_volume
                  = --------------------------;
                    last_volume    now_volume
                    ----------- + ------------
                    entry_price   trade_prices
        '''

        if self.positions is None:
            return None;

        dataframe_dict = { "t": self.times,
                           "o": self.positions,
                           "p": self.trade_prices,
                           "v": self.diff_volumes };

        args = list( dataframe_dict.keys() )[ 1 : ];

        dataframe = pandas.DataFrame( dataframe_dict );

        groups = dataframe.groupby( "t", group_keys = False );

        if len( groups ) > 1:
            return groups.apply( parts.calculate_entry_prices, *args );

        else:
            return parts.calculate_entry_prices( dataframe, *args );

    @cached_property
    def fees ( self ):
        ''' 手续费占比数据;

            1: 计算依据当笔交易金额占比数据 diff_volume;


                             avbl * diff_volume (交易金额占比)
            交易数量: size = --------------------------------- * leverage;
                                  entry_price (交易价格)

            手续费占比: fees

                      size * trade_price * fee_rate (手续费)
                    = -------------------------------------
                                 avbl (可用余额)

                      diff_volume
                    = ----------- * leverage * trade_price * fee_rate
                      entry_price

                    *平仓与减仓: trade_price = trade_price;

                    *开仓与补仓: trade_price = entry_price;
            '''

        if self.positions is None:
            return None;

        directions = self.directions.mask(
            self.end_points, other = self.directions.shift() );

        rate_dataframe_dict = { "d": directions,
                                "p": self.trade_prices,
                                "e": self.entry_prices,
                                "v": self.diff_volumes };

        rate_series = pandas.DataFrame( rate_dataframe_dict ).apply(
            lambda x: x[ "d" ] * -1 \
                   if x[ "d" ] * x[ "v" ] > 0 \
                   else 0 if x[ "e" ] == 0 else x[ "d" ] * x[ "p" ] / x[ "e" ],
            axis = 1 );

        return self.diff_volumes * self.leverage * self.fee_rate * rate_series;

    @cached_property
    def liq_prices ( self ):
        ''' 强平价格数据;
                             avbl * position
            持仓数量: size = ------------------ * lever;
                               entry_price

            对于名义价格 size * entry_price < 50000 的头寸: 维持保证金率: mmr = 0.004;
                                                         维持保证金速算额: cumb = 0;

            强平价格: liquidation_price

                    avbl - avbl * fee + avbl * roa + cumb - direction * size * entry_price
                  = ----------------------------------------------------------------------;
                                      size * mmr - direction * size

                    entry_price * ( 1 - fee + roa - direction * position * lever )
                  = --------------------------------------------------------------;
                            ( mmr - direction ) * ( position * lever )
        '''

        if self.positions is None:
            return None;

        dataframe_dict = { "t": self.times,
                           "r": self.roas,
                           "f": self.fees,
                           "p": self.positions,
                           "d": self.directions,
                           "v": self.diff_volumes,
                           "e": self.entry_prices };

        args = [ self.leverage, *list( dataframe_dict.keys() )[ 1 : ] ]

        dataframe = pandas.DataFrame( dataframe_dict );

        groups = dataframe.groupby( "t", group_keys = False );


        if len( groups ) > 1:
            return groups.apply( parts.calculate_liq_prices, *args );

        else:
            return parts.calculate_liq_prices( dataframe, *args );

    @cached_property
    def liqs ( self ):
        ''' 已被强平数据;
        '''

        return ( ( self.directions > 0 ) & ( self.ohlc[ "Low" ] < self.liq_prices ) ) | \
               ( ( self.directions < 0 ) & ( self.ohlc[ "High" ] > self.liq_prices ) );

    @cached_property
    def rois ( self ):
        ''' 投资回報率 ROI: 反映获利能力或效率;

            1: 计算依据当笔交易金额占比数据 diff_volume;
            2: 仅保留减仓或平仓周期的数据;
            3: 未计算手续费;

            ROI = ( trade_prices - entry_prices ) / entry_prices
                = ( trade_prices / entry_prices ) - 1;

        '''

        if self.positions is None:
            return None;

        directions = self.directions.mask(
            self.end_points, other = self.directions.shift() );

        rois = ( self.trade_prices / self.entry_prices ) - 1;

        rois = rois * self.leverage * directions * ( self.diff_volumes * directions < 0 );

        rois = rois.fillna( value = 0 );

        return rois;

    @cached_property
    def roas ( self ):
        ''' 资产回报率 ROA: 反映每单位资产创造利润的指标;

            1: 计算依据当笔交易;
            2: 仅保留减仓或平仓周期的数据;
            3: 未计算手续费;

                  avbl + avbl * diff_volume * roi - avbl
            ROA = --------------------------------------;
                                 avbl

                  avbl * ( 1 + diff_volume * roi - 1 )
                = ------------------------------------;
                                avbl

                = diff_volume * roi;
        '''

        if self.positions is None:
            return None;

        directions = self.directions.mask(
            self.end_points, other = self.directions.shift() );

        return self.rois * self.diff_volumes * directions * -1;

    @cached_property
    def equitys ( self ):
        ''' 资产占比数据: 反映资产的变化(已计算手续费)
            1: 按照交易次数为交易分组;

            2: 组内使用资产回报率 ROA 累加计算资产;
               组内使用手续费 fee 累加计算总手续费;

            3: 组内计算真实资产占比;
        '''

        if self.positions is None:
            return None;

        dataframe_dict = { "t": self.times,
                           "r": self.roas,
                           "f": self.fees };

        args = list( dataframe_dict.keys() );

        return parts.calculate_equitys( dataframe_dict, *args );

    @cached_property
    def trades ( self ):
        ''' 数据总览;
        '''

        if self.positions is None:
            return None;

        trades = pandas.DataFrame( dtype = float,
                                   index = self.positions.index );

        trades[ "times" ] = self.times;
        trades[ "dir" ] = self.directions;
        trades[ "trade_prices" ] = self.trade_prices;
        trades[ "entry_prices" ] = self.entry_prices;
        trades[ "liq_prices" ] = self.liq_prices
        trades[ "diff_vols" ] = self.diff_volumes;
        trades[ "pos" ] = self.positions;
        trades[ "rois" ] = self.rois;
        trades[ "roas" ] = self.roas;
        trades[ "equitys" ] = self.equitys;
        trades[ "fees" ] = self.fees;
        trades[ "liqs" ] = self.liqs;

        return trades;

    @cached_property
    def report ( self ):
        ''' 各种可供分析的指标;
        '''
        if self.positions is None:
            return None;

        return parts.performance_summary( self.ohlc,
                                          self.positions,
                                          self.diff_volumes,
                                          self.roas,
                                          self.equitys );

    def summary ( self ):
        ''' 打印报告;
        '''
        if self.report is None:
            return None;

        print( self );

        for dic in iter( self.report ):

            print( "-" * 48 );

            for key, value in dic.items():

                if isinstance( value, str ):
                    print( "| %-10s%30s |" % ( key, value ) );

                if isinstance( value, int ):
                    print( "| %-10s%30d |" % ( key, value ) );

                if isinstance( value, float ):
                    print( "| %-10s%30.6f |" % ( key, value ) );

            print( "-" * 48 );

    def plot ( self ):
        ''' 图像比例:
                -----------------------------
                |             ↑             |
                |           0.045           |
                |             ↓             |
                |         ---------         |
                |         |       |         |
                |← 0.045 →|       |← 0.065 →|
                |         |       |         |
                |         ---------         |
                |             ↑             |
                |           0.065           |
                |             ↓             |
                -----------------------------

            matplotlib 汉字与负数乱码不显示的问题;
                需设置 plt.rcParams[ "font.sans-serif" ] = [ "SimHei" ];
                      plt.rcParams[ "axes.unicode_minus" ] = False;

            macos 不存在 SimHei 的问题;
                1: 查看 matplotlib 字体文件路径:
                    matplotlib.matplotlib_fname(),

                2: 官网下载字体文件:
                    https://www.fontpalace.com/font-download/simhei;

                3: 将字体文件放置于字体文件路径下:
                    matplotlib/mpl-data/fonts/ttf/;

                4: 查看 matplotlib 字体缓存路径:
                    matplotlib.get_cachedir(), 并将其删除: rm -rf ...;

                5: 修改 matplotlibrc 文件:
                   1): 字库族为 sans-serif:
                       删注释: # font.family: sans-serif ->
                                font.family: sans-serif;

                   2): 添加 SimHei 即宋体到字库族列表中:
                       删注释, 并添加 SimHei: # font.sans-serif: ... ->
                                              font.sans-serif: SimHei, ...;

                   3): 解决负号 - 显示为方块
                       删注释, 并改为 False: # axes.unicode_minus: True ->
                                             axes.unicode_minus: False;
        '''

        parts.plot( self.ohlc );

    def plot_equitys ( self ):
        ''' 打印资产占比数据 equitys 图表;
        '''

        fig, ax_o = plt.subplots( 1, 1 );

        ax_v = ax_o.twinx();

        self.equitys.plot( color = "r", style = "-", ax = ax_o );
        # self.ohlc.Close.plot( color = "g", style = "-", ax = ax_v );
        # mpf.plot(self.ohlc, type='line')

        mpf.plot( self.ohlc, type='candle', volume=True, show_nontrading = True)

        # mpf.plot( data = self.ohlc,
        #           type = "candle",
        #           title = "candlestick",
        #           style = "binance",
        #           ylabel = "price($)",
        #           ylabel_lower = "volume(shares)",
        #           figratio = ( 12, 6 ),
        #           volume = True,
        #           show_nontrading = True );

        #plt.plot( self.equitys );

        #plt.plot( self.ohlc.Close );


        # (price[ix] - price[ix][0]).resample('W').first().dropna() \
        #     .plot(color='black', alpha=0.5, label='underlying', ax=ax)



        plt.title( str( self ) );

        plt.tick_params( labelsize = 6 );

        plt.show();

    def plot_trades ( self, subset = None ):
        '''
        '''

        if subset is None:
            subset = slice( None, None );

        fr = self.trades.ix[subset]
        le = fr.price[(fr.pos > 0) & (fr.vol > 0)]
        se = fr.price[(fr.pos < 0) & (fr.vol < 0)]
        lx = fr.price[(fr.pos.shift() > 0) & (fr.vol < 0)]
        sx = fr.price[(fr.pos.shift() < 0) & (fr.vol > 0)]

        import matplotlib.pylab as pylab
        _ = None
        if ax is None:
            _,ax = pylab.subplots()

        ax.plot(le.index, le.values, '^', color='lime', markersize=12,
                   label='long enter')
        ax.plot(se.index, se.values, 'v', color='red', markersize=12,
                   label='short enter')
        ax.plot(lx.index, lx.values, 'o', color='lime', markersize=7,
                   label='long exit')
        ax.plot(sx.index, sx.values, 'o', color='red', markersize=7,
                   label='short exit')
        
        self.ohlc.O.ix[subset].plot(color='black', label='price', ax=ax)
        ax.set_ylabel('Trades for %s' % subset)
        return _,ax
