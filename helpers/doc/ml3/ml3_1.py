import numpy as np;
import pandas as pd;

from matplotlib import pyplot as plt;

# np.ndarray.ndim:
# 返回数据的维度, ndim = len( shape )
#
# np.ndarray.tile( A, reps ):
# 通过规则重复构造出新数组
# np.tile( np.array( [ 0, 1, 2 ] ), 2 );
# >>> np.array( [ 0, 1, 2, 0, 1, 2 ] );

# np.tile( np.array( [ 0, 1, 2 ] ), ( 2, 2 ) )
# >>> np.array( [ [ 0, 1, 2, 0, 1, 2 ],
#				  [ 0, 1, 2, 0, 1, 2 ] ] );

# np.tile( np.array( [ 0, 1, 2 ] ), ( 3, 2 ) )
# >>> np.array( [ [ 0, 1, 2, 0, 1, 2 ],
#				  [ 0, 1, 2, 0, 1, 2 ],
#				  [ 0, 1, 2, 0, 1, 2 ] ] );

# 表格
dataframe = pd.read_csv( "./data1.ml3.csv", header = 0 );

# 数据
data = np.array( dataframe );

# 初始簇点
centers = data[ : 3 ];

# 颜色列表
colour = [ "red", "blue", "green" ];

# 将数据通过距离平方和分类
def classify ( data, centers ):

	# 所有数据到对应簇点距离之和
	distance = 0;

	# 通过簇点数量创建列表
	classes = [ [] for i in range( centers.shape[ 0 ] ) ];

	for i in range( data.shape[ 0 ] ):

		# 通过簇点数量复制数据点行数以便相减计算差距
		diff = np.tile( data[ i ], ( centers.shape[ 0 ], 1 ) ) - centers;

		# 差距平方
		sqdiff = diff ** 2;

		# 差距平方求和
		sqdiffsum = sqdiff.sum( axis = 1 );

		# 索引排序
		sortindex = sqdiffsum.argsort();

		# 将数据放入对应的簇类, 通过距离最小的方式区别
		classes[ sortindex[ 0 ] ].append( list( data[ i ] ) );

		# 累加最短距离
		distance = distance + sqdiffsum[ sortindex[ 0 ] ];

	# 返回格式: [ 簇类 -> 数据 ];
	return classes, distance;

# 更新簇点
def updatecenters ( classes ):

	# 新簇列表
	centers = [];

	for i in range( len( classes ) ):

		# 当前簇的数据数组
		classitem = np.array( classes[ i ] );

		# 求均值作为新坐标
		center = classitem.sum( axis = 0 ) / len( classes[ i ] )

		# 添加新簇到新簇列表
		centers.append( center );

	return np.array( centers );

# 1: 通过欧式最短距离分类数据
# 2: 通过距离均值更新中心点
# 3: 循环 1 - 2
def kmeans ( data, centers, distance ):

	# 1
	classes, newdistance = classify( data, centers );

	# 绘制
	for i in range( len( centers ) ):

		plt.scatter( centers[ i ][ 0 ], centers[ i ][ 1 ], c = colour[ i ], marker = "x" );

	for i in range( len( classes ) ):

		for dataitem in classes[ i ]:

			plt.scatter( dataitem[ 0 ], dataitem[ 1 ], c = colour[ i ], s = 2 );

	plt.title( "distance: {}".format( distance ) );

	plt.show();

	# 终止条件
	if newdistance == distance:
		return;

	# 2
	centers = updatecenters( classes );

	kmeans( data, centers, newdistance );

kmeans( data, centers, 0 );












