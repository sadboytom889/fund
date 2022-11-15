import numpy as np;
import pandas as pd;

from matplotlib import pyplot as plt;

# np.linalg.norm( x, ord = None, axis = None, keepdims = False ): 计算范数
# x: 矩阵, 也可以是一维为向量;
# ord = 1: 列和范数;
# ord = 2: 二范数;
# ord = np.inf: 行和范数;
# axis = 1 按行向量处理;
# axis = 0 按列向量处理;

# numpy.average( a, axis = None, weights = None, returned = False );
# a: 包含要平均的数据的数组;
# axis: 0: 按行方向平均, 1: 按列方向平均;
# weights: 与 a 中的值相关联的权重数组;
#
# 例:
# a = np.array( [ [  0,  1,  2,  3,  4 ],
# 				  [  5,  6,  7,  8,  9 ],
# 				  [ 10, 11, 12, 13, 14 ],
# 				  [ 15, 16, 17, 18, 19 ] ],

# 				[ [ 20, 21, 22, 23, 24 ],
# 				  [ 25, 26, 27, 28, 29 ],
# 				  [ 30, 31, 32, 33, 34 ],
# 				  [ 35, 36, 37, 38, 39 ] ],

# 				[ [ 40, 41, 42, 43, 44 ],
# 				  [ 45, 46, 47, 48, 49 ],
# 				  [ 50, 51, 52, 53, 54 ],
# 				  [ 55, 56, 57, 58, 59 ] ] ] );

# np.average( a, axis = 0 );
# # [ [ 20. 21. 22. 23. 24. ]
# #   [ 25. 26. 27. 28. 29. ]
# #   [ 30. 31. 32. 33. 34. ]
# #   [ 35. 36. 37. 38. 39. ] ]

# np.average( a, axis = 1 );
# # [ [  7.5  8.5  9.5 10.5 11.5 ]
# #   [ 27.5 28.5 29.5 30.5 31.5 ]
# #   [ 47.5 48.5 49.5 50.5 51.5 ] ]

# np.average( a );
# # 29.5

# np.where( condition[, x, y ] ): 满足输出 x, 不满足输出 y
#
# np.where( np.arange( 10 ), 1, -1 );
# # >>> [ -1  1  1  1  1  1  1  1  1  1 ]
# # 0 为 False, 所以 0 位置输出 -1, 其他为 1
# 
# np.where( np.arange( 10 ) > 5, 1, -1 );
# # >>> [ -1, -1, -1, -1, -1, -1,  1,  1,  1,  1 ]
# 
# np.where( [ [ 10 > 5, 10 < 5 ], [ 10 == 10, 10 == 7 ] ],
# 		  [ [ "chosen", "not chosen" ], [ "chosen", "not chosen" ] ],
# 		  [ [ "not chosen", "chosen" ], [ "not chosen", "chosen" ] ] );
# 
# # [ [ 10 > 5 ? "chosen" : "not chosen", 10 < 5 ? "not chosen" : "chosen" ],
# #   [ 10 == 10 ? "chosen" : "not chosen", 10 == 7 ? "not chosen" : "chosen" ] ]
# 
# # >>> [ [ "chosen" "chosen" ]
# #       [ "chosen" "chosen" ] ]
# 
# np.where( [ [ True, False ], [ True, True ] ],
# 			[ [ 1, 2 ], [ 3, 4 ] ],
# 			[ [ 9, 8 ], [ 7, 6 ] ] );
# # >>> [ [ 1 8 ]
# #       [ 3 4 ] ]
# 
# # np.where( condition ): 输出满足条件元素的索引/坐标
#
# np.where( np.array( [ 2, 4, 6, 8, 10 ] ) > 5 );
# #				索引: [ 0, 1, 2, 3, 4 ]
# # >>> ( array( [ 2, 3, 4 ] ), );
# 
# np.where( [ [ 0, 1 ], [ 1, 0 ] ] );
# #	索引:  [ [ [ 0, 0 ] = 0, [ 0, 1 ] = 1 ],
# #			[ [ 1, 0 ] = 1, [ 1, 1 ] = 0 ] ]
# # >>> ( array( [ 0, 1 ] ), array( [ 1, 0 ] ) );

