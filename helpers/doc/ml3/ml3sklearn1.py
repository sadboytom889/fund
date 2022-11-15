import numpy as np;
import pandas as pd;

from matplotlib import pyplot as plt;
from sklearn.cluster import KMeans;
from sklearn.cluster import MeanShift, estimate_bandwidth;
from sklearn.metrics import accuracy_score;
from sklearn.neighbors import KNeighborsClassifier;

# 表格
dataframe = pd.read_csv( "./data2.ml3.csv", header = 0 );
#              V1         V2  labels
# 0      2.072345  -3.241693       0
# 1     17.936710  15.784810       0
# 2      1.083576   7.319176       0
# 3     11.120670  14.406780       0
# 4     23.711550   2.557729       0
# ...         ...        ...     ...
# 2995  85.652800  -6.461061       1
# 2996  82.770880  -2.373299       1
# 2997  64.465320 -10.501360       1
# 2998  90.722820 -12.255840       1
# 2999  64.879760 -24.877310       1
# [3000 rows x 3 columns]

xdataframe = dataframe.drop( [ "labels" ], axis = 1 );
#              V1         V2
# 0      2.072345  -3.241693
# 1     17.936710  15.784810
# 2      1.083576   7.319176
# 3     11.120670  14.406780
# 4     23.711550   2.557729
# ...         ...        ...
# 2995  85.652800  -6.461061
# 2996  82.770880  -2.373299
# 2997  64.465320 -10.501360
# 2998  90.722820 -12.255840
# 2999  64.879760 -24.877310

# 数据
ydataframe = dataframe.loc[ :, "labels" ];
# 0       0
# 1       0
# 2       0
# 3       0
# 4       0
#        ..
# 2995    1
# 2996    1
# 2997    1
# 2998    1
# 2999    1
# Name: labels, Length: 3000, dtype: int64

# 提前获取数据类别
pd.value_counts( ydataframe );
# 2    1156
# 1     954
# 0     890
# Name: labels, dtype: int64

#======================== KMeans ============================

# 创建 KMeans 模型
model = KMeans( n_clusters = 3, random_state = 0 );

# 训练 KMeans 模型
model.fit( xdataframe );

# 获取簇中心点
centers = model.cluster_centers_;
# [ [ 69.92418447 -10.11964119 ]
#   [ 40.68362784  59.71589274 ]
#   [  9.4780459   10.686052   ] ]

# 获取预测值
yhat = model.predict( xdataframe );
# [2 2 2 ... 0 0 0]

# 获取预测类别
pd.value_counts( yhat );
# 1    1149
# 0     952
# 2     899
# dtype: int64

# 重新整理分类
ycorrected = [];

for i in yhat:
	if i == 0:
		ycorrected.append( 1 );

	if i == 1:
		ycorrected.append( 2 );

	if i == 2:
		ycorrected.append( 0 );

ycorrected = np.array( ycorrected );

# 获取整理后的预测类别
pd.value_counts( ycorrected );
# 2    1149
# 1     952
# 0     899
# dtype: int64

# 获取准确率
accuracy = accuracy_score( ydataframe, ycorrected );
# 0.997

# 绘制
plt.subplot( 131 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 0 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 1 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 2 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 2 ],
					  s = 2 );

plt.title( "y" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.subplot( 132 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 0 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 1 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 2 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 2 ],
					  s = 2 );

plt.scatter( centers[ :, 0 ],
			 centers[ :, 1 ],
			 marker = "x",
			 s = 50 );

plt.title( "KMeans - yhat" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.subplot( 133 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 0 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 1 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 2 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 2 ],
					  s = 2 );

plt.scatter( centers[ :, 0 ],
			 centers[ :, 1 ],
			 marker = "x",
			 s = 50 );

plt.title( "KMeans - ycorrected" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.show();

#======================== KNN ============================

# 创建 KNN 模型
model2 = KNeighborsClassifier( n_neighbors = 3 );

# 训练 KNN 模型
model2.fit( xdataframe, ydataframe );

# 获取预测值
yhat = model2.predict( xdataframe );

# 获取准确率
accuracy = accuracy_score( ydataframe, yhat );
# 1.0

# 获取预测类别
pd.value_counts( yhat );
# 2    1156
# 1     954
# 0     890
# dtype: int64

# 绘制
plt.subplot( 121 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 0 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 1 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 2 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 2 ],
					  s = 2 );

plt.title( "y" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.subplot( 122 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 0 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 1 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 2 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 2 ],
					  s = 2 );

plt.title( "KNN - yhat" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.show();

#======================== MEANSHIFT ============================

# 估计半径
bw = estimate_bandwidth( xdataframe )
# 29.8

# 创建 MEANSHIFT 模型
model3 = MeanShift( bandwidth = bw );

# 训练 MEANSHIFT 模型
model3.fit( xdataframe, ydataframe );

# 获取簇中心点
centers = model.cluster_centers_;
# [ [ 69.92418447 -10.11964119 ]
#   [ 40.68362784  59.71589274 ]
#   [  9.4780459   10.686052   ]]

# 获取预测值
yhat = model3.predict( xdataframe );

# 获取预测类别
pd.value_counts( yhat );
# 0    1149
# 1     952
# 2     899
# dtype: int64

# 重新整理分类
ycorrected = [];

for i in yhat:
	if i == 0:
		ycorrected.append( 2 );

	if i == 1:
		ycorrected.append( 1 );

	if i == 2:
		ycorrected.append( 0 );

ycorrected = np.array( ycorrected );

# 获取准确率
accuracy = accuracy_score( ydataframe, ycorrected );
# 0.997

# 绘制
plt.subplot( 131 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 0 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 1 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ ydataframe == 2 ],
					  xdataframe.loc[ :, "V2" ][ ydataframe == 2 ],
					  s = 2 );

plt.title( "y" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.subplot( 132 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 0 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 1 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ yhat == 2 ],
					  xdataframe.loc[ :, "V2" ][ yhat == 2 ],
					  s = 2 );

plt.scatter( centers[ :, 0 ],
			 centers[ :, 1 ],
			 marker = "x",
			 s = 50 );

plt.title( "MEANSHIFT - yhat" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.subplot( 133 );

label0 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 0 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 0 ],
					  s = 2 );

label1 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 1 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 1 ],
					  s = 2 );

label2 = plt.scatter( xdataframe.loc[ :, "V1" ][ ycorrected == 2 ],
					  xdataframe.loc[ :, "V2" ][ ycorrected == 2 ],
					  s = 2 );

plt.scatter( centers[ :, 0 ],
			 centers[ :, 1 ],
			 marker = "x",
			 s = 50 );

plt.title( "MEANSHIFT - ycorrected" );

plt.xlabel( "V1" );

plt.ylabel( "V2" );

plt.legend( ( label0, label1, label2 ),
			( "label0", "label1", "label2" ) );

plt.show();