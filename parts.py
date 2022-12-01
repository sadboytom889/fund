import re;
import numpy;
import pandas;
import mplfinance;
import matplotlib.ticker;
from matplotlib import pyplot as plt;
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter

def calculate_positions ( signals, output_fields ):

    if signals is None:
        return None;

    buy, sell, short, cover = output_fields;

    position = 0;

    positions_series = pandas.Series( data = 0.0,
                                      index = signals.index );

    for index, signal in signals.iterrows():

        if signal[ sell ] or signal[ cover ]:
            if position > 0 and signal[ sell ] and signal[ sell ] > 0:
                position = position - position * signal[ sell ];
                position = 0 if position < 0 else position;

            if position < 0 and signal[ cover ] and signal[ cover ] > 0:
                position = position - position * signal[ cover ];
                position = 0 if position > 0 else position;

        else:
            if signal[ buy ] and signal[ buy ] > 0:
                position = 1 if position + signal[ buy ] > 1 else \
                                position + signal[ buy ];

            if signal[ short ] and signal[ short ] > 0:
                position = -1 if position - signal[ short ] < -1 else \
                                 position - signal[ short ];

        positions_series[ index ] = position;

    return positions_series;

def calculate_entry_prices ( group, positions_field,
                                    trade_prices_field,
                                    diff_volumes_field ):
    entry_prices = 0;

    entry_prices_series = pandas.Series( data = 0.0,
                                         index = group[ positions_field ].index );

    for index, row in group.iterrows():

        position = row[ positions_field ];

        price = row[ trade_prices_field ];

        volume = row[ diff_volumes_field ];

        if position * volume > 0:

            if entry_prices == 0:
                entry_prices = price;

            else:
                last_volume = position - volume;

                total_size = last_volume / entry_prices + volume / price;

                entry_prices = position / total_size;

        entry_prices_series[ index ] = entry_prices;

    cond = ( group[ positions_field ] == 0 ) & \
           ( group[ diff_volumes_field ] == 0 );

    entry_prices_series = entry_prices_series.mask( cond, other = 0 );

    return entry_prices_series;

def calculate_liq_prices ( group, leverage,
                                  roas_field,
                                  fees_field,
                                  positions_field,
                                  directions_field,
                                  diff_volumes_field,
                                  entry_prices_field ):
    mmr = 0.004;

    roas = group[ roas_field ];

    fees = group[ fees_field ];

    positions = group[ positions_field ];

    directions = group[ directions_field ];

    diff_volumes = group[ diff_volumes_field ];

    entry_prices = group[ entry_prices_field ];

    roas = roas.cumsum();

    fees = fees.cumsum();

    positions = positions * directions;

    liq_price = ( entry_prices * \
        ( 1 + roas + fees - directions * positions * leverage ) ) / \
        ( ( mmr - directions ) * positions * leverage );

    liq_price = liq_price.mask(
        ( liq_price < 0 ) | ( positions == 0 ), other = 0 );

    return liq_price;

