import numpy as np;
import pandas as pd;
from matplotlib import pyplot as plt;

UNCLASSIFIED = False

NOISE = 0;

# # np.transpose( a, axes = None );
# # 不传参则默认将维度反序
# # 即将原数组的各个 axis 进行反转, 例: ( 0, 1, 2 ) -> ( 2, 1, 0 )
#
# # 传参则指定反转规则
# x = np.arange( 12 ).reshape( ( 2, -1 ) );
# # [ [ 0  1  2  3  4  5 ]
# #   [ 6  7  8  9 10 11 ] ]
#
# x = np.arange( 12 ).reshape( ( 3, -1 ) );
# # [ [ 0  1  2  3 ]
# #   [ 4  5  6  7 ]
# #   [ 8  9 10 11 ] ]
#
# x = np.arange( 24 ).reshape( ( 2, 3, 4 ) );
# # x.shape = ( 2, 3, 4 );
# # [ [ [  0  1  2  3 ], [  4  5  6  7 ], [  8  9 10 11 ] ]
# #   [ [ 12 13 14 15 ], [ 16 17 18 19 ], [ 20 21 22 23 ] ] ];
# # 第一层 [] 为 0 ( x ) 轴
# # 第二层 [] 为 1 ( y ) 轴
# # 第三层 [] 为 2 ( z ) 轴
#
# x = x.transpose( 1, 2, 0 ); # 原 0 轴转化为 2 轴
# 							# 原 1 轴转化为 0 轴
# 							# 原 2 轴转化为 1 轴
# # ( 2, 3, 4 ) -> ( 3(原1轴), 4(原2轴), 2(原0轴) )
# # x.shape = ( 3, 4, 2 )
# # [ [ [ 0 12 ], [ 1 13 ], [  2 14 ], [  3 15 ] ]
# #   [ [ 4 16 ], [ 5 17 ], [  6 18 ], [  7 19 ] ]
# #   [ [ 8 20 ], [ 9 21 ], [ 10 22 ], [ 11 23 ] ] ];

# np.array( [ [ 1 ],
# 			  [ 2 ],
# 			  [ 3 ],
# 			  [ 4 ],
# 			  [ 5 ] ] ) == 1;
# 
# # >>> [ [  True ]
# #       [ False ]
# #       [ False ]
# #       [ False ]
# #       [ False ] ]

# nonzero( a ): 返回数组 a 中非零元素的索引值数组
# np.nonzero( [ 0, 0 ] );
# # >>> ( array( [] ), )
# 
# np.nonzero( [ 0, 2, 3 ] );
# # >>> ( array( [ 1, 2 ] ), )
# 
# np.nonzero( np.array( [ [ 0, 0, 3 ],
# 						  [ 0, 0, 0 ],
# 						  [ 0, 0, 9 ] ] ) );
# # >>> ( array( [ 0, 2 ] ), array( [ 2, 2 ] ) );
# 1): 第 1 个 array 从 row 值上对 3 和 9 进行描述
# 2): 第 2 个 array 从 col 值上对 3 和 9 进行描述

# np.nonzero( np.array( [ [ 0, 0, 3 ],
# 						  [ 0, 1, 0 ],
# 						  [ 0, 0, 9 ] ] ) )
# # >>> ( array( [ 0, 1, 2 ] ), array( [ 2, 1, 2 ] ) );
# 1): 第 1 个 array 从 row 值上对 3, 1, 9 进行描述
# 2): 第 2 个 array 从 col 值上对 3, 1, 9 进行描述

# np.nonzero( np.array( [ [ 0, 0, 3, 2 ],
# 						  [ 0, 1, 0, 1 ],
# 						  [ 0, 0, 9, 0 ] ] ) )
# # >>> ( array( [ 0, 0, 1, 1, 2 ] ), array( [ 2, 3, 1, 3, 2 ] ) );

# np.nonzero( np.array( [ [ [ 0, 0 ], [ 1, 0 ] ],
# 						  [ [ 0, 0 ], [ 1, 0 ] ],
# 						  [ [ 0, 0 ], [ 1, 0 ] ] ] ) );
# # >>> ( array( [ 0, 1, 2 ] ), array( [ 1, 1, 1 ] ), array( [ 0, 0, 0 ] ) );

# np.nonzero( np.array( [ [ True ],
# 						  [ True ],
# 						  [ True ],
# 						  [ False ] ] ) );
# # >>> (array( [ 0, 1, 2 ] ), array( [ 0, 0, 0 ] ) );

