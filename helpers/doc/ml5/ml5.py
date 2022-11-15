import numpy as np;

import pandas as pd;

from matplotlib import pyplot as plt;

# 概率密度函数
def pdffun ( x, mu, sigma ):
	# f( x ) = k * eʰ⁽ˣ⁾; h( x ) = -( x - μ )² / 2σ²; k = 1 / ( σ * √( 2ℼ ) );
	# numpy.exp(): 返回 e 的幂次方
	pdf = np.exp( - ( ( x - mu ) ** 2 ) / ( 2 * sigma ** 2 ) ) / ( sigma * np.sqrt( 2 * np.pi ) );
	return pdf;

# 读取数据
dataframe = pd.read_csv( "data1.ml5.csv" );

# 数据大小
size = dataframe.shape[ 0 ];
# 100

# 转化为数组
data = np.array( dataframe ).reshape( 1, -1 )[ 0 ];

# 数据集的最大值 max
max = data.max();
# 2559

# 数据集的最小值 min
min = data.min();
# 2520

# 数据集的平均值 μ
mean = data.mean();
# 2540.05

# 数据集的标准差 σ
std = data.std();
# 5.6592844070606665

# μ - 3σ < rule < μ + 3σ
rule = ( mean - 3 * std > data ) | ( mean + 3 * std < data );
# [False False False False False False False False False False False False
#  False False False False False False False False False False False False
#  False False  True False False False False False False False False False
#  False False False False False False False False False False False False
#  False False False False False False False False False  True False False
#  False False False False False False False False False False False False
#  False False False False False False False False False False False False
#  False False False False False False False False False False False False
#  False False False False]

# 异常点索引
index = np.arange( size )[ rule ];
# [26 57]
print( "获得异常点", data[ index ] );

# 绘制
x = np.arange( min, max, 0.1 );
y = pdffun( x, mean, std );
plt.plot( x, y );
plt.hist( data, bins = 12, rwidth = 0.9, density = True );
plt.xlabel( "Data" );
plt.ylabel( "Probability" );
plt.show();

