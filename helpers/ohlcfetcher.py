import os;
import re;
import ssl;
import sys;
import time;
import argparse;
import urllib.request;
import urllib.parse;

import pandas as pd;

class Ohlcfetcher ( object ):
    ''' 通过 http 请求获取数据;
    '''
    def __init__ ( self, params = None ):
        ''' 定义各种配置, 参数 params: 命令行参数, 详见 self.__getargs;
        '''

        # 定义所支持的交易对列表;
        self.__symbols = [ "XBTUSD", "ETHUSD" ];

        # 定义采集的数据列名与数据类型映射字典;
        self.__colmap = { "Open": "float64",
                          "High": "float64",
                          "Low": "float64",
                          "Close": "float64",
                          "Volume": "int64" };

        # 定义最小交易周期: Timedelta 对象, 0 days 00:01:00(1分钟);
        self.__mintimedelta = pd.Timedelta( value = 1, unit = "T" );

        # 定义最大交易周期: Timedelta 对象, 7 days 00:00:00(1周);
        self.__maxtimedelta = pd.Timedelta( value = 1, unit = "W" );

        # 定义数据输出文件夹名称;
        self.__folder = "./kline";

        # 定义数据切片长度;
        self.__limit = 1000;

        # 定义输出进度条长度;
        self.__progresslen = 30;

        # 定义 http 请求等待超时时间, 单位: 秒;
        self.__timeout = 60;

        # 定义 http 请求失败重试次数, 单位: 次;
        self.__retrycount = 20;

        # 定义 http 两次请求之间睡眠时间, 单位: 秒;
        self.__sleeptime = 30;

        # 创建未经验证的上下文传递到 urllib 以解决错误:
        # SSL Certificate_Verify_Failed Error: 过时的 Python 默认证书或无效过期的根证书而发生的;
        self.__context = ssl._create_unverified_context();

        # 解析命令行参数并保存为 args;
        args = self.__getargs( params );

        # 定义数据存放内存地址;
        self.__data = self.__getemptydataframe( args.intervals );

        # 开始获取数据的主程序;
        self.__run( args.symbol, args.start, args.end, args.intervals );

    def getdata ( self, interval ):
        ''' 返回数据 self.__data;
        '''

        return self.__data;

    def __getemptydataframe ( self, intervals ):
        ''' 用 self.__colmap 各项 key 生成类型为各项 value 的空 Series;

            用各项值为空 Series 的字典 emptycol: { '...': Series([], dtype: ...),
                                                '...': Series([], dtype: ...),
                                                '...': Series([], dtype: ...) };

            用 intervals 时间周期(Timedelta 对象)作 key, emptycol 生成的 DataFrame 作 value 生成函数返回值:
            { Timedelta('...'): Empty DataFrame   Timedelta('...'): Empty DataFrame
                                Columns: [...]                      Columns: [...]
                                Index: []                           Index: [] };
        '''

        data = {};

        for interval in [ self.__mintimedelta, *intervals ]:

            emptycol = {};
            for col in self.__colmap:

                emptycol[ col ] = pd.Series( [], dtype = self.__colmap[ col ] );

            data[ interval ] = pd.DataFrame( emptycol );

        return data;

    def __checksymbol ( self, symbol ):
        ''' 检查交易对是否存在于 self.__symbols 中;
        '''
        if symbol not in self.__symbols:
            raise argparse.ArgumentTypeError(
                "\n请检查交易对是否存在于 {} 中".format( self.__symbols ) );

        return symbol;

    def __checktime ( self, time ):
        ''' 检查时间格式是否满足 YYYY-MM-DD HH:mm;
        '''

        # 通过正则判断时间格式;
        if re.compile( r"^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$" ).match( time ):
            try:
                # 将输入时间转化为 utc Timestamp 对象时间;
                utctime = pd.to_datetime( time, utc = True,
                                                errors = "raise",
                                                format = "%Y-%m-%d %H:%M:%S" );
                return utctime;

            except Exception as error:
                raise argparse.ArgumentTypeError(
                    "\n{}".format( error ) );

        else:
            raise argparse.ArgumentTypeError(
                "\n检查时间格式是否满足 YYYY-MM-DD HH:mm" );

    def __checkinterval ( self, interval ):
        ''' 检查周期是否满足要求;
        '''
        try:
            # 将时间周期字符串转化为 Timedelta 对象;
            interval = pd.Timedelta( value = int( interval ), unit = "T" );

            # 判断时间是否处在最小时间周期与最大时间周期之间;
            # 因将默认获取最小周期数据再根据小周期合成各 interval, 故 interval 无需包含最小周期;
            if self.__mintimedelta < interval <= self.__maxtimedelta:

                # 各基本时间周期 Timedelta 对象(1分钟, 1小时, 1天, 1周);
                minuteunit = pd.Timedelta( value = 1, unit = "T" );
                hourunit = pd.Timedelta( value = 1, unit = "H" );
                dayunit = pd.Timedelta( value = 1, unit = "D" );
                weekunit = pd.Timedelta( value = 1, unit = "W" );

                # 判断时间周期是否满足要求, 即能被基本时间周期整除;
                minutecond = ( minuteunit % interval ).total_seconds() == 0;
                hourcond = ( hourunit % interval ).total_seconds() == 0;
                daycond = ( dayunit % interval ).total_seconds() == 0;
                weekcond = ( weekunit % interval ).total_seconds() == 0;

                if minutecond or hourcond or daycond or weekcond:
                    return interval;

                else:
                    raise argparse.ArgumentTypeError(
                        "\n{}".format( "输入时间周期不能被单位时间周期整除" ) );
            else:
                raise argparse.ArgumentTypeError(
                    "\n{}".format( "输入时间周期超出最大最小时间周期" ) );

        except Exception as error:
            raise argparse.ArgumentTypeError(
                "\n{}".format( error ) );

    def __getargs ( self, params ):
        ''' 解析命令行参数;
        '''

        # prog: 程序名称;
        prog = "历史数据下载器";

        # usage: 描述程序用途的字符串;
        usage = "%(prog)s[提供历史数据]";

        # description: 在参数帮助文档之前显示的文本;
        description = "参数: \n" + \
                      "-symbol(-s): 交易对; \n" + \
                      "--start(-st): 开始时间, 格式: YYYY-MM-DD HH:mm \n" + \
                      "--end(-et): 结束时间, 格式: YYYY-MM-DD HH:mm \n" + \
                      "--intervals(-i): 周期;";

        # epilog: 在参数帮助文档之后显示的文本;
        epilog = "在当前目录保存数据文件";

        # formatter_class: 用于自定义帮助文档输出格式的类;
        formatter_class = argparse.RawTextHelpFormatter;

        parser = argparse.ArgumentParser( prog = prog,
                                          usage = usage,
                                          description = description,
                                          epilog = epilog,
                                          formatter_class = formatter_class );

        parser.add_argument( "-s", "--symbol", dest = "symbol",
                                               type = self.__checksymbol,
                                               required = True,
                                               help = "键入交易对形如 XBTUSD" );

        parser.add_argument( "-st", "--start", dest = "start",
                                               type = self.__checktime,
                                               required = True,
                                               help = "键入形如 YYYY-MM-DD HH:mm 代表开始时间" );

        parser.add_argument( "-et", "--end", dest = "end",
                                             type = self.__checktime,
                                             required = True,
                                             help = "键入形如 YYYY-MM-DD HH:mm 代表结束时间" );

        parser.add_argument( "-i", "--intervals", dest = "intervals",
                                                  nargs = "*",
                                                  type = self.__checkinterval,
                                                  default = [],
                                                  help = "键入单个或多个周期形如 30 60, 单位: 分钟(m)" );

        result = parser.parse_args( params if params else sys.argv[ 1: ] );

        return result;

    def __getsavepath ( self, symbol, interval, start, end ):
        ''' 生成文件路径并检查是否已存在
        '''
        # 若存放数据的文件夹不存在则创建文件夹;
        if not os.path.exists( self.__folder ):
            os.mkdir( self.__folder );

        # 文件名: 交易对-时间周期-开始时间-结束时间
        filename = "{}-{}-{}-{}.csv".format( symbol, interval, start, end );

        # 文件路径
        savePath = "{}/{}".format( self.__folder, filename );

        return [ os.path.exists( savePath ), savePath ];

    def __printprogress ( self, status, interval, idx, lastidx ):
        ''' 对长度大于 1 的任务:
            命令行输出进度条形如: [status] [interval] [idx/lastidx] [##...];
        '''

        # 若任务数量不大于 1 则不输出;
        if lastidx == 0:
            return;

        # 已完成数量;
        done = int( self.__progresslen * idx / lastidx );

        # 命令行输出;
        sys.stdout.write( "\r[{}] [{}] [{}/{}] [{}{}]{}".format(
            status, interval, idx, lastidx,
            "#" * done, "." * ( self.__progresslen - done ),
            "\n" if idx == lastidx else "" ) );

        # 刷新缓冲区;
        sys.stdout.flush();

    def __retryget ( self, request ):
        ''' 发送 http 请求, 若失败重试 self.__retrycount 次;
        '''
        sleeptime = self.__sleeptime;

        # 重试计数器;
        retrycount = 0;

        # 最后一次请求失败错误记录;
        reason = "";

        while retrycount < self.__retrycount:
            try:
                # 睡眠指定时间(秒);
                time.sleep( sleeptime );

                # 请求开始前重置错误原因;
                reason = "";

                # 发送 http 请求;
                response = urllib.request.urlopen( request,
                                                   context = self.__context,
                                                   timeout = self.__timeout );
                # 解码;
                jsonstr = response.read().decode( "utf-8" );

                # 请求结束后重置睡眠时间;
                sleeptime = self.__sleeptime;

                return jsonstr;

            except Exception as error:
                # 记录错误原因;
                reason = error;

                # 记录重试次数;
                retrycount = retrycount + 1;

                # 倍增睡眠时间;
                sleeptime = sleeptime * 2;

        else:
            raise Exception(
                "网络请求错误: {}, {}".format( request.get_full_url(), reason ) );

    def __bitmexfixrow ( self, row ):
        ''' bitmex 修复行数据;
        '''

        # 将表示结束时间的数据行 timestamp 字符串转化为 Timestamp 对象;
        closetime = pd.to_datetime( row[ "timestamp" ],
                                    format = "%Y-%m-%d %H:%M:%S",
                                    utc = True );

        # 开始时间 Timestamp;
        opentime = closetime - self.__mintimedelta;

        # 修复 bitmex 数据潜在错误;
        maxoc = max( row[ "open" ], row[ "close" ] );
        minoc = min( row[ "open" ], row[ "close" ] );
        high = maxoc if maxoc > row[ "high" ] else row[ "high" ];
        low = minoc if minoc < row[ "low" ] else row[ "low" ];

        return [ opentime, high, low ];

    def __bitmexgetdataframe ( self, jsonstr, start, end, expectedsize ):
        ''' 生成 dataframe 并检查数据时间与条数是否正确;
            bitmex 接口:
            1: 响应数据 json 字符串形如: [ { "symbol", "timestamp", "open", "high", "low", "close", "volume" } ];
               该方法将 bitmex 数据转化为标准 dataframe 形如:
                                             Open     High      Low    Close    Volume
               Date                                                                   
               YYYY-MM-DD HH:mm:ss+00:00      ...      ...      ...      ...       ...

            2: 响应数据中的 timestamp 是周期结束时间戳, 而其他常见系统使用周期开始时时间戳;

            3: 响应数据也许存在两种情况的错误: 1: 开盘价低于最低价, 2: 收盘价高于最高价;
               经对比发现其中开盘价与收盘价是正确的, 最低价与最高价是需要自行修复的;
        '''

        # 通过接口数据转化为的原始 dataframe;
        dataframe = pd.read_json( jsonstr,
                                  orient = "records",
                                  dtype = self.__colmap );

        # 需新增的列;
        newcol = "Date";

        # 需删除的列;
        delcol = [ "timestamp", "symbol" ];

        # 需更新的列;
        updatecol = [ newcol, "high", "low" ];

        # 更新需更新的列: 修复 bitmex 数据行;
        dataframe[ updatecol ] = dataframe.apply( self.__bitmexfixrow,
                                                  axis = 1,
                                                  result_type = "expand" );

        # 删除需删除的列;
        dataframe = dataframe.drop( labels = delcol,
                                    axis = 1 );

        # 设置索引, 并检查是否存在重复;
        dataframe = dataframe.set_index( newcol,
                                         verify_integrity = True );

        # 将列名首字母大写;
        dataframe.columns = [ colname.capitalize() for colname in list( dataframe ) ];

        # 列名按照 self.__colmap 排序;
        dataframe = dataframe.reindex( columns = list( self.__colmap.keys() ) );

        # 数据长度;
        datasize = dataframe.shape[ 0 ];

        # 数据开始时间 Timestamp;
        datastart = dataframe.index[ 0 ];

        # 数据结束时间 Timestamp;
        dataend = dataframe.index[ datasize - 1 ];

        # 验证数据条数;
        if datasize != expectedsize:
            raise Exception(
                "数据条数错误: 期待 {} 条, 实际 {} 条".format(
                    expectedsize, datasize ) );

        # 验证数据开始时间与结束时间;
        if datastart != start or dataend != end:
            raise Exception(
                "数据范围错误: 期待 {} -> {}, 实际 {} -> {}".format(
                    start.strftime( "%Y-%m-%d %H:%M:%S" ),
                    end.strftime( "%Y-%m-%d %H:%M:%S" ),
                    datastart.strftime( "%Y-%m-%d %H:%M:%S" ),
                    dataend.strftime( "%Y-%m-%d %H:%M:%S" ) ) );

        return dataframe;

    def __bitmexsendrequest ( self, symbol, start, end, expectedsize ):
        ''' 通过 bitmex 交易所 http 请求拉取数据;
        '''
        # 时间格式化, Timestamp -> string;
        startformat = start.strftime( "%Y-%m-%dT%H:%M:%S.%fZ" );

        # 请求所需参数
        params = urllib.parse.urlencode( { "symbol": symbol,
                                           "startTime": startformat,
                                           "count": expectedsize,
                                           "start": 1,
                                           "binSize": "1m",
                                           "columns": "timestamp, open, high, low, close, volume" } );

        # 发送请求
        request = urllib.request.Request(
            "https://www.bitmex.com/api/v1/trade/bucketed?%s" % params );

        # 请求响应 json 字符串
        jsonstr = self.__retryget( request );

        # 通过 json 字符串转化为的 dataframe
        dataframe = self.__bitmexgetdataframe( jsonstr,
                                               start,
                                               end,
                                               expectedsize );

        return dataframe;

    def __run ( self, symbol, start, end, intervals ):
        ''' 获取最小时间周期行情;
        '''

        # 将 Timestamp 对象格式化为时间字符串形如: YYYY-MM-DD HH:mm:ss;
        startformat = start.strftime( "%Y-%m-%d %H:%M:%S" );
        endformat = end.strftime( "%Y-%m-%d %H:%M:%S" );

        # 时间周期 Timedelta 格式化为 ISO-8601 持续时间字符串形如: P[n]Y[n]M[n]DT[n]H[n]M[n]S;
        # P: 开始标记; T: 时间和日期分割标记; [n]Y: n年; [n]M: n月; [n]D: n日; [n]H: n 小时; [n]M: n分钟; [n]S: n秒;
        intervalformat = self.__mintimedelta.isoformat();

        # exists: 文件是否已存在;
        # savePath: 文件存放路径;
        exists, savePath = self.__getsavepath( symbol,
                                               intervalformat,
                                               startformat,
                                               endformat );
        try:
            if exists:
                # 读文件将数据记录在 self.__data 中;
                self.__data[ self.__mintimedelta ] = pd.read_csv( savePath,
                                                                  header = 0,
                                                                  index_col = 0,
                                                                  dtype = self.__colmap,
                                                                  parse_dates = [ "Date" ] );
            else:
                # 从开始时间到结束时间且频率为最小周期 self.__mintimedelta 的 DatetimeIndex 列表;
                dates = pd.date_range( start = start,
                                       end = end,
                                       freq = self.__mintimedelta );

                # 对 DatetimeIndex 列表以 self.__limit 尺寸进行切片;
                #                        -------------------------------------------------------
                # 例 limit = 3 则切片形如: | 00:00 00:01 00:02 | 00:03 00:04 00:05 | 00:06 ... ...
                #                        ----|-------------------|-------------------|----------
                #                           保留                 保留                保留
                dates = dates[ : : self.__limit ];

                # 已切片的 DatetimeIndex 列表 dates 的索引长度;
                lastidx = len( dates ) - 1;

                # 余数: 对输入开始结束时间以 self.__limit 尺寸进行切片(除法)后的余数;
                remainder = int( ( ( end - start ) / self.__mintimedelta ) % self.__limit + 1 );

                for idx, start in enumerate( dates ):
                    # 输出进度条;
                    self.__printprogress( "下载中", self.__mintimedelta, idx, lastidx );

                    # 当前请求期待得到的数据条数;
                    expectedsize = remainder if idx == lastidx else self.__limit;

                    # 开始时间 Timestamp 对象;
                    starttemp = start;

                    # 结束时间 Timestamp 对象;
                    endtemp = starttemp + self.__mintimedelta * ( expectedsize - 1 );

                    # 通过 bitmex 交易所 api 获取数据;
                    dataframe = self.__bitmexsendrequest( symbol,
                                                          starttemp,
                                                          endtemp,
                                                          expectedsize );

                    # 追加写入文件, 仅在首次时写入文件头部;
                    dataframe.to_csv( savePath, mode = "a",
                                                header = not bool( idx ) );

                    # 将数据记录在 self.__data 中;
                    self.__data[ self.__mintimedelta ] = pd.concat(
                        [ self.__data[ self.__mintimedelta ], dataframe ],
                        verify_integrity = True );

            # 生成其他周期数据;
            self.__generatedata( symbol, intervals );

            print( "数据获取成功" );

        except Exception as error:

            # 换行跳过进度条输出错误;
            print( "\n数据获取失败 -> {}".format( error ) );

    def __generatedata( self, symbol, intervals ):
        ''' 生成其他周期行情
        '''

        # 最小周期数据;
        base = self.__data[ self.__mintimedelta ];

        # 最小周期数据长度;
        size = base.shape[ 0 ];

        for interval in intervals:
            # 原始数据开始时间以 freq = interval 周期向上获取新的 Timestamp 对象;
            # 意在舍去不能合成新周期的部分头部时间段;
            start = base.index[ 0 ].ceil( freq = interval );

            # 原始数据结束时间加上最小周期时间得到最后一项的结束时间(为获取真正结束时间, 以免损失数据),
            # 再以 freq = interval 周期向下获取新的 Timestamp 对象,
            # 再减去最小时间周期得到最后一个柱子的开始时间;
            # 舍去不能合成新周期的部分尾部时间段;
            end = ( base.index[ size - 1 ] + self.__mintimedelta ).floor(
                freq = interval ) - interval;

            # 跳过不够条件合成新项的周期
            if end < start:
                continue;

            # 时间格式化, Timestamp -> string;
            startformat = start.strftime( "%Y-%m-%d %H:%M:%S" );
            endformat = end.strftime( "%Y-%m-%d %H:%M:%S" );
            intervalformat = interval.isoformat();

            exists, savePath = self.__getsavepath( symbol,
                                                   intervalformat,
                                                   startformat,
                                                   endformat );
            if exists:
                # 读文件将数据记录在 self.__data 中;
                self.__data[ interval ] = pd.read_csv( savePath,
                                                       header = 0,
                                                       index_col = 0,
                                                       dtype = self.__colmap,
                                                       parse_dates = [ "Date" ] );
            else:
                # 从开始时间到结束时间且频率为当前周期 interval 的 DatetimeIndex 列表;
                dates = pd.date_range( start = start, end = end, freq = interval );

                # 列表 dates 的索引长度;
                lastidx = len( dates ) - 1;

                for idx in range( 0, lastidx + 1 ):
                    self.__printprogress( "生成中", interval, idx, lastidx );

                    # 从最小周期 base 中取周期为 interval 的 start 到 end 合成新项;
                    start = dates[ idx ];
                    end = dates[ idx ] + interval - self.__mintimedelta;
                    chunk = base[ start : end ];

                    # 合成新数据行字典;
                    rowdata = { "Open": chunk.loc[ start, "Open" ],
                                "Close": chunk.loc[ end, "Close" ],
                                "High": chunk.loc[ :, "High" ].max(),
                                "Low": chunk.loc[ :, "Low" ].min(),
                                "Volume": chunk.loc[ :, "Volume" ].sum() };

                    # 通过字典生成 dataFrame, 并设置开始时间作为索引;
                    dataframe = pd.DataFrame( rowdata,
                                              index = [ start ] );

                    # 列名排序;
                    dataframe = dataframe.reindex(
                        columns = list( self.__colmap.keys() ) );

                    # 索引更名;
                    dataframe = dataframe.rename_axis( "Date" );

                    # 写入文件;
                    dataframe.to_csv( savePath,
                                      mode = "a",
                                      header = not bool( idx ) );

                    # 写入内存;
                    self.__data[ interval ] = pd.concat( [ self.__data[ interval ], dataframe ],
                                                         verify_integrity = True );