def calculate_equitys ( dataframe_dict, times_field,
                                        roas_field,
                                        fees_field ):
    ''' 计算资产占比:
        组内例:
        avbl  price  roi  buy    profit  pos  diff  roi*diff=roa   cumsumroa
         100  100.0  0.0   10     0*0=0  0.0   0.0  0.0*0.0=0.00        0.00
              110.0  0.1   20  10*0.1=1  0.1   0.1  0.1*0.1=0.01  100*0.01=1
              121.0  0.1   30  20*0.1=2  0.3   0.2  0.1*0.2=0.02  100*0.02=2
              133.1  0.1   10  30*0.1=3  0.6   0.3  0.1*0.3=0.03  100*0.03=3
              133.1  0.0    0  10*0.0=0  0.7   0.1  0.0*0.1=0.00  100*0.00=0

        组间例:
          avbl  profit  roas  last_eq=rate       (1+roas)*rate=eq      eqd
        100.00     0.0   0.0        1.0000     (1+0.0)*1.0=1.0000      0.0
        110.00    10.0   0.1        1.0000     (1+0.1)*1.0=1.1000      0.1
        121.00    11.0   0.1        1.1000     (1+0.1)*1.1=1.2100     0.11
        108.90   -12.1  -0.1        1.2100    (1-0.1)*1.21=1.0890   -0.121
         87.12  -21.78  -0.2        1.0890   (1-0.2)*1.089=0.8712  -0.2178
        130.68   43.56   0.5        0.8712  (1+0.5)*0.8712=1.3068   0.4356
    '''

    # test = [ 1.0000, 1.1000, 1.2100, 1.0890, 0.8712, 1.3068 ];
    # # test = [    0.0,    0.1,   0.11, -0.121,-0.2178, 0.4356 ];
    # # test = [ 100.00, 110.00, 121.00, 108.90,  87.12, 130.68 ];

    # test = pandas.Series( test );

    # print( "test1", test.expanding().max() )
    # print( "test2", test )
    # print( "test3", test.expanding().max() - test );
    # print( "test4", ( test.expanding().max() - test ).max() );
    # print( "test5", ( test.expanding().max() - test ) / test.expanding().max() );

    dataframe = pandas.DataFrame( dataframe_dict );

    grouped = dataframe.groupby( times_field, group_keys = False );

    args = [];

    rate = 1.0;

    for times, group in grouped:

        equitys = 1 + group[ roas_field ].cumsum();

        cumfees = group[ fees_field ].cumsum();

        equitys = equitys * rate;

        cumfees = cumfees * rate;

        # equitys = equitys + cumfees;

        rate = equitys.iloc[ -1 ];

        args.append( equitys );

    return pandas.concat( args );