# np.where( np.array( [ 2, 0 ] ) == 2 );
# # >>> ( array( [ 0 ] ), )

# 主函数
def meanshift ( data, radius ):

	clusters = [];


	# 将每个数据点都作为初始中心点
	for i in range( len( data ) ):
		# 初始中心点
		centroid = data[ i ];

		# 访问次数统计数组: [ 0, 1, 2, ... , len( data ) ]
		frequency = np.zeros( len( data ) );

		while True:
			temp = [];

			# 遍历距离当前中心点半径 radius 内的数据暂存入 temp
			for j in range( len( data ) ):
				item = data[ j ];

				diff = item - centroid;

				if np.linalg.norm( diff ) <= radius:
					temp.append( item );
					frequency[ i ] += 1;

			# 计算新中心点并记录新旧中心点
			oldcentroid = centroid;
			newcentroid = np.average( temp, axis = 0 );
			centroid = newcentroid;

			# 若新旧中心点不存在变化则终止某中心点的循环
			if np.array_equal( newcentroid, oldcentroid ):
				break;

		hassamecluster = False;

		# 判断是否需要过滤重复中心点
		for cluster in clusters:
			diff = cluster[ "centroid" ] - centroid;
			if np.linalg.norm( diff ) <= radius:
				hassamecluster = True;
				cluster[ "frequency" ] += frequency;
				break;

		if not hassamecluster:
			clusters.append( { "centroid": centroid,
							   "frequency": frequency } );


	clustering( data, clusters );

	# clusters.item.shape:
	# { "centroid": [ x, x ],
	#	"frequency": [ 0, 1, ... , len( data ) ],
	#	"data": [ array( [ x, x ] ), ... ] }

	show( clusters, radius );

# 通过访问频率聚类
def clustering( data, clusters ):
	frequency = [];

	for cluster in clusters:
		cluster[ "data" ] = [];
		frequency.append( cluster[ "frequency" ] );

	# 访问频率数组
	frequency = np.array( frequency );

	for i in range( len( data ) ):
		column = frequency[ :, i ];

		index = np.where(
			column == np.max( column ) )[ 0 ][ 0 ];

		clusters[ index ][ "data" ].append( data[ i ] );

def show ( clusters, radius ):
	colours = [ "black", "blue", "green", "cyan", "red",
				"purple", "orange", "brown" ];

	for i in range( len( clusters ) ):
		cluster = clusters[ i ];
		centroid = cluster[ "centroid" ];
		data = np.array( cluster[ "data" ] );

		plt.scatter( data[ :, 0 ],
					 data[ :, 1 ],
					 color = colours[ i ],
					 s = 20 );

		plt.scatter( centroid[ 0 ],
					 centroid[ 1 ],
					 color = colours[ i ],
					 marker = "x" );

	plt.show();

# data = np.array( [
# 	[ -4, -3.5 ], [ -3.5, -5 ], [ -2.7, -4.5 ],
# 	[ -2, -4.5 ], [ -2.9, -2.9 ], [ -0.4, -4.5 ],
# 	[ -1.4, -2.5 ], [ -1.6, -2 ], [ -1.5, -1.3 ],
# 	[ -0.5, -2.1 ], [ -0.6, -1 ], [ 0, -1.6 ],
# 	[ -2.8, -1 ], [ -2.4, -0.6 ], [ -3.5, 0 ],
# 	[ -0.2, 4 ], [ 0.9, 1.8 ], [ 1, 2.2 ],
# 	[ 1.1, 2.8 ], [ 1.1, 3.4 ], [ 1, 4.5 ],
# 	[ 1.8, 0.3 ], [ 2.2, 1.3 ], [ 2.9, 0 ],
# 	[ 2.7, 1.2 ], [ 3, 3 ], [ 3.4, 2.8 ],
# 	[ 3, 5 ], [ 5.4, 1.2 ], [ 6.3, 2 ]
# ] );

# 表格
dataframe = pd.read_csv( "./data1.ml3.csv", header = 0 );

# 数据
data = np.array( dataframe );

radius = 4;

meanshift( data, radius );