def search ( data, index, radius ):
	""" params: data: 数据集
				index: 当前数据点索引
				radius: 半径
		return: 当前数据点 radius 范围内的数据点 index[]
	"""
	seeds = [];

	for i in range( data.shape[ 1 ] ):
		diff = data[ :, index ] - data[ :, i ];

		if np.sqrt( np.power( diff, 2 ).sum() ) < radius:
			seeds.append( i );

	return seeds;

def loop ( data, result, index, clusterid, radius, minsize ):
	""" params: data: 数据集
				result: 分类结果
				index: 当前数据点索引
				clusterid: 簇 id
				radius: 半径
				minsize: 最小点个数
		return: 能否成功分类
	"""

	# 获取当前数据点半径内的种子数据点索引列表
	seeds = search( data, index, radius );

	# 种子数据数量小于 minsize 则进行下轮循环
	if len( seeds ) < minsize:
		# 半径外的数据点设为 NOISE
		result[ index ] = NOISE;
		return False;

	else:
		# 半径内的数据点设为当前簇类 id: clusterid
		result[ index ] = clusterid;
		for seedId in seeds:
			result[ seedId ] = clusterid;

		# 遍历当前数据点半径内的种子数据点索引
		while len( seeds ) > 0:
			# 根据种子数据点找到新的种子数据点索引
			newseeds = search( data, seeds[ 0 ], radius );

			if len( newseeds ) >= minsize:

				for i in range( len( newseeds ) ):
					# 若种子数据未分类则分类并添加入遍历数据
					if result[ newseeds[ i ] ] == UNCLASSIFIED:
						result[ newseeds[ i ] ] = clusterid;
						seeds.append( newseeds[ i ] );

					# 若种子数据分类为 NOISE 则分类
					if result[ newseeds[ i ] ] == NOISE:
						result[ newseeds[ i ] ] = clusterid;

			seeds = seeds[ 1: ];

		return True;

def dbscan ( data, radius, minsize ):
	""" params: data: 数据集
				radius: 半径
				minsize: 最小点个数
		return: 簇 id
	"""
	# 簇 id
	clusterid = 1;

	# 数据长度
	size = data.shape[ 1 ];

	# 数据种类
	result = [ UNCLASSIFIED ] * size;

	# index: 数据索引
	for index in range( size ):

		if result[ index ] == UNCLASSIFIED:

			if loop( data, result, index, clusterid, radius, minsize ):
				clusterid = clusterid + 1;

	return result, clusterid - 1;

def show ( data, clusters, clusternumber ):
	matclusters = np.mat( clusters ).transpose();
	# [ [ 1 ],
	#   [ 1 ],
	#   ...  ,
	#   [ 2 ],
	#   [ 2 ],
	#   ... ]

	colours = [ "black", "blue", "green", "cyan", "red",
				"purple", "orange", "brown" ];

	for i in range( clusternumber + 1 ):
		mask = np.nonzero( matclusters[ :, 0 ].A == i )[ 0 ];
		# [x, x, ... , x]

		subcluster = data[ :, mask ];
		# [ [ x, x, ... , x ]
		#   [ y, y, ... , y ] ]

		marker = "x" if i == 0 else None;

		size = 10 if i == 0 else 2;

		plt.scatter( subcluster[ 0, : ].flatten().A[ 0 ],
					 subcluster[ 1, : ].flatten().A[ 0 ],
					 c = colours[ i ],
					 marker = marker,
					 s = size );

# 表格
dataframe = pd.read_csv( "./data1.ml3.csv", header = 0 );
#          x      y
# 0    15.55  28.65
# 1    14.90  27.55
# 2    14.45  28.35
# 3    14.15  28.80
# 4    13.75  28.05
# ..     ...    ...
# 783   7.80   3.35
# 784   8.05   2.75
# 785   8.50   3.25
# 786   8.10   3.55
# 787   8.15   4.00
# [788 rows x 2 columns]

data = np.array( dataframe );
# [ [ 15.55 28.65 ]
#   [ 14.9  27.55 ]
#   [ 14.45 28.35 ]
#   ...
#   [  8.5   3.25 ]
#   [  8.1   3.55 ]
#   [  8.15  4.   ] ]

data = data.transpose();
# [ [ 15.55 14.9  14.45 ...  8.5   8.1   8.15 ]
#   [ 28.65 27.55 28.35 ...  3.25  3.55  4.   ] ]

data = np.mat( data );
# [ [ 15.55 14.9  14.45 ...  8.5   8.1   8.15 ]
#   [ 28.65 27.55 28.35 ...  3.25  3.55  4.   ] ]

clusters, clusternumber = dbscan( data, 2, 15 );

print( "共分为 {} 类".format( clusternumber ) );

print( "clusters", clusters )

show( data, clusters, clusternumber );

plt.show();