def performance_summary ( ohlc, positions, diff_volumes, roas, equitys ):
    '''
          avbl  profit  roas      eq      eqd
        100.00     0.0   0.0  1.0000      0.0
        110.00    10.0   0.1  1.1000      0.1
        121.00    11.0   0.1  1.2100     0.11
        108.90   -12.1  -0.1  1.0890   -0.121
         87.12  -21.78  -0.2  0.8712  -0.2178
        130.68   43.56   0.5  1.3068   0.4356

        gain = 10.0 + 11.0
         10.0                                     0.1
         11.0     -12.1                          0.11      -0.121
        43.56    -21.78                        0.4356     -0.2178
      = 64.56  = -33.88                      = 0.6456   = -0.3388

        64.56 / 33.88                          0.6456 / 0.3388
      = 1.90554899646                        = 1.90554899646

        ( 64.56 / 3 ) / ( 33.88 / 2 )          ( 0.6456 / 3 ) / ( 0.3388 / 2 )
      = 1.27036599764                        = 1.27036599764
    '''

    # 历史数据周期频率;
    freq = ohlc.index.inferred_freq;

    # 资产占比;
    eq = equitys[ roas != 0 ];

    # 资产变化占比;
    eqd = eq.diff().fillna( value = ( 1 - eq ) );

    # 持仓长度;
    hold = len( positions[ positions != 0 ] );

    # 操作次数;
    ops = len( diff_volumes[ diff_volumes != 0 ] );

    # 增持次数;
    inc = len( diff_volumes[ diff_volumes * positions > 0 ] );

    # 减持次数;
    dec = len( diff_volumes[ diff_volumes * positions.shift() < 0 ] );

    # 增持操作占总操作次数百分比;
    inc_pct = ( inc / ops ) if ops else 0;

    # 减持操作占总操作次数百分比;
    dec_pct = ( dec / ops ) if ops else 0;

    # 减持操作中产生盈利的次数占总操作次数百分比;
    win_pct = ( sum( eqd > 0 ) / len( eqd ) ) if len( eqd ) else 0;

    # 分钟级别资产收益率;
    minutes = eqd.resample( "T" ).sum();

    # 盈利列;
    gain_series = eqd[ eqd > 0 ];

    # 亏损列;
    loss_series = eqd[ eqd < 0 ];

    # 盈亏列;
    total_series = eqd[ eqd != 0 ];

    # 盈利总额;
    gain = gain_series.sum();

    # 亏损总额;
    loss = loss_series.sum();

    # 盈亏总额;
    total = total_series.sum();

    # 盈利操作的平均值;
    avgain = gain_series.mean() if len( gain_series ) else 0;

    # 亏损操作的平均值;
    avloss = loss_series.mean() if len( loss_series ) else 0;

    # 每笔操作的盈亏平均值;
    average = total_series.mean() if len( total_series ) else 0;

    # 最大回撤: 资产从高点到低点的最大回撤, 反映投资出现最糟糕的状况;
    maxdd = ( ( eq.expanding().max() - eq ) / eq.expanding().max() ).max();

    # 平均盈亏比: 平均盈利与平均亏损之比, 反映承担一定风险的获利;
    # 盈亏比为 2 代表每盈利 2 元将亏损 1 元, 冒亏损 1 元钱的风险获利 2 元;
    payoff = abs( avgain / avloss ) if avloss else 0;

    # 获利因子: 总盈利与总亏损之比, 反映承担单位亏损可得的获利;
    # 获利因子为 2 代表平均盈利 2 元则将亏损 1 元;
    pf = abs( gain / loss ) if loss else 0;

    # 回收系数: 总盈亏除以最大回撤, 该系数越大代表投资收益发生回撤后恢复的越快;
    # 该系数一般大于 1

    # Recovery Factor 在出现亏损情况下，恢复因子越大，加仓数越大，盈利空间越大，同时风险越大
    rf = eqd.sum() / maxdd;

    # 夏普比率: 承受一单位的总风险产生的报酬, 较高的夏普比率代表承担相同单位风险获取更高收益;
    # 分子平均值 μ 代表收益, 均值越大代表收益越高, 夏普比例越高;
    # 分母标准差 σ 代表风险, 标准差越趋近 0 则样本离散程度越小, 夏普比例越高;
    # 年交易转化数平方根: ( a / √(a) ) = √(a);
    sharpe = ( minutes.mean() / minutes.std() ) * \
             ( ( 60 * 24 * 365 ) ** 0.5 );

    # 索提诺比率: 承受一单位的下行风险产生的报酬, 运用下偏而非总标准差以区别不利的波动,
    #           较高的该比率代表相同单位下行风险获取更高收益;
    sortino = ( minutes.mean() / minutes[ minutes < 0 ].std() ) * \
              ( ( 60 * 24 * 365 ) ** 0.5 );

    # 溃疡指数: 根据价格下跌深度和持续时间衡量下行风险的度量值, 较高的溃疡指数代表较高的回撤风险;
    ulcer = ( ( ( ( ( eq - eq.expanding().max() ) * 100 ) ** 2 ).sum() / \
                      len( eq ) ) ) ** 0.5;

    # 溃疡表现指数: 较高的马丁比率值代表更高的回报但承担更小的风险;
    upi = eqd.mean() / ulcer;

    return ( {
        # 开始时间 = 历史数据起始时间;
        "开始时间(%s)" % freq: str( ohlc.index[ 0 ] ),

        # 结束时间 = 历史数据结束时间;
        "结束时间(%s)" % freq: str( ohlc.index[ -1 ] ),

        # 回测长度 = 历史数据总长度;
        "回测长度(%s)" % freq: len( ohlc ),

        # 持仓长度 = 持仓周期总长度;
        "持仓长度(F)": hold,

        # 操作次数 = 导致仓位变化的操作的次数;
        "操作次数(F)": ops,

        # 买入次数 = 导致仓位增加的操作的次数;
        "买入次数(F)": inc,

        # 卖出次数 = 导致仓位减少的操作的次数;
        "卖出次数(F)": dec,

        # 亏损次数 = 卖出产生亏损的次数;
        "亏损次数(F)": sum( eqd < 0 ),

        # 盈利次数 = 卖出产生盈利的次数;
        "盈利次数(F)": sum( eqd > 0 ),

        # 持仓长度占比 = 持仓周期总长度 / 历史数据总长度;
        "持仓长度(%)": float( ( hold / len( ohlc ) ) * 100 ),

        # 买入次数占比 = 导致仓位增加的操作的次数 / 总操作次数;
        "买入次数(%)": float( inc_pct * 100 ),

        # 卖出次数占比 = 导致仓位减少的操作的次数 / 总操作次数;
        "卖出次数(%)": float( dec_pct * 100 ) ,

        # 交易胜率 = 卖出次数中产生盈利的次数 / 卖出次数;
        "交易胜率(%)": float( win_pct * 100 )
    }, {
        # 盈利总额 = ∑( 盈利 + 盈利 + ... );
        "盈利总额(%)": float( gain * 100 ),

        # 亏损总额 = ∑( 亏损 + 亏损 + ... );
        "亏损总额(%)": float( loss * 100 ),

        # 盈亏总额 = ∑( 盈亏 + 盈亏 + ... );
        "盈亏总额(%)": float( total * 100 ),

        # 平均盈利 = 盈利总额 / 盈利次数;
        "平均盈利(%)": float( avgain * 100 ),

        # 平均亏损 = 亏损总额 / 亏损次数;
        "平均亏损(%)": float( avloss * 100 ),

        # 平均盈亏 = 盈亏总额 / 交易次数;
        "平均盈亏(%)": float( average * 100 )
    }, {
        # 最大回撤 = ( ( eq.expanding.max - eq ) / eq.expanding.max ).max;
        "最大回撤(%)": float( maxdd * 100 ),

        # 盈亏比 = 平均盈利 / 平均亏损;
        "盈亏比率": float( payoff ),

        # 获利因子 = 总盈利 / 总亏损;
        "获利因子": float( pf ),

        # 回收系数 = 总盈亏 / 最大回撤;
        "回收系数": float( rf ),

        # 夏普比率 = ( ( 周期报酬率平均值 - 无风险利率 ) / 周期报酬率标准差 ) * 年交易转化数平方根;
        "夏普比率": float( sharpe ),

        # 索提诺比率 = ( 周期报酬率平均值 – 无风险利率 ) / 周期亏损率标准差 * 年交易转化数平方根;
        "索提比率": float( sortino ),

        # 溃疡指数 = √( ∑( 百分比回撤² ) / 周期数 );
        "溃疡指数": float( ulcer ),

        # 溃疡表现指数 = 报酬率平均值 / 溃疡指数
        "马丁比率": float( upi )
    } );

class MultiCursor ():
    ''' 绘制十字光标;
    '''

    def __init__ ( self, canvas, axes ):
        """ 显示多个竖排子图的十字星光标, 所有子图显示垂直线仅一个子图显示水平线,
            保持对它的引用以确保光标响应事件处理;
        """

        self.canvas = canvas;

        self.axes = axes;

        self.needclear = False;

        self.background = None;

        self.lines = self.create();

        self.canvas.mpl_connect( "motion_notify_event", self.onmove );

        self.canvas.mpl_connect( "draw_event", self.clear );

    def create ( self ):
        ''' 创建水平垂直线;
        '''

        xmids = [];

        ymids = [];

        for ax in self.axes:

            xmin, xmax = ax.get_xlim();

            ymin, ymax = ax.get_ylim();

            xmid = 0.5 * ( xmin + xmax );

            ymid = 0.5 * ( ymin + ymax );

            xmids.append( xmid );

            ymids.append( ymid );

        xmid = min( xmids );

        ymid = min( ymids );

        cursor_color = ( 132, 142, 156 );

        args = { "linewidth": 0.4,
                 "linestyle": "--",
                 "visible": False,
                 "animated": True,
                 "color": make_color_tuple( cursor_color ) };

        return [ [ ax.axhline( ymid, **args ) for ax in self.axes ],
                 [ ax.axvline( xmid, **args ) for ax in self.axes ] ];

    def clear ( self, event ):
        ''' 绘制事件: 清理上一帧, 刷新图像;
        '''

        # 保存初始静态图像信息
        self.background = self.canvas.copy_from_bbox(
            self.canvas.figure.bbox );

        # 隐藏十字光标
        for line in self.lines[ 0 ] + self.lines[ 1 ]:
            line.set_visible( False );

    def onmove ( self, event ):
        ''' 鼠标移动事件: 设置各坐标轴十字光标;
        '''

        if event.inaxes is None:
            return;

        if not self.canvas.widgetlock.available( self ):
            return;

        self.needclear = True;

        # 设置鼠标所在坐标轴十字光标垂直线;
        for line in self.lines[ 1 ]:

            line.set_xdata( ( event.xdata, event.xdata ) );

            line.set_visible( True );
 
        for i in range( len( self.axes ) ):

            if event.inaxes == self.axes[ i ]:

                # 设置鼠标所在坐标轴十字光标水平线;
                line = self.lines[ 0 ][ i ];

                line.set_ydata( ( event.ydata, event.ydata ) );

                line.set_visible( True );

            else:
                # 其余坐标轴的光标水平线隐藏;
                self.lines[ 0 ][ i ].set_visible(False)

        # 鼠标移动时先恢复事先保存的静态信息;
        if self.background is not None:

            self.canvas.restore_region( self.background );

        for lines in self.lines:

            for line in lines:

                if line.get_visible():

                    # 绘制更新后的动态对象;
                    line.axes.draw_artist( line );
 
        # 绘制更新后的内容;
        self.canvas.blit();

def make_color_tuple ( rgb_tuple ):
    return tuple( [ x / 256 for x in list( rgb_tuple ) ] );

def make_color_str ( rgb_tuple ):
    return str( tuple( [ x / 256 for x in list( rgb_tuple ) ] ) );

def make_mpf_style ():

    down_color_ohlc = ( 246, 71, 93 );

    down_color_volume = ( ( 135, 49, 63 ) );

    up_color_ohlc = ( 13, 203, 129 );

    up_color_volume = ( 32, 115, 80 );

    edge_color = ( 43, 49, 58 );

    grid_color = ( 33, 37, 44 );

    tick_color = ( 95, 102, 115 );

    fig_color = face_color = ( 22, 26, 30 );

    color_volume = { "up": make_color_tuple( up_color_volume ),
                     "down": make_color_tuple( down_color_volume ) };

    color_dict = { "up": make_color_tuple( up_color_ohlc ),
                   "down": make_color_tuple( down_color_ohlc ),
                   "volume": color_volume,
                   "edge": "inherit",
                   "wick": "inherit",
                   "ohlc": "inherit",
                   "alpha": 1.0 };

    color = mplfinance.make_marketcolors( **color_dict );

    style_rc = { "axes.linewidth": 0.8,
                 "axes.labelweight": 100,
                 "axes.unicode_minus": False,
                 "xtick.color": make_color_str( tick_color ),
                 "ytick.color": make_color_str( tick_color ),
                 "font.weight": 100,
                 "font.size": 6,
                 "font.sans-serif": "SimHei",
                 "grid.linewidth": 0.4 };

    style_dict = { "marketcolors": color,
                   "gridstyle": "-",
                   "gridaxis": "both",
                   "gridcolor": make_color_str( grid_color ),
                   "edgecolor": make_color_str( edge_color ),
                   "figcolor": make_color_str( fig_color ),
                   "facecolor": make_color_str( fig_color ),
                   "y_on_right": True,
                   "rc": style_rc };

    style = mplfinance.make_mpf_style( **style_dict );

    return style;

def plot ( ohlc ):

    l = t = 0.045;

    r = b = 0.065;

    h = 1 - t - b;

    w = 1 - l - r;

    style = make_mpf_style();

    fig = mplfinance.figure( style = style );

    h_o = ( 1 - t - b ) * 0.90;

    h_v = ( 1 - t - b ) * 0.10;

    h_e = ( 1 - t - b ) * 0.10;

    ax_o = fig.add_axes( [ l, 1 - ( t + h_o ), w, h_o ] );

    ax_o.axes.set_xticks( ohlc.index );

    ax_o.axes.ticklabel_format( axis = "y",
                                style = "plain",
                                useOffset = False );

    ax_v = fig.add_axes( [ l, b, w, h_v ], sharex = ax_o );

    ax_v.axes.yaxis.tick_right();

    ax_e = fig.add_axes( [ l, b, w, h_e ], sharex = ax_o );

    ax_e.axes.yaxis.tick_right();

    # ax.plot(le.index, le.values, '^', color='lime', markersize=12,
    #                label='long enter')

    # add_plot = [ mplfinance.make_addplot( ohlc[ "Close" ] ) ];

    


    mplfinance.plot( data = ohlc,
                     style = style,
                     type = "candle",
                     xrotation = 0,
                     ax = ax_o,
                     volume = ax_v,
                     volume_exponent = 0,
                     # add_plot = add_plot,
                     ylabel = "",
                     ylabel_lower = "",
                     show_nontrading = True,
                     datetime_format = "%y-%m-%d\n%H:%M",
                     warn_too_much_data = 60 * 24 * 365 * 6,
                     scale_width_adjustment = dict( candle = 1.2,
                                                    volume = 0.80 ) );

    multiCursor = MultiCursor( fig.canvas, [ ax_o.axes, ax_v.axes ] );

    mplfinance.show();
